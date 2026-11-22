#!/usr/bin/env python3
"""Visible file bus for the script-graph and data-rpf workstreams."""

import argparse
import ctypes
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import select as select_module
import struct
import sys
import time

BUS_DIR = Path(os.environ.get("RAGE_BUS_DIR", Path.home() / "code" / "rage-tools-vi-bus"))
MESSAGES = BUS_DIR / "messages.jsonl"
TERMINAL_REPLY_KINDS = {"answer", "handoff", "result"}


def timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_messages():
    if not MESSAGES.is_file():
        return []
    messages = []
    for line in MESSAGES.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return messages


def append_message(message):
    BUS_DIR.mkdir(parents=True, exist_ok=True)
    with MESSAGES.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        ids = []
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                ids.append(int(json.loads(line)["id"]))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        message["id"] = max(ids, default=0) + 1
        message["ts"] = timestamp()
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(message, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        fcntl.flock(handle, fcntl.LOCK_UN)
    return message


def indent(body):
    return "\n".join("  " + line for line in body.splitlines())


def format_message(message):
    reply = f" re:#{message['reply_to']:04d}" if message.get("reply_to") else ""
    return (
        f"#{message['id']:04d} {message['ts']} "
        f"{message['from']} -> {message['to']} [{message['kind']}]{reply}\n"
        f"{indent(message['body'])}"
    )


def seen_path(name):
    return BUS_DIR / f".seen-{name}"


def mark_seen(name, message_id):
    BUS_DIR.mkdir(parents=True, exist_ok=True)
    seen_path(name).write_text(str(message_id))


def last_seen(name):
    path = seen_path(name)
    if not path.is_file():
        return 0
    try:
        return int(path.read_text().strip())
    except ValueError:
        return 0


def select(messages, name, since, show_all=False):
    selected = []
    for message in messages:
        if message.get("id", 0) <= since:
            continue
        if show_all or name in (None, "observer", "operator"):
            selected.append(message)
        elif message.get("to") in (name, "all", "*"):
            selected.append(message)
    return selected


def command_send(args):
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    elif args.body == "-":
        body = sys.stdin.read()
    else:
        body = args.body
    if not body.strip():
        raise SystemExit("empty message body")
    message = append_message(
        {
            "from": args.sender,
            "to": args.to,
            "kind": args.kind,
            "body": body.rstrip(),
            "reply_to": args.reply_to,
        }
    )
    print(format_message(message))


def command_read(args):
    since = args.since if args.since is not None else last_seen(args.as_name)
    selected = select(load_messages(), args.as_name, since, args.all)
    if not selected:
        print("no new messages")
        return
    for message in selected:
        print(format_message(message))
        print()
    if not args.no_mark:
        mark_seen(args.as_name, max(message["id"] for message in selected))


class InotifyWatcher:
    """Watch the bus directory for messages.jsonl append/create/replace events."""

    IN_MODIFY = 0x00000002
    IN_CLOSE_WRITE = 0x00000008
    IN_MOVED_TO = 0x00000080
    IN_CREATE = 0x00000100
    IN_Q_OVERFLOW = 0x00004000
    IN_ISDIR = 0x40000000
    MASK = IN_MODIFY | IN_CLOSE_WRITE | IN_MOVED_TO | IN_CREATE

    def __init__(self, directory):
        self.libc = ctypes.CDLL(None, use_errno=True)
        self.libc.inotify_init1.argtypes = [ctypes.c_int]
        self.libc.inotify_init1.restype = ctypes.c_int
        self.libc.inotify_add_watch.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint32,
        ]
        self.libc.inotify_add_watch.restype = ctypes.c_int
        flags = getattr(os, "O_CLOEXEC", 0) | os.O_NONBLOCK
        self.fd = self.libc.inotify_init1(flags)
        if self.fd < 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
        self.wd = self.libc.inotify_add_watch(
            self.fd, os.fsencode(str(directory)), self.MASK
        )
        if self.wd < 0:
            error = ctypes.get_errno()
            self.close()
            raise OSError(error, os.strerror(error))

    def wait(self, timeout):
        ready, _, _ = select_module.select([self.fd], [], [], timeout)
        if not ready:
            return None
        try:
            data = os.read(self.fd, 65536)
        except BlockingIOError:
            return None
        reason = None
        offset = 0
        while offset + 16 <= len(data):
            _, mask, _, length = struct.unpack_from("iIII", data, offset)
            name = data[offset + 16 : offset + 16 + length].split(b"\0", 1)[0]
            if mask & self.IN_Q_OVERFLOW:
                reason = "overflow"
            elif name == b"messages.jsonl" and not (mask & self.IN_ISDIR):
                if reason != "overflow":
                    reason = "message"
            offset += 16 + length
        return reason

    def close(self):
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


