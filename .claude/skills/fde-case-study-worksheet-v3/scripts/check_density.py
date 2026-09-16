#!/usr/bin/env python3
"""Compare a generated v3 pair against the canonical Phase-01 reference pair.

Structure (section names, counts) AND prose density are both checked. Density is the
one that matters: a draft can match the reference's line count exactly while running
1.5x too wordy per bullet, which is the failure this script exists to catch.

Usage:
  python3 check_density.py <ref_worksheet> <ref_key> <new_worksheet> <new_key>
"""
import re
import sys

MAX_DRIFT = 1.25  # a section over this is too wordy and must be tightened


def sections(path):
    """-> {section_name: {"bullets": [wordcount, ...], "rows": n}} keyed in file order."""
    out, cur, fenced = {}, None, False
    for line in open(path, encoding="utf-8"):
        # A fenced block (the one allowed mermaid diagram) is content, not bullets.
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = {"bullets": [], "rows": 0}
        elif cur is None:
            continue
        elif line.startswith("|"):
            if not re.match(r"^\|[\s:|-]+\|?\s*$", line):
                out[cur]["rows"] += 1
        elif line.strip() and not line.startswith("#"):
            out[cur]["bullets"].append(len(line.split()))
    return out


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def compare(ref_path, new_path, label):
    ref, new = sections(ref_path), sections(new_path)
    print(f"\n=== {label} ===")
    problems = []

    missing = [k for k in ref if k not in new]
    extra = [k for k in new if k not in ref]
    if missing:
        problems.append(f"missing sections: {missing}")
    if extra:
        problems.append(f"unexpected sections: {extra}")

    for name, rdata in ref.items():
        ndata = new.get(name)
        if not ndata:
            continue
        rb, nb = len(rdata["bullets"]), len(ndata["bullets"])
        rr, nr = rdata["rows"], ndata["rows"]
        rm, nm = mean(rdata["bullets"]), mean(ndata["bullets"])
        drift = (nm / rm) if rm else 0.0
        # Bullet counts are contractual: the reference's shape is the format.
        # Table ROW counts are content-driven (a chapter may genuinely have 4 personas
        # or 6 data sources where the reference has 3) -> warn, never fail.
        fatal, warn = [], []
        if rb != nb:
            fatal.append(f"bullets {rb}->{nb}")
        if drift > MAX_DRIFT:
            fatal.append(f"TOO WORDY {drift:.2f}x")
        if rr != nr:
            warn.append(f"rows {rr}->{nr} (content-driven, check it is intentional)")
        status = ("  <-- " + ", ".join(fatal + warn)) if (fatal or warn) else ""
        print(f"  {name[:38]:40} {rm:6.1f} -> {nm:6.1f} w/bullet  {drift:4.2f}x{status}")
        if fatal:
            problems.append(f"{name}: {', '.join(fatal)}")

    rbytes, nbytes = len(open(ref_path, "rb").read()), len(open(new_path, "rb").read())
    ratio = nbytes / rbytes
    print(f"  {'TOTAL BYTES':40} {rbytes:6d} -> {nbytes:6d}          {ratio:4.2f}x")
    if ratio > MAX_DRIFT:
        problems.append(f"file is {ratio:.2f}x the reference size")
    return problems


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    ref_w, ref_k, new_w, new_k = sys.argv[1:5]
    problems = compare(ref_w, new_w, "WORKSHEET") + compare(ref_k, new_k, "ANSWER KEY")
    print()
    if problems:
        print(f"FAIL — {len(problems)} issue(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("PASS — structure and density both match the reference.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
