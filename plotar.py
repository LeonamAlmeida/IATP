from PIL import Image, ImageDraw, ImageFont

# Caminho para o arquivo hyrule.txt existente
txt_path = "mapas/hyrule.txt"
out_img = "hyrule_grid.png"

# Cores para cada tipo de terreno
colors = {
    'M': (147, 141, 83),   # Montanha
    'A': (195, 187, 149),  # Areia
    'W': (82, 140, 212),   # Água
    'F': (3, 174, 81),     # Floresta
    'G': (148, 205, 74),   # Grama
    'X': (0, 0, 0),        # Dungeon X
    'Y': (0, 0, 0),        # Dungeon Y
    'Z': (0, 0, 0),        # Dungeon Z
    'S': (255, 0, 0),      # Espada
    'L': (255, 0, 255),    # Lost Woods
    '*': (255, 255, 255)   # Caminho encontrado
}

# Ler o mapa do TXT
with open(txt_path, "r") as f:
    mapa = [list(linha.strip()) for linha in f.readlines() if linha.strip()]

rows = len(mapa)
cols = len(mapa[0])

# Tamanho das células e margem para coordenadas
cell_size = 24
bg_color = (255, 255, 255)
grid_color = (120, 120, 120)

# Fonte
try:
    font = ImageFont.truetype("arial.ttf", 14)
except:
    font = ImageFont.load_default()

# Função auxiliar para medir texto usando textbbox
def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

# Medir espaço necessário para rótulos
tmp_img = Image.new("RGB", (10, 10))
tmp_draw = ImageDraw.Draw(tmp_img)
max_label = str(max(rows, cols))  # agora considerando 1-based
label_w, label_h = text_size(tmp_draw, max_label, font)
label_space = max(label_w, label_h) + 8

# Criar imagem
img_w = label_space + cols * cell_size + 1
img_h = label_space + rows * cell_size + 1
img = Image.new("RGB", (img_w, img_h), bg_color)
draw = ImageDraw.Draw(img)

# Coordenadas colunas (1-based)
for c in range(cols):
    txt = str(c + 1)
    tw, th = text_size(draw, txt, font)
    x = label_space + c * cell_size + (cell_size - tw) / 2
    y = (label_space - th) / 2
    draw.text((x, y), txt, fill=(0, 0, 0), font=font)

# Coordenadas linhas (1-based)
for r in range(rows):
    txt = str(r + 1)
    tw, th = text_size(draw, txt, font)
    x = (label_space - tw) / 2
    y = label_space + r * cell_size + (cell_size - th) / 2
    draw.text((x, y), txt, fill=(0, 0, 0), font=font)

# Desenhar células e grades
for r in range(rows):
    for c in range(cols):
        color = colors.get(mapa[r][c], (220, 220, 220))
        x0 = label_space + c * cell_size
        y0 = label_space + r * cell_size
        x1 = x0 + cell_size
        y1 = y0 + cell_size
        draw.rectangle([x0, y0, x1, y1], fill=color, outline=grid_color)

# Bordas externas
draw.rectangle([label_space, label_space,
                label_space + cols * cell_size,
                label_space + rows * cell_size],
               outline=(0, 0, 0), width=2)

# Salvar
img.save(out_img)
print(f"Mapa com coordenadas centralizadas salvo em {out_img}")
