# Procurando o Tesouro

Jogo 3D em um único arquivo Python para o Trabalho Prático 2 de Computação Gráfica. O menu de seleção de 2, 3 ou 4 jogadores é feito com **Tkinter**. A janela do jogo usa **PyOpenGL/FreeGLUT**; o panorama 360° é carregado com OpenCV e aplicado como textura em uma esfera, e a iluminação, os materiais, o z-buffer, a câmera polar e as primitivas 3D seguem os exemplos das aulas. Pygame é usado somente para repetir o MP3 de fundo.

## Arquivos

- `procurando_tesouro.py` — programa completo, em arquivo Python único.

- `fundo.jpeg` — imagem panorâmica 360° usada no cenário.

- `tambores.mp3` — música de fundo em repetição.

- `requirements.txt` — bibliotecas Python necessárias.

- `melhores_pontuacoes.json` — ranking local, atualizado ao concluir uma partida; começa vazio.

## Instalação e execução

Na pasta extraída do ZIP, instale as dependências Python e execute:

```bash
python -m pip install -r requirements.txt
python procurando_tesouro.py
```

O Tkinter normalmente já vem com o Python. Em algumas distribuições Linux, pode ser necessário instalar os componentes nativos antes de rodar:

```bash
sudo apt install python3-tk freeglut3-dev
```

É necessário ter uma saída de áudio disponível para ouvir a música. Se a inicialização de áudio falhar, o jogo ainda abre sem a trilha sonora.

## Como jogar

No menu, escolha a quantidade de participantes e o nível de dificuldade. Cada avatar começa em uma borda diferente do tabuleiro 6×6. Na sua vez, clique diretamente em uma casa adjacente ou use as setas/WASD. Mais de um jogador pode ocupar a mesma casa; quando isso ocorre, os avatares são reduzidos e posicionados lado a lado para não se sobreporem. Não há limite de jogadas: a partida só termina quando todas as 36 casas forem exploradas; casas e eventos descobertos ficam marcados, e cada prêmio é concedido uma única vez.

Diamantes dão de 1 a 10 quilates; pistas dão +3; ao sair de um túnel sem saída o jogador perde 10; o esconderijo deixa o jogador invisível até sua próxima vez e tira 5 pontos de cada oponente. A dificuldade altera a quantidade de pistas, túneis e esconderijos. Ao revelar a 18ª casa, a cena entra em modo noturno: o panorama escurece e a iluminação do tabuleiro muda. Um aviso colorido identifica diamantes, pistas, armadilhas e esconderijos; o ranking aparece durante a partida e o resultado final informa o vencedor ou declara empate quando há pontuação máxima igual.

- **Setas e WASD:** mover para frente/trás/esquerda/direita conforme a visão atual da câmera; a orientação se ajusta ao lado de cada jogador.

- **Botão esquerdo do mouse:** clicar na casa adjacente para mover até ela.

- **Câmera e panorama:** a câmera começa alinhada à borda do primeiro jogador e gira no mesmo sentido a cada troca; o panorama tem orientação horizontal corrigida e rotação de 90° no eixo vertical.

- **Melhores pontuações:** ao fim de uma partida, os resultados são gravados; o arquivo local e o menu guardam/mostram somente as três maiores pontuações.

- **Dificuldade:** Fácil (mais pistas e menos armadilhas), Normal ou Difícil (menos pistas e mais armadilhas).

- **R:** iniciar uma nova partida com o mesmo número de jogadores.

- **Esc:** sair do jogo (inclusive no Linux).

## Dependências

O menu usa Tkinter, incluído na biblioteca padrão do Python. O jogo usa as bibliotecas ensinadas nas aulas para OpenGL/textura/iluminação; Pygame é adicionado somente para reproduzir o MP3 em loop.