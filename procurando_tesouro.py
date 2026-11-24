import os
import sys


if sys.platform.startswith('linux'):
    os.environ['PYOPENGL_PLATFORM'] = 'glx'



import os, sys, random, json, time, tkinter as tk
import cv2, pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_RECORDES = os.path.join(PASTA, 'melhores_pontuacoes.json')
LADO = 6
LARGURA, ALTURA = 1280, 800
CORES = [(0.12, 0.72, 1.0), (1.0, 0.25, 0.16), (0.22, 0.9, 0.43), (1.0, 0.67, 0.12)]
NOMES = ['AZUL', 'RUBI', 'VERDE', 'OURO']
textura = quad = None
estado, quantidade, casas, jogadores = 'jogo', 2, [], []
vez, turnos, mensagem = 0, 0, ''
aviso, cor_aviso = 'EXPLORE A MINA', (0.05, 0.28, 0.38)
camera_azimute, alvo_azimute = 45.0, 45.0
sentido_camera = 1
dificuldade = 'Normal'
camera_inclinacao, distancia = 68.0, 9.5
MOVIMENTOS_VISTA = {
    0: {b'w':(-1,0), b's':(1,0), b'a':(0,-1), b'd':(0,1), GLUT_KEY_UP:(-1,0), GLUT_KEY_DOWN:(1,0), GLUT_KEY_LEFT:(0,-1), GLUT_KEY_RIGHT:(0,1)},
    90: {b'w':(0,-1), b's':(0,1), b'a':(1,0), b'd':(-1,0), GLUT_KEY_UP:(0,-1), GLUT_KEY_DOWN:(0,1), GLUT_KEY_LEFT:(1,0), GLUT_KEY_RIGHT:(-1,0)},
    180: {b'w':(1,0), b's':(-1,0), b'a':(0,1), b'd':(0,-1), GLUT_KEY_UP:(1,0), GLUT_KEY_DOWN:(-1,0), GLUT_KEY_LEFT:(0,1), GLUT_KEY_RIGHT:(0,-1)},
    270: {b'w':(0,1), b's':(0,-1), b'a':(-1,0), b'd':(1,0), GLUT_KEY_UP:(0,1), GLUT_KEY_DOWN:(0,-1), GLUT_KEY_LEFT:(-1,0), GLUT_KEY_RIGHT:(1,0)}}



def carrega_recordes():
    try:
        with open(ARQUIVO_RECORDES, encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, list):
            return []
        return sorted((r for r in dados if isinstance(r, dict) and isinstance(r.get('pontos'), int)),
                      key=lambda r: r['pontos'], reverse=True)[:3]
    except (OSError, ValueError, TypeError):
        return []



def registra_recordes():
    recordes = carrega_recordes()
    recordes.extend({'nome': p['nome'], 'pontos': p['pontos'], 'jogadores': quantidade,
                     'dificuldade': dificuldade, 'data': time.strftime('%d/%m/%Y')} for p in jogadores)
    recordes.sort(key=lambda r: r['pontos'], reverse=True)
    try:
        with open(ARQUIVO_RECORDES, 'w', encoding='utf-8') as arquivo:
            json.dump(recordes[:3], arquivo, ensure_ascii=False, indent=2)
    except OSError as erro:
        print('Nao foi possivel salvar as melhores pontuacoes:', erro)



def conta_casas():
    return sum(casa['revelada'] for linha in casas for casa in linha)



