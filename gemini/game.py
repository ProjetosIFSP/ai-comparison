import pygame
import math
import random
import cv2
import os
import sys
sys.path.insert(0, '/home/abner/Documentos/IFSP/7semestre/IA/teste-llm/.venv/lib/python3.12/site-packages')

# Inicialização do Pygame
pygame.init()

# Constantes da tela
LARGURA_TELA = 800
ALTURA_TELA = 600
TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Quadrado Giratório e Bola Quicante")
RELOGIO = pygame.time.Clock()
FPS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)

# Propriedades do Quadrado
LADO_QUADRADO = 200
ESPESSURA_BORDA_QUADRADO = 2
CENTRO_QUADRADO = pygame.math.Vector2(LARGURA_TELA / 2, ALTURA_TELA / 2)
VELOCIDADE_ANGULAR_QUADRADO = 60  # graus por segundo
angulo_quadrado_atual = 0.0  # ângulo em graus

# Vértices locais do quadrado (em torno da origem 0,0) antes da rotação e translação.
# Definidos em sentido horário para facilitar o cálculo da normal externa.
vertices_locais_quadrado = [
    pygame.math.Vector2(-LADO_QUADRADO / 2, -LADO_QUADRADO / 2), # Superior Esquerdo
    pygame.math.Vector2(LADO_QUADRADO / 2, -LADO_QUADRADO / 2),  # Superior Direito
    pygame.math.Vector2(LADO_QUADRADO / 2, LADO_QUADRADO / 2),   # Inferior Direito
    pygame.math.Vector2(-LADO_QUADRADO / 2, LADO_QUADRADO / 2),  # Inferior Esquerdo
]

# Propriedades da Bola
RAIO_BOLA = 10
posicao_bola = pygame.math.Vector2(CENTRO_QUADRADO.x, CENTRO_QUADRADO.y)
velocidade_bola = pygame.math.Vector2(0, 0)
cor_bola = pygame.Color(VERMELHO)

# Gravidade: No Pygame, o eixo Y positivo é para baixo.
ACELERACAO_GRAVIDADE = pygame.math.Vector2(0, 350)  # pixels/s^2

# Para gravação
gravando = False
frames = []

# Configurações para gravação de vídeo
video_nome = "gameplay_gemini.mp4"
gif_nome = "gameplay_gemini.gif"
quadro_tamanho = (LARGURA_TELA, ALTURA_TELA)
fps = 30
quadro_codificador = cv2.VideoWriter_fourcc(*"mp4v")
video_writer = cv2.VideoWriter(video_nome, quadro_codificador, fps, quadro_tamanho)

def rotacionar_vertices(vertices_locais, angulo_graus, centro_rotacao):
    """
    Rotaciona uma lista de vértices locais em torno da origem e depois os translada para o centro_rotacao.
    """
    angulo_rad = math.radians(angulo_graus)
    cos_ang = math.cos(angulo_rad)
    sin_ang = math.sin(angulo_rad)
    
    vertices_globais_rotacionados = []
    for vertice_local in vertices_locais:
        x_rot = vertice_local.x * cos_ang - vertice_local.y * sin_ang
        y_rot = vertice_local.x * sin_ang + vertice_local.y * cos_ang
        vertices_globais_rotacionados.append(pygame.math.Vector2(x_rot + centro_rotacao.x, y_rot + centro_rotacao.y))
    return vertices_globais_rotacionados

def ponto_mais_proximo_no_segmento(ponto_externo, seg_ponto_a, seg_ponto_b):
    """
    Encontra o ponto em um segmento de reta [seg_ponto_a, seg_ponto_b] que é o mais próximo de ponto_externo.
    """
    vetor_segmento = seg_ponto_b - seg_ponto_a
    if vetor_segmento.length_squared() == 0: # Se o segmento for um ponto
        return seg_ponto_a
    
    vetor_ap = ponto_externo - seg_ponto_a
    # Projeta o vetor_ap no vetor_segmento
    # t é a proporção ao longo do vetor_segmento onde a projeção cai
    t = vetor_ap.dot(vetor_segmento) / vetor_segmento.length_squared()
    
    # Limita t para estar entre 0 e 1 (dentro do segmento)
    if t < 0.0:
        return seg_ponto_a # Ponto mais próximo é o início do segmento
    elif t > 1.0:
        return seg_ponto_b # Ponto mais próximo é o fim do segmento
    else:
        return seg_ponto_a + t * vetor_segmento # Projeção está no segmento

# Função para converter MP4 para GIF
def converter_para_gif(video_path, gif_path):
    comando = f"ffmpeg -i {video_path} -vf 'fps=10,scale=320:-1:flags=lanczos' {gif_path}"
    os.system(comando)

