from PIL import Image, ImageDraw, ImageFont
import os
from collections import Counter

# Cores para cada tipo de terreno da masmorra
colors = {
    '#': (183, 183, 183),  # Parede
    '.': (225, 225, 225),  # Caminho
    'E': (0, 255, 0),      # Entrada
    'P': (255, 0, 0),      # Pingente
    '*': (0, 0, 255)       # Caminho da busca (opcional para plotar)
}

def text_size(draw, text, font):
    """Função auxiliar para medir texto usando textbbox."""
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def gerar_masmorra(input_path, output_path, cell_size=20):
    """
    Gera uma imagem de uma masmorra com coordenadas a partir de um arquivo de texto.

    Args:
        input_path (str): O caminho para o arquivo de texto da masmorra.
        output_path (str): O caminho para salvar a imagem de saída.
        cell_size (int): O tamanho de cada célula em pixels na imagem.
    """
    try:
        with open(input_path, "r") as f:
            mapa = [list(line.strip()) for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Erro: O arquivo {input_path} não foi encontrado.")
        return

    if not mapa:
        print("O arquivo de mapa está vazio.")
        return

    rows = len(mapa)
    cols = len(mapa[0])

    bg_color = (255, 255, 255)
    grid_color = (120, 120, 120)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    # Medir espaço necessário para rótulos
    tmp_img = Image.new("RGB", (10, 10))
    tmp_draw = ImageDraw.Draw(tmp_img)
    max_label = str(max(rows, cols))
    label_w, label_h = text_size(tmp_draw, max_label, font)
    label_space = max(label_w, label_h) + 8

    # Criar imagem com espaço para coordenadas
    img_w = label_space + cols * cell_size + 1
    img_h = label_space + rows * cell_size + 1
    image = Image.new("RGB", (img_w, img_h), bg_color)
    draw = ImageDraw.Draw(image)

    # Desenhar coordenadas de coluna (1-based)
    for c in range(cols):
        txt = str(c + 1)
        tw, th = text_size(draw, txt, font)
        x = label_space + c * cell_size + (cell_size - tw) / 2
        y = (label_space - th) / 2
        draw.text((x, y), txt, fill=(0, 0, 0), font=font)

    # Desenhar coordenadas de linha (1-based)
    for r in range(rows):
        txt = str(r + 1)
        tw, th = text_size(draw, txt, font)
        x = (label_space - tw) / 2
        y = label_space + r * cell_size + (cell_size - th) / 2
        draw.text((x, y), txt, fill=(0, 0, 0), font=font)

    # Desenhar cada célula com a cor correspondente
    for r in range(rows):
        for c in range(cols):
            terrain_char = mapa[r][c]
            color = colors.get(terrain_char, (0, 0, 0))

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


    image.save(output_path)
    print(f"Imagem da masmorra com coordenadas salva em: {output_path}")

if __name__ == "__main__":
    # Exemplo de uso para suas 3 masmorras
    if not os.path.exists("mapas"):
        print("Pasta 'mapas' não encontrada. Crie a pasta e coloque os arquivos .txt dentro dela.")
    else:
        gerar_masmorra("mapas/masmorra1.txt", "masmorra1_gerada.png")
        gerar_masmorra("mapas/masmorra2.txt", "masmorra2_gerada.png")
        gerar_masmorra("mapas/masmorra3.txt", "masmorra3_gerada.png")