def menu_tkinter():
    global quantidade, dificuldade
    janela = tk.Tk()
    janela.title('Procurando o Tesouro')
    janela.geometry('580x1080')
    janela.resizable(False, False)
    janela.configure(bg='#101923')
    escolha = tk.IntVar(value=2)
    iniciou = [False]
    botoes = []
    tk.Label(janela, text='PROCURANDO O TESOURO', bg='#101923', fg='#f2c46d',
             font=('Arial', 23, 'bold')).pack(pady=(22, 5))
    tk.Label(janela, text='Uma expedicao 3D pela mina', bg='#101923', fg='#aebdca',
             font=('Arial', 12)).pack(pady=(0, 18))
    tk.Label(janela, text='QUANTOS JOGADORES?', bg='#101923', fg='#72d7df',
             font=('Arial', 11, 'bold')).pack(pady=(4, 13))
    linha = tk.Frame(janela, bg='#101923')
    linha.pack()


    def atualiza_botoes():
        for n, botao in botoes:
            botao.configure(bg='#256c72' if escolha.get() == n else '#263747')

    for n in (2, 3, 4):
        botao = tk.Button(linha, text=f'{n} jogadores', width=13, height=2,
                          font=('Arial', 11, 'bold'), fg='white', relief='flat',
                          command=lambda valor=n: (escolha.set(valor), atualiza_botoes()))
        botao.pack(side='left', padx=7)
        botoes.append((n, botao))
    atualiza_botoes()

    tk.Label(janela, text='NIVEL DE DIFICULDADE', bg='#101923', fg='#72d7df',
             font=('Arial', 11, 'bold')).pack(pady=(18, 8))
    nivel = tk.StringVar(value=dificuldade)
    linha_nivel = tk.Frame(janela, bg='#101923'); linha_nivel.pack()
    botoes_nivel = []


    def atualiza_niveis():
        for nome, botao in botoes_nivel:
            botao.configure(bg='#256c72' if nivel.get() == nome else '#263747')

    for nome in ('Fácil', 'Normal', 'Difícil'):
        botao = tk.Button(linha_nivel, text=nome, width=13, height=1, fg='white',
                          font=('Arial', 10, 'bold'), relief='flat',
                          command=lambda valor=nome: (nivel.set(valor), atualiza_niveis()))
        botao.pack(side='left', padx=7); botoes_nivel.append((nome, botao))
    atualiza_niveis()
    tk.Label(janela, text='Fácil: 3 pistas/1 túnel/1 esconderijo | Normal: 2 de cada | Difícil: 1/4/3',
             bg='#101923', fg='#9aabb8', font=('Arial', 9)).pack(pady=(5, 0))

    caixa = tk.Frame(janela, bg='#192735', padx=24, pady=18)
    caixa.pack(fill='x', padx=42, pady=18)
    tk.Label(caixa, text='COMO JOGAR', bg='#192735', fg='#f2c46d',
             font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 8))
    regras = ('Explore o tabuleiro 6 x 6, casa por casa.\n'
              'Diamantes valem de 1 a 10 quilates; pistas dao +3.\n'
              'Cuidado com tuneis e esconderijos!\n'
              'A partida termina quando todas as casas forem exploradas.')
    tk.Label(caixa, text=regras, bg='#192735', fg='#d5dee5', justify='left',
             font=('Arial', 10), pady=7).pack(anchor='w')
    painel_recordes = tk.Frame(janela, bg='#192735', padx=20, pady=13)
    painel_recordes.pack(fill='x', padx=42, pady=(0, 18))
    tk.Label(painel_recordes, text='MELHORES PONTUACOES', bg='#192735', fg='#72d7df',
             font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 7))
    recordes = carrega_recordes()
    if recordes:
        for i, registro in enumerate(recordes[:3]):
            linha_recorde = f"{i + 1}. {registro['nome']}: {registro['pontos']} q  |  {registro.get('dificuldade', 'Normal')}"
            tk.Label(painel_recordes, text=linha_recorde, bg='#192735', fg='#d5dee5',
                     font=('Arial', 10)).pack(anchor='w', pady=1)
    else:
        tk.Label(painel_recordes, text='As melhores partidas aparecerao aqui.',
                 bg='#192735', fg='#aebdca', font=('Arial', 10)).pack(anchor='w')
    tk.Label(janela, text='Setas e WASD acompanham a camera.',
             bg='#101923', fg='#9aabb8', font=('Arial', 9)).pack(pady=(0, 18))


    def iniciar():
        global quantidade, dificuldade
        quantidade = escolha.get()
        dificuldade = nivel.get()
        iniciou[0] = True
        janela.destroy()

    tk.Button(janela, text='INICIAR EXPLORACAO', command=iniciar,
              bg='#bd7d2d', activebackground='#d79742', fg='white',
              activeforeground='white', font=('Arial', 13, 'bold'),
              relief='flat', padx=28, pady=12).pack()
    janela.bind('<Escape>', lambda evento: janela.destroy())
    janela.mainloop()
    return iniciou[0]