def command_wait(args):
    BUS_DIR.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + args.timeout if args.timeout is not None else None
    since = args.since if args.since is not None else last_seen(args.as_name)
    next_heartbeat = time.monotonic() + args.heartbeat
    try:
        watcher = InotifyWatcher(BUS_DIR)
    except (OSError, AttributeError) as error:
        raise SystemExit(f"inotify is required for bus wait: {error}")
    try:
        selected = select(load_messages(), args.as_name, since, args.all)
        if selected:
            for message in selected:
                print(format_message(message))
                print()
            if not args.no_mark:
                mark_seen(args.as_name, max(message["id"] for message in selected))
            return
        while True:
            now = time.monotonic()
            remaining = deadline - now if deadline is not None else None
            if remaining is not None and remaining <= 0:
                print(f"timeout after {args.timeout}s; last id {since}", flush=True)
                raise SystemExit(2)
            wait_for = remaining
            if args.heartbeat > 0:
                heartbeat_in = max(0, next_heartbeat - now)
                wait_for = heartbeat_in if remaining is None else min(remaining, heartbeat_in)
            reason = watcher.wait(wait_for)
            if reason in ("message", "overflow"):
                selected = select(load_messages(), args.as_name, since, args.all)
                if selected:
                    for message in selected:
                        print(format_message(message))
                        print()
                    if not args.no_mark:
                        mark_seen(args.as_name, max(message["id"] for message in selected))
                    return
                continue
            if args.heartbeat > 0 and time.monotonic() >= next_heartbeat:
                print(f"[wait] {args.as_name} waiting since #{since} ...", flush=True)
                next_heartbeat += args.heartbeat
    finally:
        watcher.close()


def command_digest(args):
    messages = load_messages()
    since = args.since if args.since is not None else last_seen(args.as_name)
    answered = {
        message.get("reply_to")
        for message in messages
        if message.get("reply_to") and message.get("kind") in TERMINAL_REPLY_KINDS
    }
    addressed = [
        message
        for message in messages
        if args.all or message.get("to") in (args.as_name, "all", "*")
    ]
    open_requests = [
        message
        for message in addressed
        if message.get("kind") in ("request", "question") and message["id"] not in answered
    ]
    open_ids = {message["id"] for message in open_requests}
    fresh = [
        message
        for message in addressed
        if message["id"] > since and message["id"] not in open_ids
    ]
    selected = {message["id"]: message for message in open_requests + fresh}
    if not selected:
        print("no open requests or new messages")
        return

    def brief(message):
        body = " ".join(message["body"].split())
        if len(body) > args.max_chars:
            body = body[: args.max_chars] + "..."
        return (
            f"#{message['id']:04d} {message['from']}->{message['to']} "
            f"[{message['kind']}] {body}"
        )

    if open_requests:
        print("OPEN REQUESTS")
        for message in open_requests:
            print(brief(message))
        print()
    if fresh:
        print("NEW")
        for message in sorted(fresh, key=lambda item: item["id"]):
            print(brief(message))
    if not args.no_mark:
        mark_seen(args.as_name, max(selected))


def command_log(args):
    messages = load_messages()
    if not messages:
        print("bus is empty")
        return
    for message in messages:
        print(format_message(message))
        print()


def command_tail(args):
    BUS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"tailing {MESSAGES} as {args.as_name} (Ctrl-C to stop)")
    since = args.since if args.since is not None else last_seen(args.as_name)
    try:
        watcher = InotifyWatcher(BUS_DIR)
    except (OSError, AttributeError) as error:
        raise SystemExit(f"inotify is required for bus tail: {error}")
    try:
        def emit():
            nonlocal since
            selected = select(load_messages(), args.as_name, since, args.all)
            for message in selected:
                print(format_message(message))
                print()
                since = max(since, message["id"])
            if selected and not args.no_mark:
                mark_seen(args.as_name, since)
        emit()
        while True:
            reason = watcher.wait(None)
            if reason in ("message", "overflow"):
                emit()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        watcher.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    send = sub.add_parser("send", help="append a message")
    send.add_argument("--from", dest="sender", required=True)
    send.add_argument("--to", required=True)
    send.add_argument("--kind", default="note", help="note, request, answer, handoff, question")
    send.add_argument("--body", default="-", help="message text, or - for stdin")
    send.add_argument("--body-file")
    send.add_argument("--reply-to", type=int)
    send.set_defaults(func=command_send)

    read = sub.add_parser("read", help="print new messages")
    read.add_argument("--as", dest="as_name", default="observer")
    read.add_argument("--since", type=int)
    read.add_argument("--all", action="store_true")
    read.add_argument("--no-mark", action="store_true")
    read.set_defaults(func=command_read)

    wait = sub.add_parser("wait", help="blocking inotify wait for a new message")
    wait.add_argument("--as", dest="as_name", default="observer")
    wait.add_argument("--since", type=int)
    wait.add_argument("--timeout", type=float, default=1.0, help="deadline in seconds (default 1.0)")
    wait.add_argument("--heartbeat", type=float, default=0.0)
    wait.add_argument("--interval", type=float, default=1.0, help="accepted for compatibility; inotify is required")
    wait.add_argument("--all", action="store_true")
    wait.add_argument("--no-mark", action="store_true")
    wait.set_defaults(func=command_wait)

    digest = sub.add_parser("digest", help="compact open requests and new messages")
    digest.add_argument("--as", dest="as_name", default="observer")
    digest.add_argument("--since", type=int)
    digest.add_argument("--all", action="store_true")
    digest.add_argument("--max-chars", type=int, default=240)
    digest.add_argument("--no-mark", action="store_true")
    digest.set_defaults(func=command_digest)

    log = sub.add_parser("log", help="print the whole bus")
    log.set_defaults(func=command_log)

    tail = sub.add_parser("tail", help="follow the bus via inotify")
    tail.add_argument("--as", dest="as_name", default="observer")
    tail.add_argument("--since", type=int)
    tail.add_argument("--all", action="store_true")
    tail.add_argument("--no-mark", action="store_true")
    tail.add_argument("--interval", type=float, default=1.0)
    tail.set_defaults(func=command_tail)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
