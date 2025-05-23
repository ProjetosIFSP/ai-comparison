import pygame
import pymunk
import pymunk.pygame_util
import random
import math

# Inicialização do Pygame
pygame.init()
largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Quadrado Rotativo com Bola")
relogio = pygame.time.Clock()

# Inicialização do Pymunk
espaco = pymunk.Space()
espaco.gravity = (0, -900)  # Gravidade para baixo no sistema padrão Y↑

# Utilitário para desenhar com Pygame
desenho_pymunk = pymunk.pygame_util.DrawOptions(tela)

# =======================
# Parâmetros do Quadrado
# =======================
lado_quadrado = 200
angulo_rotacao = 0  # Ângulo em graus
velocidade_angular = 60  # graus por segundo

# Criação do quadrado como 4 segmentos
def criar_quadrado_rotativo():
    centro = (largura // 2, altura // 2)
    corpo = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    corpo.position = centro
    formas = []

    for i in range(4):
        a = i * math.pi / 2
        b = (i + 1) * math.pi / 2
        x1, y1 = math.cos(a) * lado_quadrado / 2, math.sin(a) * lado_quadrado / 2
        x2, y2 = math.cos(b) * lado_quadrado / 2, math.sin(b) * lado_quadrado / 2
        segmento = pymunk.Segment(corpo, (x1, y1), (x2, y2), 2)
        segmento.elasticity = 1.0
        segmento.color = pygame.Color('white')
        formas.append(segmento)

    # Adicione o corpo e todos os segmentos ao mesmo tempo
    espaco.add(corpo, *formas)
    return corpo, formas

corpo_quadrado, lados_quadrado = criar_quadrado_rotativo()

# =====================
# Criação da Bola
# =====================
def criar_bola():
    raio = 10
    massa = 1
    inercia = pymunk.moment_for_circle(massa, 0, raio)
    corpo = pymunk.Body(massa, inercia)
    corpo.position = largura // 2, altura // 2
    forma = pymunk.Circle(corpo, raio)
    forma.elasticity = 1.0
    forma.cor = pygame.Color('#FF0000')  # Vermelho puro
    espaco.add(corpo, forma)
    return corpo, forma

corpo_bola, forma_bola = criar_bola()

# ============================
# Colisão: troca de cor
# ============================
def cor_aleatoria():
    return pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def callback_colisao(arbiter, space, data):
    forma_bola.cor = cor_aleatoria()
    return True  # Permite resposta física normal

handler = espaco.add_default_collision_handler()
handler.begin = callback_colisao

# ============================
# Loop principal do jogo
# ============================
rodando = True
while rodando:
    dt = relogio.tick(60) / 1000.0  # Tempo por frame
    tela.fill((0, 0, 0))  # Fundo preto

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Atualizar rotação do quadrado
    angulo_rotacao += math.radians(velocidade_angular) * dt
    corpo_quadrado.angle = angulo_rotacao

    # Passo da simulação física
    espaco.step(dt)

    # Desenhar as formas com Pygame
    espaco.debug_draw(desenho_pymunk)

    # Desenhar a bola com a cor atual
    pos_bola = int(corpo_bola.position.x), altura - int(corpo_bola.position.y)
    pygame.draw.circle(tela, forma_bola.cor, pos_bola, int(forma_bola.radius))

    pygame.display.flip()

pygame.quit()
