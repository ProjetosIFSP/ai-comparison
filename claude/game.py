import pygame
import sys
import math
import random

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Quadrado e Bola")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)

# Configurações do jogo
FPS = 60
clock = pygame.time.Clock()

# Classe do Quadrado
class Quadrado:
    def __init__(self, x, y, lado):
        self.x = x
        self.y = y
        self.lado = lado
        self.angulo = 0
        self.velocidade_angular = 60  # 60 graus por segundo
        self.espessura = 2
        
        # Criando os vértices do quadrado (no estado inicial, sem rotação)
        self.vertices_originais = [
            [-lado/2, -lado/2],  # Superior esquerdo
            [lado/2, -lado/2],   # Superior direito
            [lado/2, lado/2],    # Inferior direito
            [-lado/2, lado/2]    # Inferior esquerdo
        ]
        
        # Inicializando os vértices atuais (serão atualizados durante a rotação)
        self.vertices_atuais = list(self.vertices_originais)
        
    def atualizar(self, dt):
        # Atualiza o ângulo de rotação
        self.angulo += self.velocidade_angular * dt
        self.angulo %= 360  # Mantém o ângulo entre 0 e 360 graus
        
        # Atualiza a posição dos vértices com base na rotação
        angulo_rad = math.radians(self.angulo)
        for i, (vx, vy) in enumerate(self.vertices_originais):
            # Aplica a matriz de rotação
            x_rotacionado = vx * math.cos(angulo_rad) - vy * math.sin(angulo_rad)
            y_rotacionado = vx * math.sin(angulo_rad) + vy * math.cos(angulo_rad)
            
            # Atualiza o vértice com a posição rotacionada + a posição central do quadrado
            self.vertices_atuais[i] = [self.x + x_rotacionado, self.y + y_rotacionado]
    
    def desenhar(self, surface):
        # Desenha as linhas do quadrado conectando os vértices
        for i in range(4):
            inicio = (int(self.vertices_atuais[i][0]), int(self.vertices_atuais[i][1]))
            fim = (int(self.vertices_atuais[(i+1)%4][0]), int(self.vertices_atuais[(i+1)%4][1]))
            pygame.draw.line(surface, BRANCO, inicio, fim, self.espessura)
    
    def obter_lados(self):
        # Retorna os 4 lados do quadrado como segmentos de reta (para detecção de colisão)
        lados = []
        for i in range(4):
            p1 = self.vertices_atuais[i]
            p2 = self.vertices_atuais[(i+1)%4]
            lados.append((p1, p2))
        return lados

# Classe da Bola
class Bola:
    def __init__(self, x, y, raio):
        self.x = x
        self.y = y
        self.raio = raio
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.gravidade = 0.5  # Aceleração devido à gravidade (pixels/segundo²)
        self.cor = VERMELHO
        self.amortecimento = 0.8  # Fator de amortecimento para colisões
    
    def atualizar(self, dt):
        # Aplica a gravidade
        self.velocidade_y += self.gravidade * dt
        
        # Atualiza a posição com base na velocidade
        self.x += self.velocidade_x * dt
        self.y += self.velocidade_y * dt
        
        # Colisão com as bordas da tela (opcional, para evitar que a bola saia da tela)
        if self.x - self.raio < 0:
            self.x = self.raio
            self.velocidade_x *= -self.amortecimento
        elif self.x + self.raio > WIDTH:
            self.x = WIDTH - self.raio
            self.velocidade_x *= -self.amortecimento
        
        if self.y - self.raio < 0:
            self.y = self.raio
            self.velocidade_y *= -self.amortecimento
        elif self.y + self.raio > HEIGHT:
            self.y = HEIGHT - self.raio
            self.velocidade_y *= -self.amortecimento
    
    def desenhar(self, surface):
        pygame.draw.circle(surface, self.cor, (int(self.x), int(self.y)), self.raio)
    
    def trocar_cor_aleatoria(self):
        # Gera uma cor aleatória (evitando cores muito escuras)
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        self.cor = (r, g, b)

