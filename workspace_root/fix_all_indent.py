"""
Fix Python indentation errors in QALS11 Actions test files.
The common issue: compound statement bodies (try, except, for, if, else, etc.)
are not properly indented (body is at same level as the header).
"""
import re
from pathlib import Path

TARGET_DIR = Path(r"c:\Prcatices-AI\qa_automation\tests\QALS11\Actions")

COMPOUND_HEADERS = re.compile(
    r"^\s*(for\s|if\s|elif\s|else:|while\s|with\s|try:|except(\s|:)|finally:|def\s|class\s|async\s)"
)


def bracket_net(line: str) -> int:
    """Net change in open-bracket depth from a line (ignores strings naively)."""
    depth = 0
    i = 0
    while i < len(line):
        ch = line[i]
        # Skip string literals (basic handling)
        if ch in ('"', "'"):
            quote = ch
            # Check for triple quotes
            if line[i:i+3] in ('"""', "'''"):
                quote = line[i:i+3]
                i += 3
                while i < len(line) - len(quote) + 1:
                    if line[i:i+len(quote)] == quote:
                        i += len(quote)
                        break
                    i += 1
                continue
            else:
                i += 1
                while i < len(line):
                    if line[i] == '\\':
                        i += 2
                        continue
                    if line[i] == quote:
                        i += 1
                        break
                    i += 1
                continue
        elif ch == '#':
            break  # Rest is comment
        elif ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth -= 1
        i += 1
    return depth


def get_statement_start_indent(line: str):
    """Return indentation of a non-blank line, or None if blank."""
    stripped = line.rstrip('\n\r')
    lstripped = stripped.lstrip()
    if not lstripped:
        return None
    return len(stripped) - len(lstripped)


def is_compound_header(stripped: str) -> bool:
    """True if stripped line is a compound statement header (ends with :)."""
    if not stripped.endswith(':'):
        return False
    if stripped.startswith('#'):
        return False
    return bool(COMPOUND_HEADERS.match('    ' + stripped))


def fix_one_pass(lines: list) -> tuple:
    """
    One pass: find compound headers where body is at same indent, add 4 spaces.
    Returns (new_lines, changed_bool).
    """
    changed = False
    i = 0
    bracket_depth = 0

    while i < len(lines):
        line = lines[i]
        raw_stripped = line.rstrip('\n\r')
        lstripped = raw_stripped.lstrip()

        if not lstripped:
            i += 1
            continue

        indent = len(raw_stripped) - len(lstripped)

        # Track whether this line is inside a multi-line expression
        if bracket_depth > 0:
            bracket_depth += bracket_net(line)
            if bracket_depth < 0:
                bracket_depth = 0
            i += 1
            continue

        # This is a statement-level line
        net = bracket_net(line)
        bracket_depth += net
        if bracket_depth < 0:
            bracket_depth = 0

        if not is_compound_header(lstripped):
            i += 1
            continue

        # It's a compound header at indent N.
        # If bracket_depth > 0 now, skip continuation lines first.
        j = i + 1
        temp_depth = bracket_depth
        while j < len(lines) and temp_depth > 0:
            temp_depth += bracket_net(lines[j])
            if temp_depth < 0:
                temp_depth = 0
            j += 1

        # Now find next non-blank statement line
        while j < len(lines) and not lines[j].rstrip('\n\r').strip():
            j += 1

        if j >= len(lines):
            i += 1
            continue

        next_indent = get_statement_start_indent(lines[j])
        if next_indent is None or next_indent > indent:
            # Body already has correct indentation or is empty
            i += 1
            continue

        # Body is at same or lower indent as header → fix it
        # Add 4 spaces to all lines in the body block.
        # Body ends when we hit a "real" statement at indent < header_indent
        # (that's not else/elif/except/finally at the same level).
        k = j
        inner_depth = 0
        while k < len(lines):
            kline = lines[k]
            kraw = kline.rstrip('\n\r')
            kstripped = kraw.lstrip()

            if not kstripped:
                k += 1
                continue

            kindent = len(kraw) - len(kstripped)

            if inner_depth > 0:
                # Continuation — add 4 spaces
                lines[k] = '    ' + kline
                changed = True
                inner_depth += bracket_net(kline)
                if inner_depth < 0:
                    inner_depth = 0
                k += 1
                continue

            # Statement line
            if kindent < indent:
                # Left the block
                break

            # Add 4 spaces
            lines[k] = '    ' + kline
            changed = True
            inner_depth += bracket_net(lines[k])
            if inner_depth < 0:
                inner_depth = 0
            k += 1

        i += 1

    return lines, changed


def fix_file(filepath: Path) -> bool:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    # Ensure all lines end with newline
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'

    original = list(lines)

    for pass_num in range(20):  # max 20 passes for deep nesting
        lines, changed = fix_one_pass(lines)
        if not changed:
            print(f"  {filepath.name}: converged after {pass_num} pass(es)")
            break
    else:
        print(f"  {filepath.name}: WARNING - did not converge in 20 passes")

    if lines != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False


def main():
    files_with_errors = [
        "test_calloff.py",
        "test_add_notes.py",
        "test_adhoc_receipts.py",
        "test_adjust_inventory.py",
        "test_approve_reject_cards.py",
        "test_issue_inventory.py",
        "test_move_location.py",
        "test_receive.py",
        "test_release.py",
        "test_reschedule.py",
        "test_runline_approve.py",
        "test_set_po.py",
    ]

    print("Fixing indentation in QALS11 Actions test files...\n")
    for fname in files_with_errors:
        fpath = TARGET_DIR / fname
        if not fpath.exists():
            print(f"  {fname}: NOT FOUND, skipping")
            continue
        fixed = fix_file(fpath)
        status = "FIXED" if fixed else "no changes needed"
        print(f"  {fname}: {status}")

    print("\nDone.")


if __name__ == "__main__":
    main()