def cria_textura():
    global textura
    imagem = cv2.imread(os.path.join(PASTA, 'fundo.jpeg'))
    if imagem is None:
        raise FileNotFoundError('Nao encontrei fundo.jpeg na pasta do jogo.')
    imagem = cv2.flip(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB), -1)
    altura, largura, _ = imagem.shape
    textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textura)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, largura, altura, 0, GL_RGB, GL_UNSIGNED_BYTE, imagem.tobytes())



def polar_view():
    glTranslatef(0, 0, -distancia)
    glRotatef(-camera_inclinacao, 1, 0, 0)
    glRotatef(-camera_azimute, 0, 0, 1)



def desenha_fundo():
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textura)
    glColor3f(0.40, 0.48, 0.70) if conta_casas() >= LADO * LADO // 2 else glColor3f(1, 1, 1)
    glDepthMask(GL_FALSE)
    glPushMatrix(); glRotatef(90, 0, 0, 1)
    gluSphere(quad, 70, 36, 24)
    glPopMatrix()
    glDepthMask(GL_TRUE)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)



def cor(rgb, brilho=35):
    glColor3f(*rgb)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.45, 0.45, 0.45, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, brilho)



def esfera(x, y, z, escala, rgb, brilho=35):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(*escala)
    cor(rgb, brilho)
    glutSolidSphere(0.5, 16, 12)
    glPopMatrix()



def posicao_casa(linha, coluna):
    return coluna - 2.5, 2.5 - linha



def desenha_minerador(jogador, deslocamento=(0, 0), escala=1):
    if jogador['invisivel']:
        return
    x, y = posicao_casa(*jogador['posicao'])
    glPushMatrix()
    glTranslatef(x + deslocamento[0], y + deslocamento[1], 0.23)
    glScalef(escala, escala, escala)
    roupa = jogador['cor']

    esfera(0, 0, 0.26, (0.34, 0.25, 0.42), roupa)
    esfera(-0.19, 0, 0.08, (0.13, 0.13, 0.20), (0.12, 0.10, 0.09))
    esfera(0.19, 0, 0.08, (0.13, 0.13, 0.20), (0.12, 0.10, 0.09))
    esfera(-0.23, 0, 0.36, (0.12, 0.13, 0.27), roupa)
    esfera(0.23, 0, 0.36, (0.12, 0.13, 0.27), roupa)
    esfera(0, 0, 0.58, (0.25, 0.23, 0.25), (0.94, 0.68, 0.46))
    esfera(0, 0, 0.72, (0.29, 0.27, 0.12), (1.0, 0.68, 0.12), 80)
    glPopMatrix()



def desenha_item(linha, coluna, casa):
    if not casa['revelada'] or casa['tipo'] == 'inicio':
        return
    x, y = posicao_casa(linha, coluna)
    x, y = x + 0.23, y - 0.23
    glPushMatrix(); glTranslatef(x, y, 0.205)
    tipo = casa['tipo']
    if tipo == 'diamante':
        cor((0.15, 0.92, 1.0) if not casa['coletado'] else (0.42, 0.67, 0.72), 110)
        glTranslatef(0, 0, 0.26); glRotatef(45, 0, 0, 1); glScalef(0.19, 0.19, 0.27)
        glutSolidOctahedron()
    elif tipo == 'pista':
        cor((0.25, 0.9, 0.45), 55)
        glPushMatrix(); glTranslatef(0, 0, 0.27); glScalef(0.07, 0.07, 0.54)
        glutSolidCube(1); glPopMatrix()
        glTranslatef(0, 0, 0.52); glScalef(0.39, 0.07, 0.23); glutSolidCube(1)
    elif tipo == 'tunel':
        cor((0.70, 0.17, 0.09), 65); glTranslatef(0, 0, 0.065)
        glutSolidTorus(0.065, 0.19, 12, 20)
        cor((0.035, 0.025, 0.04), 8); glTranslatef(0, 0, -0.045)
        glutSolidSphere(0.10, 14, 10)
    elif tipo == 'esconderijo':
        cor((0.72, 0.3, 0.95), 65)
        glutSolidCone(0.21, 0.38, 12, 5)
    glPopMatrix()



