import ast
from pathlib import Path

ROOT = Path(r"c:\Prcatices-AI\qa_automation\tests\QALS11")


def try_parse(text: str, file_path: Path):
    try:
        ast.parse(text, filename=str(file_path))
        return None
    except (IndentationError, SyntaxError) as exc:
        return exc


def fix_file(path: Path) -> tuple[int, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    changed = 0
    max_iters = 8000

    for _ in range(max_iters):
        current = "".join(lines)
        err = try_parse(current, path)
        if err is None:
            if changed:
                path.write_text(current, encoding="utf-8")
            return changed, "ok"

        msg = getattr(err, "msg", str(err))
        lineno = getattr(err, "lineno", None)
        if not lineno or lineno < 1 or lineno > len(lines):
            return changed, f"stopped: {msg}"

        idx = lineno - 1
        raw = lines[idx]
        stripped = raw.lstrip(" \t")

        # Keep blank/comment lines untouched; move to next real line when possible.
        if not stripped.strip() or stripped.startswith("#"):
            next_idx = idx + 1
            while next_idx < len(lines):
                nxt = lines[next_idx]
                nxt_stripped = nxt.lstrip(" \t")
                if nxt_stripped.strip() and not nxt_stripped.startswith("#"):
                    lines[next_idx] = "    " + nxt
                    changed += 1
                    break
                next_idx += 1
            else:
                return changed, f"stopped: {msg}"
            continue

        # Primary fix for missing block indentation.
        if "expected an indented block" in msg or "expected an indented block after" in msg:
            lines[idx] = "    " + raw
            changed += 1
            continue

        # Too much indentation at current position.
        if "unexpected indent" in msg:
            if raw.startswith("    "):
                lines[idx] = raw[4:]
                changed += 1
                continue
            return changed, f"stopped: {msg}"

        # Loop controls often need one extra nesting level after prior repairs.
        if "outside loop" in msg and (stripped.startswith("break") or stripped.startswith("continue")):
            lines[idx] = "    " + raw
            changed += 1
            continue

        # Secondary syntax fallout after try/for/if blocks; indent current line once.
        if "expected 'except' or 'finally' block" in msg:
            lines[idx] = "    " + raw
            changed += 1
            continue

        # Generic syntax fallback: try gentle unindent first, then indent.
        if "invalid syntax" in msg:
            if raw.startswith("    "):
                lines[idx] = raw[4:]
            else:
                lines[idx] = "    " + raw
            changed += 1
            continue

        return changed, f"stopped: {msg}"

    return changed, "stopped: max_iters"


def main():
    targets = sorted(ROOT.rglob("test_*.py"))
    total_changed = 0
    unresolved = []

    for path in targets:
        changed, status = fix_file(path)
        total_changed += changed
        if changed:
            print(f"[fixed] {path} (+{changed})")
        if status != "ok":
            unresolved.append((path, status))

    print(f"\nTotal indentation edits: {total_changed}")
    if unresolved:
        print("Unresolved files:")
        for path, status in unresolved:
            print(f" - {path}: {status}")


if __name__ == "__main__":
    main()
