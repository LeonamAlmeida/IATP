import heapq
import os
import itertools
from PIL import Image, ImageDraw, ImageFont

# --- Parâmetros e Configurações ---
TERRAIN_COSTS = {
    'G': 10, 'A': 20, 'F': 100, 'M': 150, 'W': 180,
    'S': 10, 'X': 20, 'Y': 20, 'Z': 20, 'L': 10
}

DUNGEON_PATH_COST = 10
DUNGEON_WALL = '#'

# Cores
aSTAR_COLORS = {
    'M': (147, 141, 83), 'A': (195, 187, 149), 'W': (82, 140, 212),
    'F': (3, 174, 81), 'G': (148, 205, 74), 'X': (0, 0, 0), 'Y': (0, 0, 0),
    'Z': (0, 0, 0), 'S': (255, 0, 0), 'L': (255, 0, 255)
}

DUNGEON_COLORS = {
    '#': (183, 183, 183), '.': (225, 225, 225), 'E': (0, 255, 0), 'P': (255, 0, 0)
}

PATH_COLOR = (255, 255, 255)
GRID_COLOR = (120, 120, 120)

# Classe que representa cada nó (célula) do mapa
class Node:
    def __init__(self, position, parent=None):
        self.position = position # (linha, coluna)
        self.parent = parent     # nó pai, usado para reconstruir o caminho
        self.g = 0               # custo acumulado até aqui
        self.h = 0               # heurística (distância estimada até o objetivo)
        self.f = 0               # f = g + h
    def __lt__(self, other):
        return self.f < other.f

# Lê o mapa de um arquivo de texto e cria a matriz
# Cada linha do arquivo vira uma lista de caracteres
def load_map(file_path):
    maze = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                cleaned_line = line.strip().replace(' ', '')
                if cleaned_line:
                    maze.append(list(cleaned_line))
    except FileNotFoundError:
        print(f"Erro: Arquivo {file_path} não encontrado.")
        return None
    return maze

# Função heurística (distância de Manhattan) - (Admissível porque nunca superestima o custo real)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Implementação da busca A*
def a_star_search(maze, start, end, is_dungeon=False):
    if not maze: return None, float('inf')

    # Ajuste para usar índices (linha-1, coluna-1) (lista em python começa com 0)
    start_indexed = (start[0]-1, start[1]-1)
    end_indexed = (end[0]-1, end[1]-1)

    # open_list = nós a serem explorados (fila de prioridade), closed_list = nós já visitados
    open_list, closed_list = [], set()
    # Nós de início e fim
    start_node, end_node = Node(start_indexed), Node(end_indexed)
    # Insere o nó inicial na fila de prioridade
    heapq.heappush(open_list, start_node)

    while open_list:
        # Pega o nó com menor f = g + h
        current = heapq.heappop(open_list)
        closed_list.add(current.position)

        # Se chegamos no destino, reconstruímos o caminho
        if current.position == end_node.position:
            path, node = [], current
            while node:
                path.append(node.position)
                node = node.parent
            return path[::-1], current.g
        (x, y) = current.position

        # Expande vizinhos (N, S, L, O)
        for nx, ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if not (0 <= nx < len(maze) and 0 <= ny < len(maze[0])):
                continue

            # Calcula custo do vizinho dependendo do tipo de mapa
            if is_dungeon:
                if maze[nx][ny] == DUNGEON_WALL: continue
                cost = DUNGEON_PATH_COST
            else:
                terrain = maze[nx][ny]
                cost = TERRAIN_COSTS.get(terrain, float('inf'))
                if cost == float('inf'): continue
            
            # Cria nó vizinho
            neighbor = Node((nx,ny), current)
            # Se já visitado, ignora
            if neighbor.position in closed_list: continue

            # Calcula novo custo acumulado g
            new_g = current.g + cost

            # Se já existe um nó igual na open_list com g menor, ignora
            if any(n.position==neighbor.position and new_g>=n.g for n in open_list):
                continue

            # Atualiza valores g, h e f do vizinho
            neighbor.g = new_g
            neighbor.h = heuristic(neighbor.position, end_node.position)
            neighbor.f = neighbor.g + neighbor.h

            # Adiciona vizinho à lista de exploração
            heapq.heappush(open_list, neighbor)

    return None, float('inf')

def text_size(draw, text, font):
    try:
        bbox = draw.textbbox((0,0), text, font=font)
        return bbox[2]-bbox[0], bbox[3]-bbox[1]
    except AttributeError:
        return draw.textsize(text, font=font)