def desenha_tabuleiro():

    glPushMatrix(); glTranslatef(0, 0, -0.18); glScalef(6.6, 6.6, 0.34)
    cor((0.13, 0.12, 0.14), 20); glutSolidCube(1); glPopMatrix()
    cor((0.55, 0.34, 0.12), 65)
    for x, y, sx, sy in [(0, 3.25, 6.55, 0.12), (0, -3.25, 6.55, 0.12),
                         (3.25, 0, 0.12, 6.55), (-3.25, 0, 0.12, 6.55)]:
        glPushMatrix(); glTranslatef(x, y, 0.02); glScalef(sx, sy, 0.18)
        glutSolidCube(1); glPopMatrix()
    paleta = {'inicio': (0.12, 0.47, 0.55), 'diamante': (0.15, 0.49, 0.58),
              'pista': (0.15, 0.34, 0.22), 'tunel': (0.35, 0.17, 0.12),
              'esconderijo': (0.27, 0.16, 0.36)}
    for l in range(LADO):
        for c in range(LADO):
            casa = casas[l][c]
            x, y = posicao_casa(l, c)
            cor((0.53, 0.34, 0.15), 60)
            glPushMatrix(); glTranslatef(x, y, 0.035); glScalef(0.98, 0.98, 0.20)
            glutSolidCube(1); glPopMatrix()
            cor(paleta[casa['tipo']] if casa['revelada'] else
                ((0.18, 0.25, 0.31) if (l + c) % 2 else (0.22, 0.29, 0.34)), 38)
            glPushMatrix(); glTranslatef(x, y, 0.14); glScalef(0.84, 0.84, 0.12)
            glutSolidCube(1); glPopMatrix()
            desenha_item(l, c, casa)
    deslocamentos = [(-0.20, 0.18), (0.16, 0.18), (-0.20, -0.16), (0.16, -0.16)]
    for jogador in jogadores:
        grupo = [p for p in jogadores if p['posicao'] == jogador['posicao'] and not p['invisivel']]
        if jogador['invisivel']:
            continue
        indice = grupo.index(jogador)
        if len(grupo) > 1:
            desenha_minerador(jogador, deslocamentos[indice], 0.58)
        else:
            desenha_minerador(jogador)
    glDisable(GL_LIGHTING); glColor3f(0.43, 0.47, 0.47); glBegin(GL_LINES)
    for i in range(1, LADO):
        v = i - 3
        glVertex3f(-3, v, 0.205); glVertex3f(3, v, 0.205)
        glVertex3f(v, -3, 0.205); glVertex3f(v, 3, 0.205)
    glEnd(); glEnable(GL_LIGHTING)



def inicia_jogo(n):
    global quantidade, jogadores, casas, turnos, vez, estado, mensagem, aviso, cor_aviso
    global camera_azimute, alvo_azimute, sentido_camera
    quantidade, turnos, vez, estado = n, 0, 0, 'jogo'
    casas = [[{'tipo': 'diamante', 'quilates': random.randint(1, 10), 'revelada': False, 'coletado': False}
              for _ in range(LADO)] for _ in range(LADO)]

    lados = {2: [(0, 2), (5, 3)], 3: [(0, 2), (3, 0), (3, 5)],
             4: [(0, 2), (2, 5), (5, 3), (3, 0)]}

    angulos = {2: [180, 0], 3: [180, 270, 90], 4: [180, 90, 0, 270]}
    ocupadas = lados[n]
    for l, c in ocupadas:
        casas[l][c] = {'tipo': 'inicio', 'revelada': True, 'coletado': True}
    disponiveis = [(l, c) for l in range(LADO) for c in range(LADO) if (l, c) not in ocupadas]
    random.shuffle(disponiveis)
    quantidades = {'Fácil': (3, 1, 1), 'Normal': (2, 2, 2), 'Difícil': (1, 4, 3)}[dificuldade]
    especiais, inicio = [], 0
    for tipo, total in zip(('pista', 'tunel', 'esconderijo'), quantidades):
        especiais.extend((l, c, tipo) for l, c in disponiveis[inicio:inicio + total])
        inicio += total
    for l, c, tipo in especiais:
        casas[l][c] = {'tipo': tipo, 'revelada': False, 'coletado': False}
    jogadores = [{'nome': NOMES[i], 'cor': CORES[i], 'posicao': ocupadas[i], 'lado': angulos[n][i],
                  'pontos': 0, 'invisivel': False, 'tunel': False} for i in range(n)]
    sentido_camera = 1 if n in (2, 3) else -1
    camera_azimute = alvo_azimute = float(jogadores[0]['lado'])
    mensagem, aviso, cor_aviso = 'Sua vez: entre em uma casa vizinha.', 'PRONTO PARA EXPLORAR', (0.05, 0.28, 0.38)