# Loop principal do jogo
rodando = True
while rodando:
    dt = RELOGIO.tick(FPS) / 1000.0
    if dt > 0.1: # Limitar dt para evitar saltos muito grandes em caso de lag
        dt = 0.1

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # --- Lógica de Atualização do Jogo ---
    # Rotaciona o quadrado
    angulo_quadrado_atual = (angulo_quadrado_atual + VELOCIDADE_ANGULAR_QUADRADO * dt) % 360
    vertices_globais_quadrado = rotacionar_vertices(vertices_locais_quadrado, angulo_quadrado_atual, CENTRO_QUADRADO)

    # Atualiza a física da bola
    velocidade_bola += ACELERACAO_GRAVIDADE * dt
    posicao_bola += velocidade_bola * dt

    # Detecção de Colisão e Resposta (Lógica de Resolução Única para Penetração Máxima)
    num_vertices_quadrado = len(vertices_globais_quadrado)
    
    # Armazena informações sobre a colisão que causa a penetração mais profunda
    colisao_para_resolver = {
        "profundidade_penetracao": 0.0,  # Quão "fundo" a bola entrou, ao longo da normal
        "normal_colisao": None,          # Normal da superfície da colisão mais profunda
        "houve_colisao": False
    }

    # Testa contra todos os lados para encontrar a melhor colisão para resolver
    for i in range(num_vertices_quadrado):
        ponto_lado_1 = vertices_globais_quadrado[i]
        ponto_lado_2 = vertices_globais_quadrado[(i + 1) % num_vertices_quadrado] # Pega o próximo vértice

        vetor_do_lado = ponto_lado_2 - ponto_lado_1
        if vetor_do_lado.length_squared() == 0: # Evita divisão por zero se o lado tiver comprimento 0
            continue
        
        # Calcula a normal da superfície do lado (apontando para fora do quadrado)
        normal_da_superficie = pygame.math.Vector2(vetor_do_lado.y, -vetor_do_lado.x).normalize()

        # Distância do centro da bola à linha infinita do lado, medida ao longo da normal.
        # Negativa se o centro da bola cruzou para o "interior" da linha.
        distancia_projetada_a_linha = (posicao_bola - ponto_lado_1).dot(normal_da_superficie)

        # Se o centro da bola está a uma distância menor que RAIO_BOLA da linha (colisão potencial)
        if distancia_projetada_a_linha < RAIO_BOLA:
            # Verifica se o ponto de contato real (mais próximo no segmento) também está dentro do raio
            ponto_de_contato_no_segmento = ponto_mais_proximo_no_segmento(posicao_bola, ponto_lado_1, ponto_lado_2)
            distancia_real_ao_segmento = (posicao_bola - ponto_de_contato_no_segmento).length()

            # A colisão é válida se a bola estiver penetrando a linha do lado E
            # a distância ao segmento real também for menor que o raio.
            # O epsilon (1e-5) evita problemas com ponto flutuante.
            if distancia_real_ao_segmento < RAIO_BOLA and distancia_real_ao_segmento > 1e-5:
                # COLISÃO REAL COM ESTE SEGMENTO!
                # Calcula o quanto a bola penetrou ao longo desta normal.
                # Se distancia_projetada_a_linha é -2 (2 unidades para dentro) e RAIO_BOLA é 10,
                # a penetração é 10 - (-2) = 12. Isso é o quanto precisamos empurrar para fora.
                penetracao_atual = RAIO_BOLA - distancia_projetada_a_linha
                
                # Se esta penetração for a mais profunda encontrada até agora, armazena suas informações.
                if penetracao_atual > colisao_para_resolver["profundidade_penetracao"]:
                    colisao_para_resolver["profundidade_penetracao"] = penetracao_atual
                    colisao_para_resolver["normal_colisao"] = normal_da_superficie
                    colisao_para_resolver["houve_colisao"] = True
                    
    # Se qualquer colisão foi detectada e armazenada (ou seja, houve pelo menos uma penetração válida)
    if colisao_para_resolver["houve_colisao"]:
        normal_a_usar = colisao_para_resolver["normal_colisao"]
        penetracao_a_corrigir = colisao_para_resolver["profundidade_penetracao"]
        
        epsilon_pushout = 0.1 # Pequena folga para empurrar a bola um pouco mais para fora
        
        # 1. Correção de Posição:
        # Move a bola para fora ao longo da normal da penetração mais significativa.
        posicao_bola += normal_a_usar * (penetracao_a_corrigir + epsilon_pushout)

        # 2. Reflexão da Velocidade:
        velocidade_bola = velocidade_bola.reflect(normal_a_usar)
        
        # 3. Trocar cor da bola:
        cor_bola = pygame.Color(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    
    # --- Desenho na Tela ---
    TELA.fill(PRETO) # Limpa a tela com a cor preta

    # Desenhar o Quadrado
    pygame.draw.polygon(TELA, BRANCO, vertices_globais_quadrado, ESPESSURA_BORDA_QUADRADO)

    # Desenhar a Bola
    pygame.draw.circle(TELA, cor_bola, (int(posicao_bola.x), int(posicao_bola.y)), RAIO_BOLA)

    pygame.display.flip() # Atualiza a tela inteira para mostrar o que foi desenhado

    # Gravação de vídeo
    frame = pygame.surfarray.array3d(pygame.display.get_surface())
    frame = cv2.cvtColor(cv2.transpose(frame), cv2.COLOR_RGB2BGR)
    video_writer.write(frame)

# Libera o gravador de vídeo e converte para GIF
video_writer.release()
converter_para_gif(video_nome, gif_nome)

pygame.quit()

print("Gravação concluída!")