def plot_path_on_map(maze, path, filename, is_dungeon=False, cell_size=20):
    rows, cols = len(maze), len(maze[0])
    try: font = ImageFont.truetype("arial.ttf",14)
    except: font = ImageFont.load_default()
    tmp_img = Image.new("RGB",(10,10))
    tmp_draw = ImageDraw.Draw(tmp_img)
    label_w,label_h = text_size(tmp_draw,str(max(rows,cols)),font)
    label_space = max(label_w,label_h)+8
    img = Image.new("RGB", (label_space+cols*cell_size+1,label_space+rows*cell_size+1),(255,255,255))
    draw = ImageDraw.Draw(img)
    for c in range(cols):
        txt=str(c+1); tw,th=text_size(draw,txt,font)
        x=label_space+c*cell_size+(cell_size-tw)/2; y=(label_space-th)/2
        draw.text((x,y),txt,fill=(0,0,0),font=font)
    for r in range(rows):
        txt=str(r+1); tw,th=text_size(draw,txt,font)
        x=(label_space-tw)/2; y=label_space+r*cell_size+(cell_size-th)/2
        draw.text((x,y),txt,fill=(0,0,0),font=font)
    colors = DUNGEON_COLORS if is_dungeon else aSTAR_COLORS
    for r in range(rows):
        for c in range(cols):
            color=colors.get(maze[r][c],(0,0,0))
            x0=label_space+c*cell_size; y0=label_space+r*cell_size
            draw.rectangle([x0,y0,x0+cell_size,y0+cell_size],fill=color,outline=GRID_COLOR)
    for x,y in path:
        x0=label_space+y*cell_size; y0=label_space+x*cell_size
        draw.rectangle([x0,y0,x0+cell_size,y0+cell_size],fill=PATH_COLOR)
    draw.rectangle([label_space,label_space,label_space+cols*cell_size,label_space+rows*cell_size],outline=(0,0,0),width=2)
    img.save(filename)
    print(f"Mapa visual salvo em: {filename}")

# Função que simula toda a jornada do Link
# Testa todas as ordens possíveis das masmorras e calcula o custo total
def simulate_journey(order, hyrule_map, dungeons, start_pos, lost_woods, save_images=True):
    total_cost=0; current=start_pos; step=1
    if save_images:
        print("Iniciando a jornada de Link...")
    
    # Para cada masmorra na ordem escolhida
    for idx in order:
        hyrule_entrance, dmap, dentrance, dping = dungeons[idx]
        # Caminho até a entrada da masmorra
        if save_images:
            print(f"\n--- Passo {step}: Indo para Masmorra com entrada em {hyrule_entrance} ---")
        path,cost=a_star_search(hyrule_map,current,hyrule_entrance)
        if not path: return float('inf')
        total_cost+=cost
        if save_images:
            plot_path_on_map(hyrule_map,path,f"percurso/hyrule_caminho_{step}.png")
            print(f"Caminho no mapa principal (custo: {cost}):\nCusto acumulado: {total_cost}")
        current=hyrule_entrance; step+=1
        # Caminho até o pingente dentro da masmorra
        if save_images:
            print(f"\n--- Passo {step}: Explorando a Masmorra (indo ao Pingente em {dping}) ---")
        path,cost=a_star_search(dmap,dentrance,dping,True)
        if not path: return float('inf')
        total_cost+=cost
        if save_images:
            plot_path_on_map(dmap,path,f"percurso/masmorra_{step-1}_pingente.png",True)
            print(f"Caminho dentro da Masmorra (custo: {cost}):\nCusto acumulado: {total_cost}")
        step+=1
        # Caminho de volta para a saída da masmorra
        if save_images:
            print(f"\n--- Passo {step}: Voltando da Masmorra para a saída ({dentrance}) ---")
        path,cost=a_star_search(dmap,dping,dentrance,True)
        if not path: return float('inf')
        total_cost+=cost
        if save_images:
            plot_path_on_map(dmap,path,f"percurso/masmorra_{step-2}_saida.png",True)
            print(f"Caminho de volta na Masmorra (custo: {cost}):\nCusto acumulado: {total_cost}")
        step+=1

    # Caminho final até Lost Woods
    if save_images:
        print(f"\n--- Passo {step}: Indo para Lost Woods em {lost_woods} ---")
    path,cost=a_star_search(hyrule_map,current,lost_woods)
    if not path: return float('inf')
    total_cost+=cost
    if save_images:
        plot_path_on_map(hyrule_map,path,f"percurso/hyrule_caminho_{step}.png")
        print(f"Caminho final para Lost Woods (custo: {cost}):\nCusto acumulado: {total_cost}")

        print("\n------------------------------------")
        print(f"Jornada de Link concluída com sucesso! Chegamos em Lost Woods. Custo total: {total_cost}")
        print("------------------------------------")
    return total_cost

def main():
    map_folder="mapas"
    hyrule=load_map(os.path.join(map_folder,"hyrule.txt"))
    m1=load_map(os.path.join(map_folder,"masmorra1.txt"))
    m2=load_map(os.path.join(map_folder,"masmorra2.txt"))
    m3=load_map(os.path.join(map_folder,"masmorra3.txt"))
    if not all([hyrule,m1,m2,m3]): return

    start_pos=(28,25); lost_woods=(6,7)
    dungeons=[((33,6),m1,(27,15),(4,14)),((18,40),m2,(26,14),(3,14)),((2,25),m3,(26,15),(20,16))]

    best_cost=float('inf'); best_order=None
    # Testa todas as ordens possíveis de visitar as masmorras
    for perm in itertools.permutations(range(3)):
        cost=simulate_journey(perm,hyrule,dungeons,start_pos,lost_woods,save_images=False)
        print(f"Ordem {perm} -> custo total: {cost}")
        if cost<best_cost:
            best_cost=cost; best_order=perm

    # Executa a melhor ordem com prints e salvando imagens
    simulate_journey(best_order,hyrule,dungeons,start_pos,lost_woods,save_images=True)
    print(f"\nMelhor ordem de masmorras: {best_order}, custo total: {best_cost}")

if __name__=="__main__":
    if not os.path.exists("mapas"):
        print("Pasta 'mapas' não encontrada.")
    else:
        if not os.path.exists("percurso"): os.makedirs("percurso")
        main()
