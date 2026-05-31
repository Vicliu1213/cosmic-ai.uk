#!/usr/bin/env python3
"""
One-click deploy: docs/task6.md → src/omega_system/omega_system.py
"""

import re

# Hardcoded _placeholder: replaces broken indentation version in task6.md
PLACEHOLDER_FUNC = '''
def _placeholder(name: str) -> object:
    """Placeholder for cross-file import fallback."""
    class _P:
        def __getattr__(self, item):
            async def _noop(*a, **kw):
                return {}
            return _noop
    return _P()
'''

DUNDER_FIXES = {
    '**future**': '__future__', '**init**': '__init__', '**name**': '__name__',
    '**main**': '__main__', '**mul**': '__mul__', '**str**': '__str__',
    '**gt**': '__gt__', '**getattr**': '__getattr__',
}
SPECIAL_FIXES = {'GENE*CATALOG': 'GENE_CATALOG'}

TOP_KWS = ('class ', 'def ', 'async def ', '@', 'from ', 'import ')


def fix_md(text: str) -> str:
    for old, new in DUNDER_FIXES.items():
        text = text.replace(old, new)
    text = text.replace('\\*', '*')
    text = text.replace('\\_', '_')
    for old, new in SPECIAL_FIXES.items():
        text = text.replace(old, new)
    return text


def remove_markdown_artifacts(lines):
    """
    Remove part headers, section descriptions, and decorative lines.
    
    Strategy: scan for section description blocks in a pre-pass to mark
    which lines to skip, then remove them in the main pass.
    This avoids issues with stray docstring markers breaking string parsing.
    """
    n = len(lines)
    skip = [False] * n

    # Pre-pass: find """...Part...""" blocks and mark them
    i = 0
    while i < n:
        s = lines[i].strip()

        # Opening """ on its own line
        if s == '"""' and i < n - 1:
            # Look ahead a few lines to see if this is a section description
            lookahead = min(i + 20, n)
            is_section_desc = False
            for j in range(i + 1, lookahead):
                if 'Ω宇宙系统 Part' in lines[j]:
                    is_section_desc = True
                    break
                if lines[j].strip() == '"""':
                    break
            if is_section_desc:
                # Mark from this """ to the closing """
                skip[i] = True
                i += 1
                while i < n and lines[i].strip() != '"""':
                    skip[i] = True
                    i += 1
                if i < n:
                    skip[i] = True  # closing """
                i += 1
                continue

        i += 1

    # Main pass: build result, skipping marked lines
    result = []
    for i in range(n):
        if skip[i]:
            continue
        s = lines[i].strip()

        # Decorative separators
        if re.match(r'^["#=Ω\s\-_*]{25,}$', s):
            continue

        result.append(lines[i])

    return result


def fix_indentation(lines):
    """Fix class body indentation (everything is at 0 indent in the source)."""
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        s = line.strip()
        indent = len(line) - len(line.lstrip())

        # @dataclass + class combination
        if s == '@dataclass' and indent == 0:
            result.append(line)
            i += 1
            if i < n:
                nxt = lines[i]
                ns = nxt.strip()
                if ns.startswith('class ') and (len(nxt) - len(nxt.lstrip())) == 0:
                    result.append(nxt)
                    i += 1
                    # Fix body
                    result, i = _indent_body(lines, i, result)
                else:
                    result.append(nxt)
                    i += 1
            continue

        # Standalone class
        if s.startswith('class ') and indent == 0:
            result.append(line)
            i += 1
            result, i = _indent_body(lines, i, result)
            continue

        # Top-level function
        if (s.startswith('def ') or s.startswith('async def ')) and indent == 0:
            result.append(line)
            i += 1
            result, i = _indent_body(lines, i, result)
            continue

        result.append(line)
        i += 1

    return result


def _indent_body(lines, start, result):
    """
    Indent class/function body lines from 0→4 spaces until next top-level.
    """
    i = start
    n = len(lines)
    while i < n:
        raw = lines[i]
        s = raw.strip()
        indent = len(raw) - len(raw.lstrip())

        if s == '':
            result.append(raw)
            i += 1
            continue

        if indent == 0:
            if s.startswith(TOP_KWS) or s == '@dataclass':
                break
            result.append('    ' + s)
            i += 1
            continue

        result.append(raw)
        i += 1

    return result, i


def fix_nested_blocks(lines):
    """
    Post-processing: fix indentation of lines inside control flow blocks
    (if/for/while/etc.) that are at the same level as the header.
    """
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if not s or not s.endswith(':'):
            i += 1
            continue
        indent = len(lines[i]) - len(lines[i].lstrip())
        block_keywords = ('if ', 'elif ', 'else:', 'for ', 'while ',
                          'try:', 'except', 'finally:', 'with ')
        is_block = any(s.startswith(kw) for kw in block_keywords)
        if not is_block:
            i += 1
            continue
        # Look ahead for first non-empty line
        j = i + 1
        while j < n and lines[j].strip() == '':
            j += 1
        if j < n:
            next_raw = lines[j]
            next_indent = len(next_raw) - len(next_raw.lstrip())
            if next_indent <= indent:
                # Add 4 to current indent (was at same level as header)
                lines[j] = ' ' * (next_indent + 4) + next_raw.strip()
                # Also fix ALL subsequent lines that have same indent
                # (they belong to the block body)
                j += 1
                while j < n:
                    nxt = lines[j]
                    nxt_indent = len(nxt) - len(nxt.lstrip())
                    if nxt.strip() == '' or nxt_indent > next_indent:
                        j += 1
                        continue
                    if nxt_indent <= indent:
                        # Same level as block header → not in block anymore
                        break
                    nxt_stripped = nxt.strip()
                    if nxt_indent == next_indent:
                        # Fix: add 4 to match the body indent
                        lines[j] = ' ' * (nxt_indent + 4) + nxt_stripped
                    j += 1
        i += 1
    return lines


