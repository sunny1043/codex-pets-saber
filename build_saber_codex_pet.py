from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

SRC = Path('/Users/sunny/Desktop/ai相关/桌宠project/动作')
OUT = Path('/Users/sunny/Desktop/ai相关/桌宠project/codex-pet')
CELL_W, CELL_H = 192, 208
COLS, ROWS = 8, 11

def load(name):
    im = Image.open(SRC / name).convert('RGBA')
    # Preserve the supplied transparent artwork and fit it safely inside a cell.
    scale = min((CELL_W * 0.82) / im.width, (CELL_H * 0.88) / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((CELL_W - im.width)//2, CELL_H - im.height - 10))
    return canvas

def frame(base, kind, i):
    im = base.copy()
    if kind == 'idle':
        # subtle breathing loop
        dy = [1, 0, -1, 0, 1, 0, -1, 0][i]
        out = Image.new('RGBA', im.size, (0,0,0,0)); out.alpha_composite(im, (0,dy)); return out
    if kind == 'jumping':
        dy = [7, 4, 0, -4, -7, -4, 0, 4][i]
        out = Image.new('RGBA', im.size, (0,0,0,0)); out.alpha_composite(im, (0,dy)); return out
    if kind == 'running-right':
        dx = [-6,-3,0,3,6,3,0,-3][i]
        out = Image.new('RGBA', im.size, (0,0,0,0)); out.alpha_composite(im, (dx,0)); return out
    if kind == 'running-left':
        return ImageOps.mirror(frame(base, 'running-right', i))
    if kind == 'waving':
        return im.rotate([-2,0,2,0,-2,0,2,0][i], resample=Image.Resampling.BICUBIC, expand=False)
    if kind == 'failed':
        return ImageEnhance.Brightness(im).enhance([0.9,0.85,0.8,0.85,0.9,0.85,0.8,0.85][i])
    if kind == 'waiting':
        return im.rotate([2,1,0,-1,-2,-1,0,1][i], resample=Image.Resampling.BICUBIC, expand=False)
    if kind == 'running':
        return ImageEnhance.Contrast(im).enhance([1.0,1.03,1.06,1.03,1.0,1.03,1.06,1.03][i])
    if kind == 'review':
        return im.rotate([1,1,0,-1,-1,-1,0,1][i], resample=Image.Resampling.BICUBIC, expand=False)
    return im

OUT.mkdir(parents=True, exist_ok=True)
base = load('思考.png')
sources = {
    'idle':'睡觉.png', 'running-right':'开心.png', 'running-left':'开心.png',
    'waving':'提醒.png', 'jumping':'睡醒.png', 'failed':'错误提示.png',
    'waiting':'提醒.png', 'running':'思考.png', 'review':'思考.png'
}
atlas = Image.new('RGBA', (COLS*CELL_W, ROWS*CELL_H), (0,0,0,0))
names = list(sources)
counts = [6, 8, 8, 4, 5, 8, 6, 6, 6]
for row, kind in enumerate(names):
    src = load(sources[kind])
    for col in range(COLS):
        if col < counts[row] or (row == 0 and col == 6):
            atlas.alpha_composite(frame(src, kind, col), (col*CELL_W, row*CELL_H))
# Rows 9-10: 16 look-direction cells, using coherent registered front/rear families.
for col in range(COLS):
    src = load('开心.png')
    atlas.alpha_composite(ImageOps.mirror(src) if col >= 4 else src, (col*CELL_W, 9*CELL_H))
    src2 = load('思考.png')
    atlas.alpha_composite(ImageOps.mirror(src2) if col >= 4 else src2, (col*CELL_W, 10*CELL_H))
atlas.save(OUT/'spritesheet.png')
(OUT/'pet.json').write_text('''{\n  "id": "saber",\n  "displayName": "Saber",\n  "description": "A chibi Saber-inspired Codex pet built from the existing transparent action artwork.",\n  "spriteVersionNumber": 2,\n  "spritesheetPath": "spritesheet.png"\n}\n''', encoding='utf-8')
print(OUT/'spritesheet.png')
print(OUT/'pet.json')
