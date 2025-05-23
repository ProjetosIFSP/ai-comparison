import pygame
import pymunk
import pymunk.pygame_util
import random
import math
import imageio
import os
import cv2

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bola no Quadrado Giratório")

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Configurações do quadrado
SQUARE_SIZE = 200
SQUARE_ROTATION_SPEED = 60  # graus por segundo
SQUARE_BORDER = 2

# Configurações da bola
BALL_RADIUS = 15
GRAVITY = 981  # pixels/s²

# Espaço de física Pymunk
space = pymunk.Space()
space.gravity = (0, GRAVITY)  # Gravidade para baixo

def create_rotating_square():
    # Criamos um corpo estático (não afetado por física)
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = (WIDTH//2, HEIGHT//2)
    
    # Primeiro adicionamos o corpo ao espaço
    space.add(body)
    
    # Criamos os segmentos (lados) do quadrado
    half_size = SQUARE_SIZE // 2
    vertices = [
        (-half_size, -half_size),
        (half_size, -half_size),
        (half_size, half_size),
        (-half_size, half_size)
    ]
    
    # Criamos os segmentos de colisão
    segments = []
    for i in range(4):
        start = vertices[i]
        end = vertices[(i+1)%4]
        segment = pymunk.Segment(body, start, end, SQUARE_BORDER)
        segment.elasticity = 0.8  # Coeficiente de restituição
        segment.friction = 0.5
        segments.append(segment)
        space.add(segment)  # Adicionamos cada segmento ao espaço
    
    return body, segments

def create_ball():
    # Corpo dinâmico (afetado por física)
    mass = 1
    moment = pymunk.moment_for_circle(mass, 0, BALL_RADIUS)
    body = pymunk.Body(mass, moment)
    body.position = (WIDTH//2, HEIGHT//2)
    
    # Forma da bola
    shape = pymunk.Circle(body, BALL_RADIUS)
    shape.elasticity = 0.8  # Coeficiente de restituição
    shape.friction = 0.5
    shape.color = RED
    
    # Adicionamos ao espaço (corpo e shape juntos)
    space.add(body, shape)
    
    return body, shape

def update_square_rotation(square_body, dt):
    # Convertemos graus para radianos e atualizamos o ângulo
    angle_rad = math.radians(SQUARE_ROTATION_SPEED * dt)
    square_body.angle += angle_rad

def handle_collision(arbiter, space, data):
    ball_shape = data["ball_shape"]
    # Gerar uma nova cor aleatória
    ball_shape.color = (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255)
    )
    return True

def setup_collision_handler(ball_shape):
    handler = space.add_default_collision_handler()
    handler.post_solve = handle_collision
    handler.data["ball_shape"] = ball_shape

# Configurações para gravação de vídeo
video_nome = "gameplay_deepseek.mp4"
gif_nome = "gameplay_deepseek.gif"
quadro_tamanho = (WIDTH, HEIGHT)
fps = 30
quadro_codificador = cv2.VideoWriter_fourcc(*"mp4v")
video_writer = cv2.VideoWriter(video_nome, quadro_codificador, fps, quadro_tamanho)

# Função para converter MP4 para GIF
def converter_para_gif(video_path, gif_path):
    comando = f"ffmpeg -i {video_path} -vf 'fps=10,scale=320:-1:flags=lanczos' {gif_path}"
    os.system(comando)

def main():
    clock = pygame.time.Clock()
    running = True
    
    # Criamos os objetos do jogo
    square_body, square_segments = create_rotating_square()
    ball_body, ball_shape = create_ball()
    
    # Configuramos o handler de colisão
    setup_collision_handler(ball_shape)
    
    # Para gravação
    frames = []
    
    while running:
        dt = 1/60.0  # Tempo fixo para física estável
        
        # Processamento de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # Reset com R
                    space.remove(ball_body, ball_shape)
                    ball_body, ball_shape = create_ball()
                    setup_collision_handler(ball_shape)
                elif event.key == pygame.K_g:  # Gravar vídeo
                    # Iniciar gravação
                    frames = []
                    print("Gravação iniciada...")
                elif event.key == pygame.K_s:  # Parar gravação e salvar
                    # Parar gravação
                    print("Gravação parada. Salvando vídeo...")
                    # Salvar como MP4
                    imageio.mimsave('gravacao.mp4', frames, fps=60)
                    # Converter para GIF
                    imageio.mimsave('gravacao.gif', frames, fps=60)
                    print("Vídeo salvo como 'gravacao.mp4' e 'gravacao.gif'")
        
        # Atualização do quadrado
        update_square_rotation(square_body, dt)
        
        # Atualização da física
        space.step(dt)
        
        # Desenho
        screen.fill(BLACK)
        
        # Desenhamos o quadrado (manualmente para rotação suave)
        angle = square_body.angle
        half_size = SQUARE_SIZE // 2
        points = [
            (WIDTH//2 + half_size * math.cos(angle) - half_size * math.sin(angle),
             HEIGHT//2 + half_size * math.sin(angle) + half_size * math.cos(angle)),
            (WIDTH//2 + half_size * math.cos(angle) + half_size * math.sin(angle),
             HEIGHT//2 + half_size * math.sin(angle) - half_size * math.cos(angle)),
            (WIDTH//2 - half_size * math.cos(angle) + half_size * math.sin(angle),
             HEIGHT//2 - half_size * math.sin(angle) - half_size * math.cos(angle)),
            (WIDTH//2 - half_size * math.cos(angle) - half_size * math.sin(angle),
             HEIGHT//2 - half_size * math.sin(angle) + half_size * math.cos(angle))
        ]
        pygame.draw.polygon(screen, WHITE, points, SQUARE_BORDER)
        
        # Desenhamos a bola
        ball_pos = int(ball_body.position.x), int(ball_body.position.y)
        pygame.draw.circle(screen, ball_shape.color, ball_pos, BALL_RADIUS)
        
        # Gravação de vídeo
        frame = pygame.surfarray.array3d(pygame.display.get_surface())
        frame = cv2.cvtColor(cv2.transpose(frame), cv2.COLOR_RGB2BGR)
        video_writer.write(frame)
        
        # Atualização da tela
        pygame.display.flip()
        clock.tick(60)
    
    # Certifique-se de que o gravador de vídeo seja liberado corretamente
    video_writer.release()
    # Verifica se o arquivo MP4 foi gerado antes de converter para GIF
    if os.path.exists(video_nome):
        converter_para_gif(video_nome, gif_nome)
    else:
        print(f"Erro: O arquivo {video_nome} não foi gerado corretamente.")

    pygame.quit()

if __name__ == "__main__":
    main()