from PIL import Image
import numpy as np
import math
from collections import Counter

# Entrada/Saida da masmorra(E) e Pingente(P) foram adicionados manualmente no txt

# Cores de referência
sample_colors = {
    'PAREDE': (183, 183, 183),
    'CAMINHO': (225, 225, 225)
}

terrain_to_letter = {
    'PAREDE': '#',
    'CAMINHO': '.'
}

def color_dist(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def converter_masmorra(img_path, out_path, grid_size=28, margin=2):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size

    rows = []
    counts = {k: 0 for k in sample_colors.keys()}

    for gy in range(grid_size):
        y0 = (gy * h) // grid_size + margin
        y1 = ((gy + 1) * h) // grid_size - margin

        row_chars = []
        for gx in range(grid_size):
            x0 = (gx * w) // grid_size + margin
            x1 = ((gx + 1) * w) // grid_size - margin

            region = np.array(img.crop((x0, y0, x1, y1))).reshape(-1, 3)
            region_tuples = [tuple(map(int, px)) for px in region]

            # Cor mais frequente no bloco
            most_common_color, _ = Counter(region_tuples).most_common(1)[0]

            # Descobre qual terreno é mais próximo dessa cor
            best = None
            bestd = float('inf')
            for t, cent in sample_colors.items():
                d = color_dist(most_common_color, cent)
                if d < bestd:
                    bestd = d
                    best = t

            counts[best] += 1
            row_chars.append(terrain_to_letter[best])

        # Aqui removemos os espaços entre os caracteres
        rows.append(''.join(row_chars))

    with open(out_path, 'w') as f:
        for r in rows:
            f.write(r + '\n')

    print(f"Arquivo salvo em: {out_path}")
    print("Contagem por tipo de célula:")
    for t, c in counts.items():
        print(f"  {t}: {c}")

# Exemplo
converter_masmorra("masmorra1(X).jpg", "masmorra1.txt")
converter_masmorra("masmorra2(Y).jpg", "masmorra2.txt")
converter_masmorra("masmorra3(Z).jpg", "masmorra3.txt")
