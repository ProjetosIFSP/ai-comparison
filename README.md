### Prompt

Crie um programa detalhado para um jogo simples em 2D. O jogo se passa com um quadrado fixo posicionado no centro da tela, girando continuamente e infinitamente em torno de seu próprio centro. Inicialmente, uma bola é criada exatamente no centro deste quadrado. A bola é afetada pela força da gravidade, puxando-a para baixo (considerando um sistema de coordenadas padrão onde o eixo Y positivo é para cima).

Use Pygame (ou pygame + pymunk) para gráficos e física do jogo
Garanta movimentos suaves
O algoritmo deve descrever os seguintes aspectos:

Inicialização:
Quadrado: O quadrado está fixo no centro da tela e fica girando. Tem bordas de 2px brancas e tem lado de 200px com sua velocidade angular constante de 60 graus por segundo.
Bola: A bola é criada inicialmente no centro exato do quadrado, sua velocidade inicial é zero e sofre a aceleração da gravidade. A cor inicial dessa bola é vermelha pura (#FF0000).
Detecção de Colisão: Ao detectar a colisão da bola em um lado do quadrado, a bola deve quicar e trocar para uma cor aleatória. A trajetória da bola deve ser refletida de forma realista em relação à normal da superfície da colisão no instante exato da colisão.

Instruções adicionais: Priorize a clareza e a lógica do algoritmo. Você pode utilizar conceitos de física vetorial básica para descrever o movimento e a reflexão.