def cleanup(lines):
    """Remove __name__ blocks, placeholder code, etc."""
    result = []
    skip_next = False
    for line in lines:
        s = line.strip()

        # Skip __name__ block lines
        if '__name__' in line and '"__main__"' in line:
            skip_next = True
            continue
        if skip_next and 'asyncio.run' in line:
            skip_next = False
            continue
        skip_next = False

        # Deduplicate logging.basicConfig (keep first)
        if 'logging.basicConfig' in line:
            if any('logging.basicConfig' in x for x in result):
                continue

        # Remove duplicate __future__ imports (must be at file start)
        if 'from __future__' in line:
            if any('from __future__' in x for x in result):
                continue

        result.append(line)

    return result


def main():
    with open('docs/task6.md', 'r', encoding='utf-8') as f:
        raw = f.read()

    # 1. Fix markdown syntax
    code = fix_md(raw)
    lines = code.split('\n')

    # 2. Remove markdown artifacts
    lines = remove_markdown_artifacts(lines)

    # 3. Fix indentation
    lines = fix_indentation(lines)

    # 3b. Fix nested block indentation (if/for/while bodies inside function bodies)
    lines = fix_nested_blocks(lines)

    # 4. Remove conditional import blocks and simplify coordinator
    filtered = []
    skip_paren = 0
    in_mindnode_block = False
    for line in lines:
        s = line.strip()
        
        # Remove "from omega_system_part1 import (...)" block
        if 'from omega_system_part1' in s:
            skip_paren = 1
            continue
        if skip_paren:
            skip_paren += s.count('(') - s.count(')')
            if skip_paren <= 0:
                skip_paren = 0
            continue
        
        # Keep _placeholder function and related (needed for conditional fallbacks)
        
        # Transform single-line: self.xxx = Class() if 'Class' in dir() else ...
        m = re.search(r"(self\.\w+)\s*=\s*(\w+)\s+if\s+['\"]\2['\"]\s+in\s+dir", line)
        if m:
            filtered.append(f"        {m.group(1)} = {m.group(2)}()")
            continue
        
        # Handle multi-line: node = MindNode(...) \ if 'MindNode' in dir() else type(...)
        if 'node = MindNode(entity_id' in s and line.strip().endswith('\\'):
            # This line is already correct - remove the trailing backslash
            indent = len(line) - len(line.lstrip())
            filtered.append(' ' * indent + 'node = MindNode(entity_id, entity_id, 130.0, 1.0, 100.0)')
            in_mindnode_block = True
            continue
        if in_mindnode_block:
            # Skip continuation lines until the statement ends
            if s.endswith('})()'):
                in_mindnode_block = False
            continue
        
        filtered.append(line)
    lines = filtered

    # 5. Cleanup (deduplicate, remove __name__ blocks)
    lines = cleanup(lines)

    code = '\n'.join(lines)

    # Strip broken _placeholder + _P from markdown, append correct version
    placeholder_lines = 0
    cleaned_lines = code.split('\n')
    temp = []
    skipping = False
    for ln in cleaned_lines:
        s = ln.strip()
        if s.startswith('def _placeholder'):
            skipping = True
        if skipping and s.startswith('# ── 主程序'):
            skipping = False
        if not skipping:
            temp.append(ln)
        else:
            placeholder_lines += 1

    code = '\n'.join(temp) + '\n' + PLACEHOLDER_FUNC
    print(f"   Removed {placeholder_lines} placeholder lines, injected clean version")

    # Write
    path = 'src/omega_system/omega_system.py'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"✅ Deployed: {path}")
    print(f"   Lines: {len(code.split(chr(10)))}")

    # Syntax check
    try:
        compile(code, path, 'exec')
        print("✅ Python syntax: OK")
    except SyntaxError as e:
        print(f"⚠️  Syntax error: line {e.lineno}: {e.msg}")
        clines = code.split('\n')
        start = max(0, e.lineno - 5)
        end = min(len(clines), e.lineno + 3)
        for idx in range(start, end):
            marker = " >>>" if idx + 1 == e.lineno else "    "
            print(f"{marker} L{idx+1}: {clines[idx][:120]}")
        return

    # 6. Black formatting
    try:
        import black as black_module
        formatted = black_module.format_str(code, mode=black_module.Mode(line_length=120))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(formatted)
        print("✅ Black format applied")
    except Exception as e:
        print(f"⚠️  Black skipped: {e}")

    # 7. Verify final syntax with black-formatted code
    with open(path, 'r', encoding='utf-8') as f:
        final_code = f.read()
    try:
        compile(final_code, path, 'exec')
        line_count = len(final_code.split('\n'))
        print(f"✅ Final syntax: OK ({line_count} lines)")
    except SyntaxError as e:
        print(f"⚠️  Final syntax error: line {e.lineno}: {e.msg}")
        clines = final_code.split('\n')
        start = max(0, e.lineno - 3)
        end = min(len(clines), e.lineno + 2)
        for idx in range(start, end):
            marker = " >>>" if idx + 1 == e.lineno else "    "
            print(f"{marker} L{idx+1}: {clines[idx][:120]}")


if __name__ == '__main__':
    main()