# Função para calcular a distância de um ponto a uma linha (segmento de reta)
def distancia_ponto_segmento(ponto, segmento):
    x, y = ponto
    (x1, y1), (x2, y2) = segmento
    
    # Encontra o ponto mais próximo na linha
    A = x - x1
    B = y - y1
    C = x2 - x1
    D = y2 - y1
    
    dot = A * C + B * D
    len_sq = C * C + D * D
    
    # Evita divisão por zero para segmentos muito pequenos
    if len_sq == 0:
        return math.sqrt((x - x1)**2 + (y - y1)**2)
    
    param = dot / len_sq
    
    # Encontra o ponto mais próximo no segmento de reta
    if param < 0:
        xx = x1
        yy = y1
    elif param > 1:
        xx = x2
        yy = y2
    else:
        xx = x1 + param * C
        yy = y1 + param * D
    
    # Calcula a distância ao ponto mais próximo
    return math.sqrt((x - xx)**2 + (y - yy)**2)

# Função para calcular a normal de um segmento de reta
def calcular_normal(segmento):
    (x1, y1), (x2, y2) = segmento
    dx = x2 - x1
    dy = y2 - y1
    
    # Normal para fora (assumindo sentido anti-horário dos vértices)
    nx = -dy
    ny = dx
    
    # Normaliza a normal
    comprimento = math.sqrt(nx**2 + ny**2)
    if comprimento > 0:
        nx /= comprimento
        ny /= comprimento
    
    return nx, ny

# Função para verificar e processar colisões entre a bola e o quadrado
def verificar_colisao(bola, quadrado):
    lados = quadrado.obter_lados()
    
    # Verifica colisão com cada lado do quadrado
    for lado in lados:
        distancia = distancia_ponto_segmento((bola.x, bola.y), lado)
        
        # Se a distância é menor que o raio da bola, houve colisão
        if distancia <= bola.raio:
            # Calcula a normal da superfície
            nx, ny = calcular_normal(lado)
            
            # Verifica se a bola está se movendo em direção à superfície
            velocidade_dot_normal = (bola.velocidade_x * nx + bola.velocidade_y * ny)
            if velocidade_dot_normal > 0:
                # Se a bola está se afastando da superfície, não reflete
                continue
            
            # Calcula a reflexão (componente normal é invertida, tangencial mantida)
            vx_novo = bola.velocidade_x - 2 * velocidade_dot_normal * nx
            vy_novo = bola.velocidade_y - 2 * velocidade_dot_normal * ny
            
            # Aplica o amortecimento e atualiza a velocidade
            bola.velocidade_x = vx_novo * bola.amortecimento
            bola.velocidade_y = vy_novo * bola.amortecimento
            
            # Afasta ligeiramente a bola da superfície para evitar colisões múltiplas
            ajuste = bola.raio - distancia + 0.1
            bola.x += nx * ajuste
            bola.y += ny * ajuste
            
            # Troca a cor da bola
            bola.trocar_cor_aleatoria()
            
            # Para evitar múltiplas colisões em um único frame, saímos após detectar a primeira
            break

# Configurações iniciais dos objetos
lado_quadrado = 200
centro_x, centro_y = WIDTH // 2, HEIGHT // 2
quadrado = Quadrado(centro_x, centro_y, lado_quadrado)
bola = Bola(centro_x, centro_y, 15)  # Bola com raio de 15 pixels

# Loop principal do jogo
running = True
while running:
    # Calcula o tempo decorrido desde o último frame
    dt = clock.tick(FPS) / 1000.0  # Converte para segundos
    
    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Atualiza o quadrado
    quadrado.atualizar(dt)
    
    # Atualiza a bola
    bola.atualizar(dt)
    
    # Verifica colisões
    verificar_colisao(bola, quadrado)
    
    # Limpa a tela
    screen.fill(PRETO)
    
    # Desenha os objetos
    quadrado.desenhar(screen)
    bola.desenhar(screen)
    
    # Atualiza a tela
    pygame.display.flip()

# Encerra o Pygame
pygame.quit()
sys.exit()