def mover(dl, dc):
    global turnos, vez, estado, mensagem, aviso, cor_aviso, alvo_azimute
    if estado != 'jogo':
        return
    jogador = jogadores[vez]
    l, c = jogador['posicao']; nl, nc = l + dl, c + dc
    if not (0 <= nl < LADO and 0 <= nc < LADO):
        mensagem = 'A borda da mina bloqueia esse caminho.'
        aviso, cor_aviso = 'CAMINHO BLOQUEADO', (0.32, 0.18, 0.07)
        return
    saiu_tunel = jogador['tunel']
    if saiu_tunel:
        jogador['pontos'] -= 10
        jogador['tunel'] = False
    jogador['posicao'] = (nl, nc)
    casa = casas[nl][nc]
    if not casa['revelada']:
        casa['revelada'] = True
        tipo = casa['tipo']
        if tipo == 'diamante':
            jogador['pontos'] += casa['quilates']; casa['coletado'] = True
            mensagem = f"Diamante de {casa['quilates']} quilates!"
            aviso, cor_aviso = f"DIAMANTE +{casa['quilates']} QUILATES", (0.02, 0.34, 0.47)
        elif tipo == 'pista':
            jogador['pontos'] += 3; casa['coletado'] = True
            mensagem = 'Pista encontrada: +3 quilates.'
            aviso, cor_aviso = 'PISTA ENCONTRADA: +3 QUILATES', (0.06, 0.34, 0.16)
        elif tipo == 'tunel':
            jogador['tunel'] = True
            mensagem = 'Tunel sem saida: ao sair, voce perde 10 quilates.'
            aviso, cor_aviso = 'ARMADILHA: -10 AO SAIR DO TUNEL', (0.46, 0.09, 0.06)
        elif tipo == 'esconderijo':
            jogador['invisivel'] = True
            for outro in jogadores:
                if outro is not jogador:
                    outro['pontos'] -= 5
            casa['coletado'] = True
            mensagem = 'Esconderijo: invisivel e oponentes perdem 5.'
            aviso, cor_aviso = 'ESCONDERIJO: OPONENTES -5', (0.30, 0.08, 0.43)
    else:
        mensagem = 'Casa ja explorada; sem novo premio.'
        aviso, cor_aviso = 'CASA JA EXPLORADA', (0.17, 0.22, 0.28)
    if saiu_tunel:
        mensagem += ' Saida do tunel: -10.'
        aviso, cor_aviso = f'SAIU DO TUNEL: -10 | {aviso}', (0.46, 0.09, 0.06)
    turnos += 1
    if conta_casas() == LADO * LADO:
        estado = 'fim'
        maior = max(p['pontos'] for p in jogadores)
        lideres = [p for p in jogadores if p['pontos'] == maior]
        registra_recordes()
        if len(lideres) > 1:
            nomes = ', '.join(p['nome'] for p in lideres)
            mensagem = f"Empate! {nomes} terminaram com {maior} quilates."
            aviso, cor_aviso = 'EMPATE!', (0.28, 0.16, 0.43)
        else:
            mensagem = f"Fim da exploracao! Vencedor: {lideres[0]['nome']} ({maior} quilates)."
            aviso, cor_aviso = f"VENCEDOR: {lideres[0]['nome']}", (0.55, 0.32, 0.06)
        return
    vez = (vez + 1) % quantidade
    if jogadores[vez]['invisivel']:
        jogadores[vez]['invisivel'] = False
    proximo_angulo = float(jogadores[vez]['lado'])
    if sentido_camera > 0:
        while proximo_angulo <= alvo_azimute:
            proximo_angulo += 360
    else:
        while proximo_angulo >= alvo_azimute:
            proximo_angulo -= 360
    alvo_azimute = proximo_angulo



