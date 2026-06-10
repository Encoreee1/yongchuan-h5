import re, os, base64

PROJECT = r'd:\Study\project2\yongchuan-h5'
HTML = os.path.join(PROJECT, 'index.html')

with open(HTML, 'r', encoding='utf-8') as f:
    content = f.read()

def encode(filepath):
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(filepath)[1].lower()
    mime = {'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.mp3':'audio/mpeg'}[ext]
    return f'data:{mime};base64,{data}'

# 1. Replace CSS url() references
def replace_css_url(m):
    path = m.group(1)
    full = os.path.join(PROJECT, path)
    if os.path.exists(full):
        return f'url({encode(full)})'
    return m.group(0)

content = re.sub(r'url\(([^)]+)\)', replace_css_url, content)

# 2. Replace all static asset paths
for root, dirs, files in os.walk(os.path.join(PROJECT, 'assets')):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, PROJECT).replace('\\', '/')
        uri = encode(full)
        content = content.replace(rel, uri)

# 3. Handle JS template literals for icons
icon_uris = {}
for name in ['icon_bandage','icon_medkit','icon_stretcher','icon_water',
             'icon_whistle','icon_debris','icon_tree','icon_car','icon_barrel',
             'icon_blanket','icon_medal']:
    path = os.path.join(PROJECT, 'assets', 'images', f'{name}.png')
    if os.path.exists(path):
        icon_uris[name] = encode(path)

icon_map_entries = ', '.join(f"'{k}':'{v}'" for k, v in icon_uris.items())
icon_map_js = f'{{{icon_map_entries}}}'

# Replace template literal patterns — match the inner expression only
content = content.replace(
    'assets/images/${iconName}.png',
    '${ICON_MAP[iconName]}'
)
content = content.replace(
    'assets/images/${p.icon}.png',
    '${ICON_MAP[p.icon]}'
)
content = content.replace(
    'assets/images/${name}.png',
    '${ICON_MAP[name]}'
)
content = content.replace(
    'assets/images/${PUZZLE_ICONS[i]}.png',
    '${ICON_MAP[PUZZLE_ICONS[i]]}.png'
)

# Insert ICON_MAP before </body>
map_decl = f'\n<script>const ICON_MAP={icon_map_js};</script>\n'
content = content.replace('</body>', map_decl + '</body>')

# Write output
out = os.path.join(PROJECT, 'yongchuan-h5-standalone.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(content)

size_mb = os.path.getsize(out) / (1024*1024)

# Verify
remaining = [m.group(0) for m in re.finditer(r'assets/(audio|images)/', content)]
print(f'Done: {out}')
print(f'Size: {size_mb:.1f}MB')
print(f'Remaining external asset refs: {len(remaining)}')
if remaining:
    for r in remaining[:5]:
        print(f'  {r[:100]}')
