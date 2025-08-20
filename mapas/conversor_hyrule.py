from PIL import Image
import numpy as np
import math

# Fiz alterações manuais no hyrule.txt para adicionar a espada 'S' de sword, e X, Y e Z referente a cada masmorra, além de L para lost woods
# Valor exato RGB adquirido via extensão eye drop
sample_colors = {
    'GRASS': (148, 205, 74),
    'FOREST': (3, 174, 81),
    'MOUNTAIN': (147, 141, 83),
    'SAND': (195, 187, 149),
    'WATER': (82, 140, 212)
}

terrain_to_letter = {
    'GRASS': 'G',
    'FOREST': 'F',
    'SAND': 'A',      # Areia
    'MOUNTAIN': 'M',
    'WATER': 'W'      # Água
}

def color_dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

# --- parâmetros ---
img_path = 'hyrule.jpg'
grid_size = 42

img = Image.open(img_path).convert('RGB')
w, h = img.size

rows = []
counts = {k: 0 for k in sample_colors.keys()}

for gy in range(grid_size):
    y0 = (gy * h) // grid_size
    y1 = ((gy + 1) * h) // grid_size
    if y1 <= y0:
        y1 = min(y0 + 1, h)

    row_chars = []
    for gx in range(grid_size):
        x0 = (gx * w) // grid_size
        x1 = ((gx + 1) * w) // grid_size
        if x1 <= x0:
            x1 = min(x0 + 1, w)

        region = np.array(img.crop((x0, y0, x1, y1))).reshape(-1, 3)
        avg = tuple(region.mean(axis=0))

        best = None
        bestd = float('inf')
        for t, cent in sample_colors.items():
            d = color_dist(avg, cent)
            if d < bestd:
                bestd = d
                best = t

        counts[best] += 1
        row_chars.append(terrain_to_letter[best])

    rows.append(''.join(row_chars))

out_file = 'hyrule.txt'
with open(out_file, 'w') as f:
    for r in rows:
        f.write(r + '\n')

print("Arquivo salvo em:", out_file)
print("Contagem por terreno (células):")
for t, c in counts.items():
    print(f"  {t}: {c}")