def retangulo(x, y, largura, altura, rgb, alfa=0.94):
    glColor4f(*rgb, alfa); glBegin(GL_QUADS)
    glVertex2f(x, y); glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura); glVertex2f(x, y + altura)
    glEnd()



def texto(x, y, frase, tamanho=18, rgb=(0.94, 0.94, 0.91), central=False):
    fonte = GLUT_BITMAP_HELVETICA_18 if tamanho >= 18 else GLUT_BITMAP_HELVETICA_12
    bytes_frase = frase.encode('latin1', 'replace')
    if central:
        x -= sum(glutBitmapWidth(fonte, b) for b in bytes_frase) / 2
    glColor3f(*rgb); glRasterPos2f(x, y)
    for letra in bytes_frase:
        glutBitmapCharacter(fonte, letra)



def inicio_overlay():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, LARGURA, 0, ALTURA)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING); glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)



def fim_overlay():
    glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)



def desenha_painel():
    exploradas = conta_casas()
    fase = 'NOITE' if exploradas >= LADO * LADO // 2 else 'DIA'
    inicio_overlay()
    retangulo(18, ALTURA - 205, 258, 184, (0.035, 0.055, 0.075), 0.86)
    texto(36, ALTURA - 52, 'PLACAR DA MINA', 18, (1.0, 0.76, 0.29))
    for i, jogador in enumerate(sorted(jogadores, key=lambda p: p['pontos'], reverse=True)):
        y = ALTURA - 83 - i * 27
        texto(38, y, f"{i + 1}. {jogador['nome']}: {jogador['pontos']} q", 18, jogador['cor'])
        if jogadores.index(jogador) == vez and estado == 'jogo':
            texto(227, y, '<', 18, (1, 1, 1))
    texto(36, ALTURA - 190, f'{exploradas}/36 casas | {turnos} turnos | {fase}', 12,
          (0.66, 0.78, 1.0) if fase == 'NOITE' else (0.78, 0.84, 0.86))
    retangulo(18, 20, min(660, LARGURA - 36), 43, (0.035, 0.055, 0.075), 0.88)
    texto(32, 35, mensagem[:76], 12, (0.96, 0.88, 0.66))
    largura_aviso = min(440, LARGURA - 36)
    retangulo((LARGURA - largura_aviso) / 2, ALTURA - 158, largura_aviso, 48, cor_aviso, 0.94)
    texto(LARGURA / 2, ALTURA - 138, aviso[:46], 18, (1, 1, 1), True)
    if estado == 'jogo':
        x_painel = max(18, LARGURA - 370)
        retangulo(x_painel, ALTURA - 96, 352, 76, (0.035, 0.055, 0.075), 0.88)
        texto(x_painel + 15, ALTURA - 48, f"VEZ: {jogadores[vez]['nome']}", 18, jogadores[vez]['cor'])
        texto(x_painel + 15, ALTURA - 75, 'Clique/setas | WASD camera | R reinicia | ESC sai', 12)
        if jogadores[vez]['invisivel']:
            texto(x_painel + 15, ALTURA - 90, 'MODO INVISIVEL', 12, (0.8, 0.55, 1.0))
    else:
        retangulo(LARGURA / 2 - 255, ALTURA / 2 - 105, 510, 210, (0.035, 0.055, 0.075), 0.95)
        texto(LARGURA / 2, ALTURA / 2 + 52, 'EXPEDICAO CONCLUIDA', 18, (1.0, 0.76, 0.29), True)
        texto(LARGURA / 2, ALTURA / 2 + 12, mensagem, 12, central=True)
        texto(LARGURA / 2, ALTURA / 2 - 38, 'R: nova partida       ESC: sair', 18, central=True)
    fim_overlay()



