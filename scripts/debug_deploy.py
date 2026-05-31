# Debug script
import re

with open('docs/task6.md', 'r', encoding='utf-8') as f:
    raw = f.read()

# Step 1: fix markdown
DUNDER_FIXES = {
    '**future**': '__future__', '**init**': '__init__', '**name**': '__name__',
    '**main**': '__main__', '**mul**': '__mul__', '**str**': '__str__',
    '**gt**': '__gt__', '**getattr**': '__getattr__',
}
SPECIAL_FIXES = {'GENE*CATALOG': 'GENE_CATALOG'}
def fix_markdown(text):
    for old, new in DUNDER_FIXES.items():
        text = text.replace(old, new)
    text = text.replace('\\*', '*')
    for old, new in SPECIAL_FIXES.items():
        text = text.replace(old, new)
    return text

code = fix_markdown(raw)
lines = code.split('\n')

# Show raw lines around @dataclass, CausalChain, SpacetimeControlSystem
for i in range(920, 960):
    line = lines[i]
    if any(x in line for x in ['CausalChain', 'Spacetime', '@dataclass', 'reversible', 'reversed', '"""']):
        print(f'L{i+1}: indent={len(line)-len(line.lstrip())} {repr(line[:120])}')
