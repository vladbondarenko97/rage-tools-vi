"""Smoke tests for the naming and PSIN tools.

Plain assertions, no framework: the point is that a fresh clone can run one
command and know whether the registry, the annotator and the schema readers
still work against the committed data.

    python3 tests/test_analysis_tools.py
"""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILED = []


def check(name, condition, detail=""):
    if condition:
        print(f"  ok    {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILED.append(name)


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT,
                          capture_output=True, text=True)


def main():
    print("registry")
    result = run("tools/name_registry.py", "--lookup", "0x01166164", "0xdeadbeef")
    check("lookup resolves a known hash", "Position" in result.stdout)
    check("lookup reports an unknown hash", "<unresolved>" in result.stdout)
    check("lookup exits non-zero when a hash is unresolved", result.returncode == 1)

    names = list(csv.DictReader((ROOT / "handoff/names.tsv").open(), delimiter="\t"))
    check("registry has at least 30k names", len(names) > 30000, f"({len(names)})")
    required = {"hash", "name", "kind", "confidence", "source",
                "also_known_as", "ambiguous"}
    check("registry columns", required <= set(names[0]), set(names[0]))
    check("a collision is marked ambiguous",
          any(row["ambiguous"] == "1" for row in names))

    print("annotation")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "named.tsv"
        result = run("tools/name_registry.py", "--annotate",
                     "handoff/script-bones.tsv", "--column", "bone_hash",
                     "--out", str(out))
        check("annotate succeeds", result.returncode == 0, result.stderr[:120])
        rows = list(csv.DictReader(out.open(), delimiter="\t"))
        check("annotate adds name columns", "name_confidence" in rows[0])
        check("annotate names some rows", any(row["name"] for row in rows))

    print("PSIN")
    result = run("tools/psin_dump.py", "--property", "position")
    check("property search finds records", "records mention" in result.stdout)
    result = run("tools/psin_segment.py", "--describe", "1054")
    check("describe prints entries", "Id=" in result.stdout)
    check("describe pairs Id and Type",
          any("Type=" in line and "Id=" in line for line in result.stdout.splitlines()))

    result = run("tools/psin_entries.py", "--out", "cache/psin-entries-test.tsv")
    check("entries extraction runs", result.returncode == 0, result.stderr[:120])
    entries = list(csv.DictReader((ROOT / "cache/psin-entries-test.tsv").open(),
                                  delimiter="\t"))
    check("entries found", len(entries) > 1000, f"({len(entries)})")
    check("entries carry Id/Type pairs",
          any(row["field_a"] in ("Id", "Type") for row in entries))

    if (ROOT / "script.rpf").is_file():
        print("extraction from the archive")
        result = run("tools/psin_extract.py", "script.rpf",
                     "--out", "cache/psin-properties-test.tsv")
        check("extract runs", result.returncode == 0, result.stderr[:120])
        rows = list(csv.DictReader((ROOT / "cache/psin-properties-test.tsv").open(),
                                   delimiter="\t"))
        check("extract finds the same 62,910 rows", len(rows) == 62910, f"({len(rows)})")
        check("extract column layout", "class_hash" in rows[0], set(rows[0]))
    else:
        print("extraction from the archive: skipped (script.rpf not present)")

    print()
    if FAILED:
        print(f"FAIL: {len(FAILED)} check(s) failed: {', '.join(FAILED)}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