def desenha():
    fator = 0.52 if conta_casas() >= LADO * LADO // 2 else 1.0
    glClearColor(0.025 * fator, 0.035 * fator, 0.055 * fator, 1)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.28 * fator, 0.28 * fator, 0.28 * fator, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.95 * fator, 0.90 * fator, 0.80 * fator, 1))
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity(); polar_view()
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 10, 1))
    desenha_fundo(); desenha_tabuleiro(); desenha_painel()
    glutSwapBuffers()



def redimensiona(largura, altura):
    global LARGURA, ALTURA
    LARGURA, ALTURA = max(largura, 1), max(altura, 1)
    glViewport(0, 0, LARGURA, ALTURA)
    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(48, LARGURA / ALTURA, 0.5, 180)
    glMatrixMode(GL_MODELVIEW)



def mover_vista(tecla):
    mover(*MOVIMENTOS_VISTA[jogadores[vez]['lado']][tecla])



def teclado(tecla, x, y):
    if tecla == b'\x1b':
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)
        return
    if estado == 'fim':
        if tecla in (b'r', b'R'):
            inicia_jogo(quantidade)
    else:
        if tecla.lower() in (b'w', b'a', b's', b'd'):
            mover_vista(tecla.lower())
        elif tecla in (b'r', b'R'):
            inicia_jogo(quantidade)
    glutPostRedisplay()



def teclas_especiais(tecla, x, y):
    if tecla in MOVIMENTOS_VISTA[jogadores[vez]['lado']]:
        mover_vista(tecla); glutPostRedisplay()



def mouse(botao, situacao, x, y):
    if botao != GLUT_LEFT_BUTTON or situacao != GLUT_DOWN or estado != 'jogo':
        return

    modelo = glGetDoublev(GL_MODELVIEW_MATRIX)
    projecao = glGetDoublev(GL_PROJECTION_MATRIX)
    tela = glGetIntegerv(GL_VIEWPORT)
    perto = gluUnProject(x, ALTURA - y, 0, modelo, projecao, tela)
    longe = gluUnProject(x, ALTURA - y, 1, modelo, projecao, tela)
    if abs(longe[2] - perto[2]) < 1e-8:
        return
    t = (0.205 - perto[2]) / (longe[2] - perto[2])
    mundo_x = perto[0] + t * (longe[0] - perto[0])
    mundo_y = perto[1] + t * (longe[1] - perto[1])
    linha, coluna = round(2.5 - mundo_y), round(mundo_x + 2.5)
    if not (0 <= linha < LADO and 0 <= coluna < LADO):
        return
    atual_l, atual_c = jogadores[vez]['posicao']
    if abs(linha - atual_l) + abs(coluna - atual_c) == 1:
        mover(linha - atual_l, coluna - atual_c)
        glutPostRedisplay()



def atualiza_camera():
    global camera_azimute
    diferenca = alvo_azimute - camera_azimute
    if abs(diferenca) > 0.2:
        camera_azimute += diferenca * 0.09
        glutPostRedisplay()



def inicializa():
    global quad
    glClearColor(0.025, 0.035, 0.055, 1)
    glEnable(GL_DEPTH_TEST); glEnable(GL_NORMALIZE)
    glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.28, 0.28, 0.28, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.95, 0.90, 0.80, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
    glShadeModel(GL_SMOOTH)
    cria_textura()
    quad = gluNewQuadric(); gluQuadricTexture(quad, GL_TRUE)
    gluQuadricOrientation(quad, GLU_INSIDE)



def principal():
    os.chdir(PASTA)
    if not menu_tkinter():
        return
    inicia_jogo(quantidade)
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(PASTA, 'tambores.mp3'))
        pygame.mixer.music.play(-1)
    except Exception as erro:
        print('Audio indisponivel; instale pygame e confira a saida de som:', erro)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    try:
        glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    except Exception:
        pass
    glutInitWindowSize(LARGURA, ALTURA)
    glutCreateWindow(b'Procurando o Tesouro - Computacao Grafica')
    inicializa()
    glutDisplayFunc(desenha); glutReshapeFunc(redimensiona)
    glutKeyboardFunc(teclado); glutSpecialFunc(teclas_especiais); glutMouseFunc(mouse)
    glutIdleFunc(atualiza_camera)
    glutMainLoop()
    pygame.mixer.quit()


if __name__ == '__main__':
    principal()
