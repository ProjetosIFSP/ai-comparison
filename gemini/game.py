import pygame
import math
import random

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
# Portanto, um valor positivo em Y na aceleração simula a gravidade puxando para baixo.
ACELERACAO_GRAVIDADE = pygame.math.Vector2(0, 350)  # pixels/s^2 (ajuste para mais ou menos gravidade)

def rotacionar_vertices(vertices_locais, angulo_graus, centro_rotacao):
    """
    Rotaciona uma lista de vértices locais em torno da origem e depois os translada para o centro_rotacao.
    Args:
        vertices_locais: Lista de pygame.math.Vector2 representando os vértices em relação à origem.
        angulo_graus: O ângulo de rotação em graus.
        centro_rotacao: pygame.math.Vector2 para onde os vértices rotacionados serão transladados.
    Returns:
        Lista de pygame.math.Vector2 representando os vértices globais rotacionados.
    """
    angulo_rad = math.radians(angulo_graus)
    cos_ang = math.cos(angulo_rad)
    sin_ang = math.sin(angulo_rad)
    
    vertices_globais_rotacionados = []
    for vertice_local in vertices_locais:
        # Rotaciona o vértice local em torno da origem (0,0)
        x_rot = vertice_local.x * cos_ang - vertice_local.y * sin_ang
        y_rot = vertice_local.x * sin_ang + vertice_local.y * cos_ang
        # Translada o vértice rotacionado para a posição global do centro do quadrado
        vertices_globais_rotacionados.append(pygame.math.Vector2(x_rot + centro_rotacao.x, y_rot + centro_rotacao.y))
    return vertices_globais_rotacionados

def ponto_mais_proximo_no_segmento(ponto_externo, seg_ponto_a, seg_ponto_b):
    """
    Encontra o ponto em um segmento de reta [seg_ponto_a, seg_ponto_b] que é o mais próximo de ponto_externo.
    Args:
        ponto_externo: pygame.math.Vector2 - o ponto para o qual queremos encontrar o mais próximo no segmento.
        seg_ponto_a: pygame.math.Vector2 - ponto inicial do segmento.
        seg_ponto_b: pygame.math.Vector2 - ponto final do segmento.
    Returns:
        pygame.math.Vector2 - o ponto no segmento mais próximo de ponto_externo.
    """
    vetor_segmento = seg_ponto_b - seg_ponto_a
    # Se o segmento tiver comprimento zero (A e B são o mesmo ponto)
    if vetor_segmento.length_squared() == 0:
        return seg_ponto_a
    
    # Vetor do início do segmento até o ponto externo
    vetor_ap = ponto_externo - seg_ponto_a
    
    # Projeta AP em AB, normalizado pelo comprimento ao quadrado de AB
    # t = AP · AB / |AB|^2
    t = vetor_ap.dot(vetor_segmento) / vetor_segmento.length_squared()
    
    if t < 0.0: # Ponto mais próximo é A
        return seg_ponto_a
    elif t > 1.0: # Ponto mais próximo é B
        return seg_ponto_b
    else: # Projeção está dentro do segmento
        return seg_ponto_a + t * vetor_segmento

# Loop principal do jogo
rodando = True
while rodando:
    # Delta time (tempo desde o último frame) em segundos
    # Ajuda a manter a física consistente independentemente da taxa de quadros
    dt = RELOGIO.tick(FPS) / 1000.0
    # Limitar dt para evitar saltos muito grandes na física se houver lag
    if dt > 0.1:
        dt = 0.1

    # Gerenciamento de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # --- Lógica de Atualização do Jogo ---

    # Rotacionar Quadrado
    angulo_quadrado_atual += VELOCIDADE_ANGULAR_QUADRADO * dt
    angulo_quadrado_atual %= 360  # Mantém o ângulo entre 0 e 360 graus
    
    # Calcula as posições globais dos vértices do quadrado rotacionado
    vertices_globais_quadrado = rotacionar_vertices(vertices_locais_quadrado, angulo_quadrado_atual, CENTRO_QUADRADO)

    # Atualizar Física da Bola
    # Aplicar aceleração da gravidade à velocidade
    velocidade_bola += ACELERACAO_GRAVIDADE * dt
    # Atualizar posição da bola com base na velocidade
    posicao_bola += velocidade_bola * dt

    # Detecção de Colisão e Resposta
    num_vertices_quadrado = len(vertices_globais_quadrado)
    for i in range(num_vertices_quadrado):
        # Define os dois vértices que formam um lado do quadrado
        ponto_lado_1 = vertices_globais_quadrado[i]
        ponto_lado_2 = vertices_globais_quadrado[(i + 1) % num_vertices_quadrado] # Próximo vértice, fazendo a volta

        # Encontra o ponto no lado atual do quadrado que está mais próximo do centro da bola
        ponto_de_contato_no_lado = ponto_mais_proximo_no_segmento(posicao_bola, ponto_lado_1, ponto_lado_2)
        
        # Vetor do ponto de contato no lado para o centro da bola
        vetor_contato_para_bola = posicao_bola - ponto_de_contato_no_lado
        distancia_bola_lado = vetor_contato_para_bola.length()

        # Verifica se houve colisão (distância menor que o raio da bola)
        # E distancia_bola_lado > 0 para evitar problemas se a bola estiver exatamente no ponto_de_contato_no_lado
        if distancia_bola_lado < RAIO_BOLA and distancia_bola_lado > 1e-5: # Adicionado epsilon para evitar divisão por zero se normalizar
            # Colisão detectada!

            # 1. Calcular a normal da superfície de colisão
            # A normal do lado do quadrado, apontando para fora.
            # Como os vértices locais foram definidos em sentido horário, esta normal aponta para fora.
            vetor_do_lado = ponto_lado_2 - ponto_lado_1
            if vetor_do_lado.length_squared() == 0: continue # Lado com comprimento zero, ignorar

            normal_da_superficie = pygame.math.Vector2(vetor_do_lado.y, -vetor_do_lado.x).normalize()

            # 2. Correção de Posição (para evitar que a bola "afunde" no quadrado)
            # Move a bola para que ela apenas toque a superfície
            penetracao = RAIO_BOLA - distancia_bola_lado
            posicao_bola += normal_da_superficie * penetracao

            # 3. Reflexão da Velocidade (quicar)
            # A função reflect do Pygame faz v_new = v_old - 2 * (v_old . normal) * normal
            velocidade_bola = velocidade_bola.reflect(normal_da_superficie)
            
            # 4. Trocar cor da bola para uma cor aleatória (evitando cores muito escuras)
            cor_bola = pygame.Color(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            
            # Importante: Processar apenas uma colisão por frame para simplificar.
            # Se a bola colidir com múltiplos lados simultaneamente (ex: um canto),
            # esta abordagem simples pode não ser perfeitamente física, mas funciona para muitos casos.
            break 
    
    # --- Desenho na Tela ---
    TELA.fill(PRETO) # Limpa a tela com a cor preta

    # Desenhar o Quadrado
    # pygame.draw.polygon(surface, color, list_of_points, width)
    # width = 0 preenche o polígono, width > 0 desenha apenas a borda
    pygame.draw.polygon(TELA, BRANCO, vertices_globais_quadrado, ESPESSURA_BORDA_QUADRADO)

    # Desenhar a Bola
    # pygame.draw.circle(surface, color, center_point, radius)
    pygame.draw.circle(TELA, cor_bola, (int(posicao_bola.x), int(posicao_bola.y)), RAIO_BOLA)

    pygame.display.flip() # Atualiza a tela inteira para mostrar o que foi desenhado

# Finalização do Pygame
pygame.quit()
