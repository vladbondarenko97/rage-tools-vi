#!/usr/bin/env python3
"""Isolated-bus check: non-terminal replies do not close a request."""
import os
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
BUS = [sys.executable, str(REPO / "tools" / "bus.py")]


def main():
    with tempfile.TemporaryDirectory(prefix="bus-digest-") as tmp:
        env = dict(os.environ, RAGE_BUS_DIR=tmp)

        def run(*args, body=None):
            return subprocess.run(
                BUS + list(args),
                env=env,
                input=body,
                text=True,
                capture_output=True,
                check=True,
            ).stdout

        def send(sender, recipient, kind, body, reply_to=None):
            args = ["send", "--from", sender, "--to", recipient, "--kind", kind]
            if reply_to is not None:
                args += ["--reply-to", str(reply_to)]
            args += ["--body", "-"]
            out = run(*args, body=body)
            return int(re.search(r"#(\d+)", out).group(1))

        r1 = send("operator", "script", "request", "R1")
        note = send("script", "operator", "note", "working: started", r1)
        out = run("digest", "--as", "script", "--all", "--since", "0", "--no-mark")
        open_part = out.split("NEW", 1)[0]
        assert f"#{r1:04d}" in open_part, out
        assert f"#{note:04d}" in out, out

        answer = send("script", "operator", "answer", "R1 done", r1)
        out = run("digest", "--as", "script", "--all", "--since", "0", "--no-mark")
        open_part = out.split("NEW", 1)[0]
        assert f"#{r1:04d}" not in open_part, out
        assert f"#{answer:04d}" in out, out

        r2 = send("operator", "script", "request", "R2")
        no_ack = send("script", "operator", "note", "NO_ACK R2", r2)
        out = run("digest", "--as", "script", "--all", "--since", "0", "--no-mark")
        open_part = out.split("NEW", 1)[0]
        assert f"#{r2:04d}" in open_part, out
        assert f"#{no_ack:04d}" in out, out

        print("ok: note/working/NO_ACK leave requests open; answer closes them")


if __name__ == "__main__":
    main()
