"""
Gerador da arte em pixel art do jogo "7 Hell's".

Todos os sprites, o fundo, a interface (UI) e a fonte pixelada sao gerados
por este script, a partir de formas simples + uma paleta fixa. Assim a arte
fica toda com o mesmo estilo e pode ser refeita/ajustada facilmente.

Como usar (na pasta raiz do projeto):
    python Tools/PixelArt/gerar_pixel_art.py

Depois abra a Unity: ela reimporta os PNGs automaticamente.
Requer: Python 3 + Pillow (pip install pillow).
"""

import math
import os
import random
import struct

from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ART = os.path.join(RAIZ, "Assets", "Art")
DOCS = os.path.join(RAIZ, "Docs")

# ---------------------------------------------------------------------------
# PALETA (todas as cores do jogo saem daqui)
# ---------------------------------------------------------------------------
T = (0, 0, 0, 0)  # transparente


def c(hexa, a=255):
    hexa = hexa.lstrip("#")
    return (int(hexa[0:2], 16), int(hexa[2:4], 16), int(hexa[4:6], 16), a)


PAL = {
    # contornos / sombras profundas
    "preto": c("1a0a12"),
    "noite": c("2d1020"),
    "vinho": c("461626"),
    # rocha vulcanica (basalto)
    "rocha0": c("2a1a24"),
    "rocha1": c("3e2834"),
    "rocha2": c("574050"),
    "rocha3": c("75586a"),
    "rocha4": c("9a7c88"),
    # lava / fogo
    "lava0": c("6e1018"),
    "lava1": c("b22418"),
    "lava2": c("ec5c20"),
    "lava3": c("ffa030"),
    "lava4": c("ffe27a"),
    # pele (Agenor)
    "pele0": c("7a4030"),
    "pele1": c("c47c58"),
    "pele2": c("eab080"),
    "pele3": c("ffd8a8"),
    # coracao / demonio
    "verm0": c("5c0c24"),
    "verm1": c("a01838"),
    "verm2": c("e0304c"),
    "verm3": c("ff7486"),
    # ouro (trofeu)
    "ouro0": c("6a3c10"),
    "ouro1": c("b07820"),
    "ouro2": c("eab83a"),
    "ouro3": c("fff0a0"),
    # enxofre (plataforma que some)
    "enx0": c("2c3410"),
    "enx1": c("566a1c"),
    "enx2": c("94ae30"),
    "enx3": c("d4e46a"),
    # claros
    "branco": c("f6f0e6"),
    "cinza": c("bcb4c0"),
    "creme": c("f4e6c8"),
}

RAMPAS = {
    "rocha": ["rocha0", "rocha1", "rocha2", "rocha3", "rocha4"],
    "pele": ["pele0", "pele1", "pele2", "pele3"],
    "verm": ["verm0", "verm1", "verm2", "verm3"],
    "ouro": ["ouro0", "ouro1", "ouro2", "ouro3"],
    "enx": ["enx0", "enx1", "enx2", "enx3"],
    "branco": ["cinza", "cinza", "branco", "branco"],
}


# ---------------------------------------------------------------------------
# Ferramentas de desenho
# ---------------------------------------------------------------------------
class Grade:
    """Grade de 'materiais' (nomes de rampa). Depois vira imagem com sombra + contorno."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.m = [[None] * w for _ in range(h)]
        self.detalhe = {}  # (x,y) -> cor fixa pintada por cima

    def dentro(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def ponto(self, x, y, mat):
        if self.dentro(x, y):
            self.m[y][x] = mat

    def ret(self, x0, y0, x1, y1, mat):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.ponto(x, y, mat)

    def elipse(self, cx, cy, rx, ry, mat):
        for y in range(self.h):
            for x in range(self.w):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    self.ponto(x, y, mat)

    def poligono(self, pts, mat):
        for y in range(self.h):
            for x in range(self.w):
                if dentro_poligono(x + 0.5, y + 0.5, pts):
                    self.ponto(x, y, mat)

    def pintar(self, x, y, cor):
        if self.dentro(x, y):
            self.detalhe[(x, y)] = PAL[cor] if isinstance(cor, str) else cor

    def imagem(self, contorno="preto", luz=(-1, -1)):
        """Converte em imagem: sombreamento pela direcao da luz + contorno escuro."""
        img = Image.new("RGBA", (self.w, self.h), T)
        lx, ly = luz
        for y in range(self.h):
            for x in range(self.w):
                mat = self.m[y][x]
                if mat is None:
                    continue
                rampa = RAMPAS[mat]
                n = len(rampa)
                nivel = n - 2  # tom base

                def vazio(dx, dy):
                    xx, yy = x + dx, y + dy
                    return not self.dentro(xx, yy) or self.m[yy][xx] != mat

                if vazio(lx, 0) or vazio(0, ly):
                    nivel = n - 1  # borda iluminada
                if vazio(-lx, 0) or vazio(0, -ly):
                    nivel = max(0, n - 3)  # borda na sombra
                if vazio(-lx, 0) and vazio(0, -ly):
                    nivel = max(0, n - 4)
                img.putpixel((x, y), PAL[rampa[nivel]])
        for (x, y), cor in self.detalhe.items():
            img.putpixel((x, y), cor)
        if contorno:
            img = contornar(img, PAL[contorno])
        return img


def dentro_poligono(px, py, pts):
    dentro = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi:
            dentro = not dentro
        j = i
    return dentro


def contornar(img, cor):
    """Pinta de 'cor' os pixels transparentes vizinhos (4 direcoes) de pixels opacos.
    Os pixels da borda da imagem que ja sao opacos tambem viram contorno."""
    w, h = img.size
    src = img.copy()
    px = src.load()
    out = img.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if not (0 <= xx < w and 0 <= yy < h):
                    out[x, y] = cor  # encostou na borda da imagem
    for y in range(h):
        for x in range(w):
            if px[x, y][3] != 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and px[xx, yy][3] != 0:
                    out[x, y] = cor
                    break
    return img


def esticar_linhas(img, fx, fy, w_final=None, h_final=None):
    """Amplia com 'nearest neighbor' (cada pixel vira um bloco). Usado quando o
    objeto na cena tem escala nao uniforme: o sprite e 'pre-distorcido' para os
    pixels aparecerem quadrados no jogo, sem mexer no Transform/colisor."""
    w = w_final or img.width * fx
    h = h_final or img.height * fy
    return img.resize((w, h), Image.NEAREST)


def salvar(img, *caminho):
    p = os.path.join(ART, *caminho)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    print("  ok", os.path.relpath(p, RAIZ))
    return img


BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dither(x, y, t):
    """True se o pixel deve usar a cor 'seguinte' (dithering ordenado 4x4)."""
    return t * 16 > BAYER4[y % 4][x % 4] + 0.5


def gradiente(cores, t, x, y):
    """Escolhe cor da lista (0..1) com dithering entre faixas."""
    t = max(0.0, min(0.9999, t))
    pos = t * (len(cores) - 1)
    i = int(pos)
    f = pos - i
    if i + 1 < len(cores) and dither(x, y, f):
        return cores[i + 1]
    return cores[i]


# ---------------------------------------------------------------------------
# PERSONAGEM: Agenor (18x36, de frente)
# ---------------------------------------------------------------------------
# Desenhado a mao, pixel por pixel. Cada letra e uma cor:
#   o contorno | 1-4 pele (escura -> clara) | r R bandana | k preto (olhos, bigode)
#   e branco do olho | w g cueca (branco / sombra) | h coracao
AGENOR_CORES = {
    ".": None, "o": "preto", "1": "pele0", "2": "pele1", "3": "pele2", "4": "pele3",
    "r": "verm2", "R": "verm1", "w": "branco", "g": "cinza", "h": "verm2", "e": "branco", "k": "preto",
}
AGENOR_CABECA = [
    "......oooooo......",  # 0  careca
    ".....o334443o.....",
    "....o33344433o....",
    "....orrrrrrrro.rR.",  # 3  bandana (com a ponta do no voando)
    "....oRRRRRRRRoRr..",
    "....o3kk33kk2o.o..",  # 5  sobrancelhas bravas
    "...oo3ek33ke2oo...",  # 6  olhos
    "...o2333423222o...",  # 7  nariz e orelhas
    "....o32kkkk22o....",  # 8  bigode
    ".....o212212o.....",  # 9  barba por fazer
    "......o1111o......",  # 10 pescoco
    "..oooo233332oooo..",  # 11 trapezio
    ".o44333333333322o.",  # 12 ombros
]
AGENOR_TRONCO = [  # (braco esq, separacao, peito/abdomen, separacao, braco dir)
    ("343", "1", "44432332", "1", "322"),
    ("343", "1", "44432332", "1", "321"),
    ("342", "1", "22212222", "1", "321"),
    ("343", "1", "33424322", "1", "321"),  # gominhos
    ("343", "1", "33212322", "1", "321"),
    ("343", "1", "33424322", "1", "321"),
    ("233", "1", "33212322", "1", "221"),
    ("343", "1", "23424321", "1", "321"),
    ("344", "o", "23333221", "o", "321"),
]
AGENOR_CUECA = ["gggggggg", "wwhwhwwg", "whhhhhwg", "wwhhhwwg", "wwwhwwwg", "wwwoowwg"]


def agenor_linhas():
    L = list(AGENOR_CABECA)
    for a, s1, c, s2, b in AGENOR_TRONCO:
        L.append("o" + a + s1 + c + s2 + b + "o")
    cu = AGENOR_CUECA
    L.append("o334o" + cu[0] + "o221o")           # maos
    L.append("o343o" + cu[1] + "o321o")
    L.append(".oooo" + cu[2] + "oooo.")
    for linha in cu[3:]:
        L.append("....o" + linha + "o....")
    for e, d in [("343", "332"), ("343", "321"), ("233", "321"), ("343", "332"), ("343", "321"), ("233", "221")]:
        L.append("....o" + e + "oo" + d + "o....")  # pernas
    L.append("...o3433oo3322o...")                    # pes
    L.append("...oooooooooooo...")
    return L


def agenor(linhas=None):
    linhas = linhas or agenor_linhas()
    assert len(linhas) == 36 and all(len(l) == 18 for l in linhas)
    img = Image.new("RGBA", (18, 36), T)
    for y, l in enumerate(linhas):
        for x, ch in enumerate(l):
            if AGENOR_CORES[ch]:
                img.putpixel((x, y), PAL[AGENOR_CORES[ch]])
    return img


# Quadros de animacao: saem do desenho base mexendo em linhas inteiras.
# Linhas do desenho: 0-12 cabeca | 13-21 tronco | 22-27 maos e cueca | 28-33 pernas | 34-35 pes
VAZIA = "." * 18


def _respirar(L):
    """Peito 'murcha' 1 pixel: tira uma linha do tronco e desce a parte de cima."""
    L = list(L)
    del L[18]
    return [VAZIA] + L


def _levantar_pernas(L, esquerda, direita, px=2):
    """Encolhe a perna (pe sobe 'px' pixels). Esquerda = colunas 0-8, direita = 9-17."""
    L = list(L)
    for lado, ativo in ((slice(0, 9), esquerda), (slice(9, 18), direita)):
        if not ativo:
            continue
        metade = [l[lado] for l in L[28:36]]
        metade = metade[:2] + metade[2 + px:] + ["." * len(metade[0])] * px
        for i, m in enumerate(metade):
            l = L[28 + i]
            L[28 + i] = l[:lado.start] + m + l[lado.stop:]
    return L


def _bracos_para_cima(L):
    """Maos sobem 1 pixel (pose de pulo)."""
    L = list(L)
    for y in (21, 22, 23):
        abaixo = L[y + 1]
        L[y] = abaixo[:5] + L[y][5:13] + abaixo[13:]
    L[24] = ".oooo" + L[24][5:13] + "oooo."
    return L


def agenor_quadros():
    """Retorna {nome_do_arquivo: imagem} com todos os quadros do player."""
    base = agenor_linhas()
    return {
        "agenor_parado_0": agenor(base),
        "agenor_parado_1": agenor(_respirar(base)),
        "agenor_andando_0": agenor(_levantar_pernas(base, True, False)),
        "agenor_andando_1": agenor(base),
        "agenor_andando_2": agenor(_levantar_pernas(base, False, True)),
        "agenor_andando_3": agenor(_respirar(base)),
        "agenor_pulo": agenor(_bracos_para_cima(_levantar_pernas(base, True, True, 3))),
    }


# ---------------------------------------------------------------------------
# INIMIGO: demonio-coracao com asinhas (21x14), 2 quadros
# ---------------------------------------------------------------------------
def demonio(quadro):
    g = Grade(21, 14)
    # coracao
    g.elipse(7.5, 5.5, 3.6, 3.6, "verm")
    g.elipse(13.5, 5.5, 3.6, 3.6, "verm")
    g.poligono([(4.2, 6), (16.8, 6), (10.5, 13.2)], "verm")
    # asinhas de morcego
    if quadro == 0:
        asa_e = [(4.5, 5), (0, 1), (1, 5), (0, 8), (4.5, 8)]
        asa_d = [(16.5, 5), (21, 1), (20, 5), (21, 8), (16.5, 8)]
    else:
        asa_e = [(4.5, 6), (0, 9), (1, 6), (0, 4), (4.5, 5)]
        asa_d = [(16.5, 6), (21, 9), (20, 6), (21, 4), (16.5, 5)]
    g.poligono(asa_e, "rocha")
    g.poligono(asa_d, "rocha")
    img = g.imagem()
    # chifres
    for (x, y) in ((6, 1), (6, 0), (14, 1), (14, 0)):
        img.putpixel((x, y), PAL["lava3"] if y == 0 else PAL["lava2"])
    # olhos bravos
    for (x, y, cor) in ((7, 5, "branco"), (8, 5, "branco"), (8, 6, "preto"),
                        (12, 5, "branco"), (13, 5, "branco"), (12, 6, "preto"),
                        (7, 4, "preto"), (13, 4, "preto"), (8, 4, "verm0"), (12, 4, "verm0")):
        img.putpixel((x, y), PAL[cor])
    # boca com presas
    for x in range(8, 13):
        img.putpixel((x, 9), PAL["preto"])
    img.putpixel((9, 10), PAL["branco"])
    img.putpixel((11, 10), PAL["branco"])
    # brilho
    img.putpixel((5, 3), PAL["verm3"])
    img.putpixel((5, 4), PAL["verm3"])
    return img


# ---------------------------------------------------------------------------
# ESPINHO (22x14) e ESTALAGMITE (espinho gigante)
# ---------------------------------------------------------------------------
def espinho():
    g = Grade(22, 14)
    g.poligono([(0, 14), (22, 14), (16, 7), (11.2, 0), (8, 5), (4, 8)], "rocha")
    img = g.imagem()
    # ponta incandescente
    for (x, y, cor) in ((11, 1, "lava4"), (11, 2, "lava3"), (10, 3, "lava3"), (11, 3, "lava2"),
                        (10, 4, "lava2"), (12, 4, "lava2")):
        img.putpixel((x, y), PAL[cor])
    # rachaduras de lava
    for (x, y) in ((10, 8), (11, 9), (11, 10), (12, 11), (6, 11), (7, 12), (15, 10), (16, 11)):
        img.putpixel((x, y), PAL["lava2"])
    return img


def estalagmite():
    w, h = 38, 142
    g = Grade(w, h)
    rnd = random.Random(7)
    pts = []
    # lado esquerdo (de baixo pra cima) com recortes
    passos = 14
    for i in range(passos + 1):
        t = i / passos
        y = h - t * (h - 1)
        x = (1 - t) * 0 + t * (w / 2 - 0.5)
        x += rnd.uniform(0, 3) * (1 - t)
        pts.append((x, y))
    for i in range(passos, -1, -1):
        t = i / passos
        y = h - t * (h - 1)
        x = (1 - t) * w + t * (w / 2 + 0.5)
        x -= rnd.uniform(0, 3) * (1 - t)
        pts.append((x, y))
    g.poligono(pts, "rocha")
    img = g.imagem()
    # veio de lava subindo pelo meio
    x = w // 2
    for y in range(4, h - 2):
        if y % 9 == 0:
            x += rnd.choice((-1, 0, 1))
        if img.getpixel((x, y))[3] and img.getpixel((x, y)) != PAL["preto"]:
            cor = "lava4" if y < 10 else ("lava3" if y % 5 else "lava2")
            img.putpixel((x, y), PAL[cor])
    # rachaduras laterais
    for _ in range(26):
        y0 = rnd.randint(30, h - 4)
        x0 = rnd.randint(4, w - 5)
        for k in range(rnd.randint(2, 4)):
            xx, yy = x0 + k * rnd.choice((-1, 1)), y0 + k
            if 0 <= xx < w and 0 <= yy < h:
                p = img.getpixel((xx, yy))
                if p[3] and p != PAL["preto"]:
                    img.putpixel((xx, yy), PAL["lava1"] if k else PAL["lava2"])
    return img


# ---------------------------------------------------------------------------
# CHAO / PAREDES: tile 16x16 com 9-slice (bordas fixas, miolo repete)
# ---------------------------------------------------------------------------
def tile_rocha(quadro=0):
    """Ladrilho de rocha 16x16. 'quadro' (0-3) move o brilho da crosta de lava (animacao)."""
    img = Image.new("RGBA", (16, 16), PAL["rocha1"])
    px = img.load()
    rnd = random.Random(3)
    # miolo: pedras irregulares
    for y in range(16):
        for x in range(16):
            r = rnd.random()
            px[x, y] = PAL["rocha2"] if r < 0.18 else (PAL["rocha0"] if r > 0.94 else PAL["rocha1"])
    # juntas das pedras (padrao que repete sem emenda no miolo 10x9)
    for x in range(3, 13):
        px[x, 8] = PAL["rocha0"]
    for y in range(4, 8):
        px[7, y] = PAL["rocha0"]
    for y in range(9, 13):
        px[4, y] = PAL["rocha0"]
        px[10, y] = PAL["rocha0"]
    for (x, y) in ((8, 5), (8, 6), (5, 10), (11, 10), (11, 11)):
        px[x, y] = PAL["rocha3"]
    # crosta de lava no topo
    for x in range(16):
        px[x, 0] = PAL["preto"]
        xq = x + quadro * 4  # o brilho anda 4 px por quadro (16 px = volta completa em 4 quadros)
        px[x, 1] = PAL["lava4"] if xq % 16 in (0, 1, 8) else PAL["lava3"]
        px[x, 2] = PAL["lava3"] if xq % 16 in (1, 9) else PAL["lava2"]
        px[x, 3] = PAL["lava1"] if (x + quadro) % 3 else PAL["lava2"]
    # pingos de lava
    for (x, y) in ((2, 4), (9, 4), (13, 4), (13, 5)):
        px[x, y] = PAL["lava2"] if (x + quadro) % 4 == 0 else PAL["lava1"]
    # bordas laterais e inferior
    for y in range(1, 16):
        px[0, y] = PAL["preto"]
        px[15, y] = PAL["preto"]
        if y > 3:
            px[1, y] = PAL["rocha3"]
            px[14, y] = PAL["rocha0"]
    for x in range(16):
        px[x, 15] = PAL["preto"]
        if 0 < x < 15:
            px[x, 14] = PAL["rocha0"]
    return img


def plataforma_dissolvivel():
    """Plataforma de enxofre rachada (200x16 'pixels de jogo'), depois esticada
    para 200x200 porque o objeto na cena usa escala ~12.5 x 1."""
    w, h = 200, 16
    img = Image.new("RGBA", (w, h), T)
    px = img.load()
    rnd = random.Random(11)
    for y in range(h):
        for x in range(w):
            r = rnd.random()
            base = "enx1" if r < 0.6 else ("enx2" if r < 0.9 else "enx0")
            px[x, y] = PAL[base]
    for x in range(w):
        px[x, 0] = PAL["preto"]
        px[x, 1] = PAL["enx3"]
        px[x, 2] = PAL["enx2"]
        px[x, h - 1] = PAL["preto"]
        px[x, h - 2] = PAL["enx0"]
    # blocos separados por rachaduras
    x = 0
    while x < w:
        x += rnd.randint(18, 30)
        if x >= w - 3:
            break
        cx = x
        for y in range(1, h - 1):
            if y % 3 == 0:
                cx += rnd.choice((-1, 0, 1))
            if 0 <= cx < w:
                px[cx, y] = PAL["preto"]
            if 0 <= cx + 1 < w and y > 2:
                px[cx + 1, y] = PAL["enx3"] if y % 4 == 0 else PAL["enx0"]
    # bolhas de enxofre
    for _ in range(40):
        bx, by = rnd.randint(2, w - 3), rnd.randint(4, h - 4)
        px[bx, by] = PAL["enx3"]
    for y in range(h):
        px[0, y] = PAL["preto"]
        px[w - 1, y] = PAL["preto"]
    return esticar_linhas(img, 1, 1, w_final=200, h_final=200)


# ---------------------------------------------------------------------------
# TROFEU (30x31), 4 quadros de brilho
# ---------------------------------------------------------------------------
def trofeu(quadro):
    g = Grade(30, 31)
    g.poligono([(6, 2), (24, 2), (22, 13), (18, 17), (12, 17), (8, 13)], "ouro")
    g.ret(13, 17, 16, 22, "ouro")
    g.ret(10, 22, 19, 24, "ouro")
    g.ret(7, 25, 22, 29, "ouro")
    # alcas
    for cx in (4.5, 25.5):
        g.elipse(cx, 7.5, 3.5, 4.5, "ouro")
    img = g.imagem(luz=(-1, -1))
    px = img.load()
    # furo das alcas
    for (cx, cy) in ((4.5, 7.5), (25.5, 7.5)):
        for y in range(31):
            for x in range(30):
                if ((x + 0.5 - cx) / 1.6) ** 2 + ((y + 0.5 - cy) / 2.5) ** 2 <= 1:
                    px[x, y] = T
    img = contornar(img, PAL["preto"])
    px = img.load()
    # boca do trofeu (interior escuro)
    for x in range(8, 22):
        px[x, 3] = PAL["ouro0"]
    for x in range(9, 21):
        px[x, 4] = PAL["ouro1"]
    # placa na base
    for x in range(11, 19):
        px[x, 27] = PAL["ouro1"]
    # chama do inferno na taca
    for (x, y, cor) in ((15, 8, "lava4"), (14, 9, "lava3"), (15, 9, "lava4"), (16, 9, "lava3"),
                        (14, 10, "lava2"), (15, 10, "lava3"), (16, 10, "lava2"), (15, 7, "lava3")):
        px[x, y] = PAL[cor]
    # brilho que passa (animacao)
    if quadro > 0:
        offs = {1: 6, 2: 13, 3: 20}[quadro]
        for y in range(2, 30):
            for k in (0, 1):
                x = offs + k + (y - 2) // 3
                if 0 <= x < 30 and px[x, y][3] and px[x, y] != PAL["preto"]:
                    px[x, y] = PAL["ouro3"] if k == 0 else PAL["branco"]
    return img


# ---------------------------------------------------------------------------
# FUNDO DO INFERNO (procedural, com dithering)
# ---------------------------------------------------------------------------
CEU = [PAL["noite"], PAL["vinho"], PAL["lava0"], PAL["lava1"], PAL["lava2"]]


def silhueta(w, base, amplitude, rnd, rugosidade=0.55, passos=7):
    """Linha de montanhas (deslocamento do ponto medio). Retorna altura por coluna."""
    n = 2 ** passos + 1
    alt = [0.0] * n
    alt[0], alt[-1] = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
    step, amp = n - 1, 1.0
    while step > 1:
        half = step // 2
        for i in range(half, n - 1, step):
            alt[i] = (alt[i - half] + alt[i + half]) / 2 + rnd.uniform(-amp, amp)
        step, amp = half, amp * rugosidade
    return [base + amplitude * alt[int(x / (w - 1) * (n - 1))] for x in range(w)]


def fundo_inferno(w, h, semente=5, sem_ceu=False):
    rnd = random.Random(semente)
    img = Image.new("RGBA", (w, h), PAL["noite"])
    px = img.load()
    # ceu: gradiente com dithering (escuro em cima -> brasa embaixo)
    for y in range(h):
        t = (y / h) ** 1.6
        for x in range(w):
            px[x, y] = gradiente(CEU, t * 0.95, x, y)
    # faixas de nevoa quente (brilho de lava ao longe)
    for _ in range(max(2, h // 70)):
        cy = rnd.uniform(0.15, 0.75) * h
        esp = rnd.uniform(0.03, 0.07) * h
        for y in range(max(0, int(cy - esp)), min(h, int(cy + esp))):
            t = 1 - abs(y - cy) / esp
            for x in range(w):
                ondula = (math.sin(x * 0.013 + cy) + math.sin(x * 0.037 + cy * 2)) * 0.35
                if dither(x, y, t * (0.3 + ondula * 0.8)):
                    px[x, y] = PAL["lava0"] if px[x, y] != PAL["lava1"] else PAL["lava2"]
    # pilares de rocha da caverna (camada distante, do chao ao teto)
    x = rnd.randint(0, 40)
    while x < w:
        larg = rnd.randint(14, 34)
        fase = rnd.uniform(0, 6)
        for y in range(h):
            meia = larg / 2 * (0.75 + 0.25 * math.sin(y * 0.03 + fase)) + 3 * math.sin(y * 0.11 + fase)
            for xx in range(int(x - meia), int(x + meia) + 1):
                if 0 <= xx < w:
                    borda = abs(xx - x) > meia - 1.5
                    px[xx, y] = PAL["rocha1"] if borda and xx < x else (PAL["vinho"] if borda else PAL["rocha0"])
            # rachaduras brilhando no pilar
            if y % 23 == int(fase * 3) % 23:
                for k in range(3):
                    xx = int(x - meia / 2) + k
                    if 0 <= xx < w and y + k < h:
                        px[xx, y + k] = PAL["lava1"]
        x += larg + rnd.randint(50, 130)
    # camadas de montanhas (longe -> perto)
    camadas = [
        (0.58, 0.10, PAL["vinho"], PAL["lava1"]),
        (0.70, 0.12, PAL["rocha1"], PAL["lava2"]),
        (0.84, 0.10, PAL["rocha0"], PAL["lava3"]),
    ]
    for i, (base, amp, cor, borda) in enumerate(camadas):
        linha = silhueta(w, base * h, amp * h, rnd, passos=8)
        for x in range(w):
            topo = int(linha[x])
            for y in range(max(0, topo), h):
                px[x, y] = cor
            if 0 <= topo < h:
                px[x, topo] = borda
    # cascatas de lava
    for _ in range(max(2, w // 220)):
        x0 = rnd.randint(10, w - 10)
        larg = rnd.randint(2, 3)
        y_fim = int(h * rnd.uniform(0.72, 0.9))
        for y in range(0, y_fim):
            ondula = int(math.sin(y * 0.15 + x0) * 0.8)
            # brilho em volta da cascata
            for k in range(-3, larg + 3):
                xx = x0 + k + ondula
                if 0 <= xx < w and dither(xx, y, 0.35 - abs(k - larg / 2) * 0.08):
                    px[xx, y] = PAL["lava0"]
            for k in range(larg):
                cor = PAL["lava2"] if k == larg // 2 else PAL["lava1"]
                if (y + k) % 7 == 0:
                    cor = PAL["lava3"]
                xx = x0 + k + ondula
                if 0 <= xx < w:
                    px[xx, y] = cor
    # mar de lava no fundo
    nivel = int(h * 0.9)
    for y in range(nivel, h):
        for x in range(w):
            onda = math.sin(x * 0.21 + y * 1.7 + math.sin(y * 3.1) * 2) + math.sin(x * 0.047 - y)
            px[x, y] = PAL["lava3"] if onda > 1.2 else (PAL["lava2"] if onda > -0.9 else PAL["lava1"])
    for x in range(w):
        px[x, nivel] = PAL["lava4"]
    # estalactites no teto
    if not sem_ceu:
        x = 0
        while x < w:
            larg = rnd.randint(3, 9)
            comp = rnd.randint(int(h * 0.04), int(h * 0.16))
            for y in range(comp):
                meia = larg * (1 - y / comp) / 2
                for xx in range(int(x + larg / 2 - meia), int(x + larg / 2 + meia) + 1):
                    if 0 <= xx < w:
                        px[xx, y] = PAL["rocha0"] if y < comp - 1 else PAL["rocha1"]
            x += larg + rnd.randint(0, 6)
        for x in range(w):
            for y in range(0, int(h * 0.025)):
                px[x, y] = PAL["preto"]
    # brasas (pontinhos)
    for _ in range(w * h // 1100):
        x, y = rnd.randrange(w - 1), rnd.randrange(int(h * 0.1), nivel - 1)
        cor = PAL["lava3"] if rnd.random() < 0.7 else PAL["lava4"]
        px[x, y] = cor
        if rnd.random() < 0.25:  # algumas brasas maiores
            px[x + 1, y] = PAL["lava2"]
            px[x, y + 1] = PAL["lava2"]
    return img


def fundo_inferno_camadas(w, h, semente=5, quadros_lava=4):
    """O mesmo cenario do fundo_inferno, separado em camadas para o efeito de paralaxe
    (cada camada anda numa velocidade diferente quando a camera se move).
    Retorna {nome: imagem}. A lava (cascatas + mar) tem varios quadros de animacao."""
    rnd = random.Random(semente)
    camadas = {}

    # 1) CEU: gradiente + nevoa quente (opaca, fica atras de tudo)
    ceu = Image.new("RGBA", (w, h), PAL["noite"])
    px = ceu.load()
    for y in range(h):
        t = (y / h) ** 1.6
        for x in range(w):
            px[x, y] = gradiente(CEU, t * 0.95, x, y)
    for _ in range(max(2, h // 70)):
        cy = rnd.uniform(0.15, 0.75) * h
        esp = rnd.uniform(0.03, 0.07) * h
        for y in range(max(0, int(cy - esp)), min(h, int(cy + esp))):
            t = 1 - abs(y - cy) / esp
            for x in range(w):
                ondula = (math.sin(x * 0.013 + cy) + math.sin(x * 0.037 + cy * 2)) * 0.35
                if dither(x, y, t * (0.3 + ondula * 0.8)):
                    px[x, y] = PAL["lava0"] if px[x, y] != PAL["lava1"] else PAL["lava2"]
    camadas["fundo_inferno_ceu"] = ceu

    # 2) PILARES + montanhas mais distantes
    pil = Image.new("RGBA", (w, h), T)
    px = pil.load()
    x = rnd.randint(0, 40)
    while x < w:
        larg = rnd.randint(14, 34)
        fase = rnd.uniform(0, 6)
        for y in range(h):
            meia = larg / 2 * (0.75 + 0.25 * math.sin(y * 0.03 + fase)) + 3 * math.sin(y * 0.11 + fase)
            for xx in range(int(x - meia), int(x + meia) + 1):
                if 0 <= xx < w:
                    borda = abs(xx - x) > meia - 1.5
                    px[xx, y] = PAL["rocha1"] if borda and xx < x else (PAL["vinho"] if borda else PAL["rocha0"])
            if y % 23 == int(fase * 3) % 23:
                for k in range(3):
                    xx = int(x - meia / 2) + k
                    if 0 <= xx < w and y + k < h:
                        px[xx, y + k] = PAL["lava1"]
        x += larg + rnd.randint(50, 130)

    def montanha(img, base, amp, cor, borda):
        p = img.load()
        linha = silhueta(w, base * h, amp * h, rnd, passos=8)
        for x in range(w):
            topo = int(linha[x])
            for y in range(max(0, topo), h):
                p[x, y] = cor
            if 0 <= topo < h:
                p[x, topo] = borda

    montanha(pil, 0.58, 0.10, PAL["vinho"], PAL["lava1"])
    camadas["fundo_inferno_pilares"] = pil

    # 3) MONTANHAS mais perto
    mont = Image.new("RGBA", (w, h), T)
    montanha(mont, 0.70, 0.12, PAL["rocha1"], PAL["lava2"])
    montanha(mont, 0.84, 0.10, PAL["rocha0"], PAL["lava3"])
    camadas["fundo_inferno_montanhas"] = mont

    # 4) LAVA: cascatas escorrendo + mar de lava ondulando (animada)
    cascatas = []
    for _ in range(max(2, w // 220)):
        cascatas.append((rnd.randint(10, w - 10), rnd.randint(2, 3), int(h * rnd.uniform(0.72, 0.9))))
    nivel = int(h * 0.9)
    for q in range(quadros_lava):
        lava = Image.new("RGBA", (w, h), T)
        px = lava.load()
        for x0, larg, y_fim in cascatas:
            for y in range(0, y_fim):
                ondula = int(math.sin(y * 0.15 + x0) * 0.8)
                for k in range(-3, larg + 3):
                    xx = x0 + k + ondula
                    if 0 <= xx < w and dither(xx, y, 0.35 - abs(k - larg / 2) * 0.08):
                        px[xx, y] = PAL["lava0"]
                for k in range(larg):
                    cor = PAL["lava2"] if k == larg // 2 else PAL["lava1"]
                    # os pontos claros descem 2 px por quadro (parece escorrer)
                    if (y - q * 2 + k) % 8 == 0:
                        cor = PAL["lava3"]
                    xx = x0 + k + ondula
                    if 0 <= xx < w:
                        px[xx, y] = cor
        fase = q * 2 * math.pi / quadros_lava
        for y in range(nivel, h):
            for x in range(w):
                onda = math.sin(x * 0.21 + y * 1.7 + math.sin(y * 3.1) * 2 + fase) + math.sin(x * 0.047 - y + fase)
                px[x, y] = PAL["lava3"] if onda > 1.2 else (PAL["lava2"] if onda > -0.9 else PAL["lava1"])
        for x in range(w):
            px[x, nivel] = PAL["lava4"] if (x // 3 + q) % 4 else PAL["lava3"]
        camadas[f"fundo_inferno_lava_{q}"] = lava

    # 5) TETO: estalactites (camada mais perto)
    teto = Image.new("RGBA", (w, h), T)
    px = teto.load()
    x = 0
    while x < w:
        larg = rnd.randint(3, 9)
        comp = rnd.randint(int(h * 0.04), int(h * 0.16))
        for y in range(comp):
            meia = larg * (1 - y / comp) / 2
            for xx in range(int(x + larg / 2 - meia), int(x + larg / 2 + meia) + 1):
                if 0 <= xx < w:
                    px[xx, y] = PAL["rocha0"] if y < comp - 1 else PAL["rocha1"]
        x += larg + rnd.randint(0, 6)
    for x in range(w):
        for y in range(0, int(h * 0.025)):
            px[x, y] = PAL["preto"]
    camadas["fundo_inferno_teto"] = teto
    return camadas


def brasa(quadro):
    """Brasa voando (3x3 px), 2 quadros: acesa e piscando."""
    img = Image.new("RGBA", (3, 3), T)
    px = img.load()
    if quadro == 0:
        px[1, 1] = PAL["lava4"]
        for (x, y) in ((0, 1), (2, 1), (1, 0), (1, 2)):
            px[x, y] = PAL["lava2"]
    else:
        px[1, 1] = PAL["lava3"]
    return img


def fundo_menu():
    w, h = 240, 135
    img = fundo_inferno(w, h, semente=21)
    px = img.load()
    # brilho atras do titulo (circulo com dithering)
    cx, cy, r = w / 2, h * 0.32, 52
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - cx) * 0.8, y - cy) / r
            if d < 1 and dither(x, y, (1 - d) * 0.8):
                atual = px[x, y]
                px[x, y] = PAL["lava1"] if atual in (PAL["noite"], PAL["vinho"]) else atual
    # chao de pedra na frente + Agenor de costas olhando o inferno
    for y in range(int(h * 0.88), h):
        for x in range(w):
            px[x, y] = PAL["preto"] if y == int(h * 0.88) else (PAL["rocha1"] if (x // 6 + y) % 5 else PAL["rocha0"])
    ag = agenor()
    img.alpha_composite(ag, (int(w * 0.2), int(h * 0.88) - 35))
    # vinheta escura nas bordas
    for y in range(h):
        for x in range(w):
            d = max(abs(x - w / 2) / (w / 2), abs(y - h / 2) / (h / 2))
            if d > 0.86 and dither(x, y, (d - 0.86) / 0.14):
                px[x, y] = PAL["preto"]
    return img


# ---------------------------------------------------------------------------
# UI: botao e painel (9-slice)
# ---------------------------------------------------------------------------
def botao(estado="normal"):
    """Botao 24x16 com moldura dourada e relevo (9-slice com bordas de 4 px).
    estado: 'normal', 'hover' (mouse em cima: brilha) ou 'press' (afundado)."""
    w, h = 24, 16
    img = Image.new("RGBA", (w, h), T)
    px = img.load()
    if estado == "hover":
        cima, meio, baixo, brilho, aro, aro_esc, dentro = "lava3", "lava2", "lava1", "lava4", "ouro3", "ouro2", "lava0"
    elif estado == "press":
        cima, meio, baixo, brilho, aro, aro_esc, dentro = "verm1", "verm1", "verm0", "verm0", "ouro1", "ouro0", "verm0"
    else:
        cima, meio, baixo, brilho, aro, aro_esc, dentro = "verm2", "verm1", "verm0", "verm3", "ouro2", "ouro1", "verm0"
    for y in range(h):
        for x in range(w):
            borda = min(x, y, w - 1 - x, h - 1 - y)
            if borda == 0:
                cor = "preto"
            elif borda == 1:
                cor = aro if (y < h - 2 and x < w - 2) else aro_esc
            elif borda == 2:
                cor = dentro
            else:
                t = (y - 3) / (h - 6)
                cor = cima if t < 0.45 else (meio if t < 0.85 else baixo)
                if y == 3:
                    cor = brilho
            px[x, y] = PAL[cor]
    # rebites dourados
    for (x, y) in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
        px[x, y] = PAL["ouro3" if estado != "press" else "ouro1"]
    for (x, y) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        px[x, y] = T
    return img


def painel():
    """Painel 32x32 (9-slice com bordas de 10 px): moldura de rocha + aro dourado + brilho de lava."""
    w = h = 32
    img = Image.new("RGBA", (w, h), T)
    px = img.load()
    for y in range(h):
        for x in range(w):
            b = min(x, y, w - 1 - x, h - 1 - y)
            claro = x + y < w  # metade de cima/esquerda recebe luz
            if b == 0:
                cor = PAL["preto"]
            elif b == 1:
                cor = PAL["ouro3" if claro else "ouro1"]
            elif b == 2:
                cor = PAL["ouro2" if claro else "ouro0"]
            elif b == 3:
                cor = PAL["preto"]
            elif b in (4, 5, 6):
                cor = PAL["rocha2" if (x * 3 + y * 5) % 7 == 0 else ("rocha3" if claro and b == 4 else "rocha1")]
            elif b == 7:
                cor = PAL["preto"]
            elif b == 8:
                cor = PAL["lava2"]
            elif b == 9:
                cor = c("6e1018", 235)
            else:
                cor = c("1a0a12", 232)
            px[x, y] = cor
    # rebites nos cantos
    for (x, y) in ((5, 5), (w - 6, 5), (5, h - 6), (w - 6, h - 6)):
        px[x, y] = PAL["lava4"]
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            px[x + dx, y + dy] = PAL["ouro1"]
    for (x, y) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        px[x, y] = T
    return img


def faixa_titulo():
    """Faixa atras dos titulos (32x16, 9-slice: pontas de 8 px, cima/baixo 5 px)."""
    w, h = 32, 16
    img = Image.new("RGBA", (w, h), T)
    px = img.load()
    for y in range(h):
        recuo = abs(y - (h - 1) / 2)
        ponta = int(max(0, 4 - recuo * 0.6))  # pontas em forma de seta (cauda de fita)
        x0, x1 = 4 - ponta, w - 5 + ponta
        if y in (0, h - 1):
            x0, x1 = 5, w - 6
        for x in range(x0, x1 + 1):
            b = min(y, h - 1 - y, x - x0, x1 - x)
            if b == 0:
                cor = PAL["preto"]
            elif b == 1:
                cor = PAL["ouro2"] if y < h / 2 else PAL["ouro1"]
            elif b == 2:
                cor = PAL["preto"]
            else:
                cor = PAL["vinho"] if y < h * 0.55 else PAL["noite"]
                if y == 3:
                    cor = PAL["verm1"]
            px[x, y] = cor
    return img


# ---------------------------------------------------------------------------
# FONTE PIXELADA (gera um arquivo .ttf de verdade, sem bibliotecas externas)
# ---------------------------------------------------------------------------
# Cada glifo: (linhas de cima pra baixo, linha de base da ultima linha)
G = {}


def glifo(ch, linhas, base=0):
    G[ch] = ([l.replace(" ", ".") for l in linhas], base)


# Maiusculas 5x7
for ch, l in {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
}.items():
    glifo(ch, l)

# Minusculas (altura-x 5, hastes 7, descendentes 2)
for ch, l, b in [
    ("a", [".##.", "...#", ".###", "#..#", ".###"], 0),
    ("b", ["#...", "#...", "###.", "#..#", "#..#", "#..#", "###."], 0),
    ("c", [".###", "#...", "#...", "#...", ".###"], 0),
    ("d", ["...#", "...#", ".###", "#..#", "#..#", "#..#", ".###"], 0),
    ("e", [".##.", "#..#", "####", "#...", ".###"], 0),
    ("f", [".###", ".#..", "####", ".#..", ".#..", ".#..", ".#.."], 0),
    ("g", [".###", "#..#", "#..#", "#..#", ".###", "...#", "###."], -2),
    ("h", ["#...", "#...", "###.", "#..#", "#..#", "#..#", "#..#"], 0),
    ("i", ["#", ".", "#", "#", "#", "#", "#"], 0),
    ("j", ["..#", "...", "..#", "..#", "..#", "..#", "..#", "..#", "##."], -2),
    ("k", ["#...", "#...", "#..#", "#.#.", "##..", "#.#.", "#..#"], 0),
    ("l", ["##.", ".#.", ".#.", ".#.", ".#.", ".#.", ".##"], 0),
    ("m", ["##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"], 0),
    ("n", ["###.", "#..#", "#..#", "#..#", "#..#"], 0),
    ("o", [".##.", "#..#", "#..#", "#..#", ".##."], 0),
    ("p", ["###.", "#..#", "#..#", "#..#", "###.", "#...", "#..."], -2),
    ("q", [".###", "#..#", "#..#", "#..#", ".###", "...#", "...#"], -2),
    ("r", ["#.##", "##..", "#...", "#...", "#..."], 0),
    ("s", [".###", "#...", ".##.", "...#", "###."], 0),
    ("t", [".#..", ".#..", "####", ".#..", ".#..", ".#..", ".###"], 0),
    ("u", ["#..#", "#..#", "#..#", "#..#", ".###"], 0),
    ("v", ["#...#", "#...#", ".#.#.", ".#.#.", "..#.."], 0),
    ("w", ["#...#", "#...#", "#.#.#", "#.#.#", ".#.#."], 0),
    ("x", ["#..#", "#..#", ".##.", "#..#", "#..#"], 0),
    ("y", ["#..#", "#..#", "#..#", "#..#", ".###", "...#", "###."], -2),
    ("z", ["####", "..#.", ".#..", "#...", "####"], 0),
]:
    glifo(ch, l, b)

# Numeros
for ch, l in {
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
}.items():
    glifo(ch, l)

# Pontuacao
glifo("!", ["#", "#", "#", "#", "#", ".", "#"])
glifo("?", [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."])
glifo(".", ["#"])
glifo(",", [".#", "#."], -1)
glifo(":", ["#", ".", ".", "#", "."])
glifo(";", [".#", "..", "..", ".#", "#."], -1)
glifo("'", ["#", "#"], 5)
glifo('"', ["#.#", "#.#"], 5)
glifo("-", ["###"], 3)
glifo("+", [".#.", "###", ".#."], 2)
glifo("=", ["###", "...", "###"], 2)
glifo("/", ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."])
glifo("(", [".#", "#.", "#.", "#.", "#.", "#.", ".#"])
glifo(")", ["#.", ".#", ".#", ".#", ".#", ".#", "#."])
glifo("_", ["#####"], -1)
glifo("*", ["#.#", ".#.", "#.#"], 3)
glifo("<", ["..#", ".#.", "#..", ".#.", "..#"], 1)
glifo(">", ["#..", ".#.", "..#", ".#.", "#.."], 1)
glifo("%", ["##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"])
glifo("#", [".#.#.", "#####", ".#.#.", "#####", ".#.#."], 1)
glifo("&", [".##..", "#..#.", ".##..", ".#..#", "#.##.", "#..#.", ".##.#"])
glifo("[", ["##", "#.", "#.", "#.", "#.", "#.", "##"])
glifo("]", ["##", ".#", ".#", ".#", ".#", ".#", "##"])
glifo("|", ["#", "#", "#", "#", "#", "#", "#", "#", "#"], -2)
glifo("@", [".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."])
glifo("$", ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."])
glifo(" ", ["..."])

# Acentos (portugues): marca de 2 linhas colocada em cima da letra
MARCAS = {
    "agudo": ["..#", ".#."],
    "grave": ["#..", ".#."],
    "circ": [".#.", "#.#"],
    "til": [".#.#", "#.#."],
    "trema": ["#.#", "..."],
}
G["ı"] = (["#", "#", "#", "#", "#"], 0)  # i sem ponto (base do í)


def acentuar(ch, base, marca):
    linhas, b = G[base]
    m = MARCAS[marca]
    wb, wm = len(linhas[0]), len(m[0])
    w = max(wb, wm)
    ob, om = (w - wb) // 2, (w - wm) // 2
    topo_base = b + len(linhas) - 1  # y da linha de cima da letra
    linhas_m = [("." * om + r + "." * w)[:w] for r in m]
    linhas_b = [("." * ob + r + "." * w)[:w] for r in linhas]
    G[ch] = (linhas_m + ["." * w] + linhas_b, b)
    assert topo_base + 3 <= 10


for ch, base, marca in [
    ("á", "a", "agudo"), ("à", "a", "grave"), ("â", "a", "circ"), ("ã", "a", "til"), ("ä", "a", "trema"),
    ("é", "e", "agudo"), ("ê", "e", "circ"), ("è", "e", "grave"),
    ("í", "ı", "agudo"), ("ó", "o", "agudo"), ("ô", "o", "circ"), ("õ", "o", "til"), ("ö", "o", "trema"),
    ("ú", "u", "agudo"), ("ü", "u", "trema"),
    ("Á", "A", "agudo"), ("À", "A", "grave"), ("Â", "A", "circ"), ("Ã", "A", "til"),
    ("É", "E", "agudo"), ("Ê", "E", "circ"), ("Í", "I", "agudo"),
    ("Ó", "O", "agudo"), ("Ô", "O", "circ"), ("Õ", "O", "til"), ("Ú", "U", "agudo"),
]:
    acentuar(ch, base, marca)
G["ç"] = (G["c"][0] + [".#.", "##."], -2)
G["Ç"] = (G["C"][0] + ["..#..", ".##.."], -2)
del G["ı"]

PX = 128         # unidades de fonte por pixel
EM = 8 * PX      # 1 em = 8 pixels -> tamanho de fonte multiplo de 8 = pixels inteiros
ASC = 10 * PX
DESC = -3 * PX


def contornos_de_pixels(pixels):
    """Transforma um conjunto de pixels (x,y com y pra cima) em contornos poligonais
    no sentido horario (padrao TrueType), unindo pixels vizinhos."""
    arestas = {}
    for (x, y) in pixels:
        for a, b in (((x, y), (x, y + 1)), ((x, y + 1), (x + 1, y + 1)),
                     ((x + 1, y + 1), (x + 1, y)), ((x + 1, y), (x, y))):
            if (b, a) in arestas:
                del arestas[(b, a)]
            else:
                arestas[(a, b)] = True
    saidas = {}
    for (a, b) in arestas:
        saidas.setdefault(a, []).append(b)
    contornos = []
    while saidas:
        inicio = next(iter(saidas))
        pts = [inicio]
        atual = inicio
        while True:
            prox = saidas[atual].pop()
            if not saidas[atual]:
                del saidas[atual]
            if prox == inicio:
                break
            pts.append(prox)
            atual = prox
        # remove pontos colineares
        limpos = []
        n = len(pts)
        for i in range(n):
            p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
            if (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0]) != 0:
                limpos.append(p1)
        contornos.append(limpos)
    return contornos


def checksum(dados):
    dados += b"\0" * ((4 - len(dados) % 4) % 4)
    return sum(struct.unpack(">%dI" % (len(dados) // 4), dados)) & 0xFFFFFFFF


def gerar_ttf(caminho, nome="PixelInferno"):
    chars = sorted(G.keys(), key=ord)
    glifos = [None] + chars  # 0 = .notdef
    glyf, loca, hmtx = b"", [], b""
    max_pts = max_cont = 0
    xmin_g = ymin_g = 10 ** 6
    xmax_g = ymax_g = -10 ** 6
    larg_total = 0
    for ch in glifos:
        if ch is None:
            linhas, base = ["####", "#..#", "#..#", "#..#", "#..#", "#..#", "####"], 0
        else:
            linhas, base = G[ch]
        w = len(linhas[0])
        avanco = (w + 1) * PX
        larg_total += avanco
        pixels = set()
        for i, l in enumerate(linhas):
            y = base + len(linhas) - 1 - i
            for x, p in enumerate(l):
                if p == "#":
                    pixels.add((x, y))
        loca.append(len(glyf))
        if not pixels:
            hmtx += struct.pack(">Hh", avanco, 0)
            continue
        conts = contornos_de_pixels(pixels)
        xs = [p[0] for cc in conts for p in cc]
        ys = [p[1] for cc in conts for p in cc]
        bx0, by0, bx1, by1 = min(xs) * PX, min(ys) * PX, max(xs) * PX, max(ys) * PX
        xmin_g, ymin_g = min(xmin_g, bx0), min(ymin_g, by0)
        xmax_g, ymax_g = max(xmax_g, bx1), max(ymax_g, by1)
        dados = struct.pack(">hhhhh", len(conts), bx0, by0, bx1, by1)
        fim, total = [], 0
        for cc in conts:
            total += len(cc)
            fim.append(total - 1)
        max_pts, max_cont = max(max_pts, total), max(max_cont, len(conts))
        dados += struct.pack(">%dH" % len(fim), *fim)
        dados += struct.pack(">H", 0)  # sem instrucoes
        dados += bytes([1] * total)    # todos os pontos "on-curve"
        px_ant = py_ant = 0
        dx, dy = b"", b""
        for cc in conts:
            for (x, y) in cc:
                dx += struct.pack(">h", x * PX - px_ant)
                dy += struct.pack(">h", y * PX - py_ant)
                px_ant, py_ant = x * PX, y * PX
        dados += dx + dy
        dados += b"\0" * ((4 - len(dados) % 4) % 4)
        glyf += dados
        hmtx += struct.pack(">Hh", avanco, bx0)
    loca.append(len(glyf))
    n = len(glifos)

    head = struct.pack(">IIIIHHqqhhhhHHhhh", 0x00010000, 0x00010000, 0, 0x5F0F3CF5, 0x000B, EM,
                       0, 0, xmin_g, ymin_g, xmax_g, ymax_g, 0, 8, 2, 1, 0)
    hhea = struct.pack(">IhhhHhhhhhhhhhhhH", 0x00010000, ASC, DESC, 0,
                       max(struct.unpack(">%dH" % (n * 2), hmtx)[0::2]), 0, 0, xmax_g, 1, 0, 0,
                       0, 0, 0, 0, 0, n)
    maxp = struct.pack(">IHHHHHHHHHHHHHH", 0x00010000, n, max_pts, max_cont, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0)
    os2 = struct.pack(">HhHHH" + "h" * 10 + "h", 4, larg_total // n, 400, 5, 0,
                      5 * PX, 5 * PX, 0, PX, 5 * PX, 5 * PX, 0, 4 * PX, PX, 3 * PX, 0)
    os2 += bytes([2, 11, 6, 9, 0, 0, 0, 0, 0, 0])  # panose
    os2 += struct.pack(">IIII", 0b11, 0, 0, 0)
    os2 += b"NONE"
    os2 += struct.pack(">HHHhhhHHIIhhHHH", 0x40, 32, max(ord(ch) for ch in chars), ASC, DESC, 0,
                       ASC, -DESC, 1, 0, 5 * PX, 7 * PX, 0, 32, 1)
    post = struct.pack(">IIhhIIIII", 0x00030000, 0, -PX, PX, 0, 0, 0, 0, 0)

    # cmap formato 4 (um segmento por caractere)
    segs = [(ord(ch), glifos.index(ch)) for ch in chars] + [(0xFFFF, 0)]
    sc = len(segs)
    busca = 2 * 2 ** int(math.log2(sc))
    fim_c = b"".join(struct.pack(">H", s[0]) for s in segs)
    ini_c = fim_c
    delta = b"".join(struct.pack(">H", ((s[1] - s[0]) & 0xFFFF) if s[0] != 0xFFFF else 1) for s in segs)
    rng = b"\0\0" * sc
    sub = struct.pack(">HHHHHHH", 4, 0, 0, sc * 2, busca, int(math.log2(sc)), sc * 2 - busca)
    sub += fim_c + b"\0\0" + ini_c + delta + rng
    sub = sub[:2] + struct.pack(">H", len(sub)) + sub[4:]
    cmap = struct.pack(">HHHHI", 0, 1, 3, 1, 12) + sub

    nomes = {1: nome, 2: "Regular", 3: nome + "-Regular", 4: nome + " Regular", 6: nome + "-Regular"}
    regs, txt = b"", b""
    for nid, s in nomes.items():
        b = s.encode("utf-16-be")
        regs += struct.pack(">HHHHHH", 3, 1, 0x409, nid, len(b), len(txt))
        txt += b
    name = struct.pack(">HHH", 0, len(nomes), 6 + 12 * len(nomes)) + regs + txt

    loca_b = struct.pack(">%dI" % len(loca), *loca)
    tabelas = {b"OS/2": os2, b"cmap": cmap, b"glyf": glyf, b"head": head, b"hhea": hhea,
               b"hmtx": hmtx, b"loca": loca_b, b"maxp": maxp, b"name": name, b"post": post}
    tags = sorted(tabelas)
    nt = len(tags)
    es = int(math.log2(nt))
    sr = 16 * 2 ** es
    cab = struct.pack(">IHHHH", 0x00010000, nt, sr, es, nt * 16 - sr)
    offset = 12 + 16 * nt
    dirs, corpo = b"", b""
    for t in tags:
        d = tabelas[t]
        dirs += struct.pack(">4sIII", t, checksum(d), offset + len(corpo), len(d))
        corpo += d + b"\0" * ((4 - len(d) % 4) % 4)
    fonte = bytearray(cab + dirs + corpo)
    ajuste = (0xB1B0AFBA - checksum(bytes(fonte))) & 0xFFFFFFFF
    pos_head = 12 + 16 * nt + sum(len(tabelas[t]) + (4 - len(tabelas[t]) % 4) % 4 for t in tags[:tags.index(b"head")])
    fonte[pos_head + 8:pos_head + 12] = struct.pack(">I", ajuste)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "wb") as f:
        f.write(fonte)
    print("  ok", os.path.relpath(caminho, RAIZ), f"({len(chars)} caracteres)")


def amostra_fonte(texto, escala=3):
    """Desenha o texto com os glifos (so para a imagem de preview)."""
    w = sum(len(G.get(ch, G["?"])[0][0]) + 1 for ch in texto)
    img = Image.new("RGBA", (w, 14), T)
    x = 0
    for ch in texto:
        linhas, b = G.get(ch, G["?"])
        for i, l in enumerate(linhas):
            y = 10 - (b + len(linhas) - 1 - i)
            for j, p in enumerate(l):
                if p == "#":
                    img.putpixel((x + j, y), PAL["creme"])
        x += len(linhas[0]) + 1
    return img.resize((w * escala, 14 * escala), Image.NEAREST)


# ---------------------------------------------------------------------------
def main():
    print("Gerando pixel art em", ART)
    imgs = {}
    imgs["agenor"] = salvar(agenor(), "Sprites", "Personagens", "agenor.png")
    for nome, img in agenor_quadros().items():
        imgs[nome] = salvar(img, "Sprites", "Personagens", "Animacao", nome + ".png")
    for q in (0, 1):
        imgs[f"demonio{q}"] = salvar(demonio(q), "Sprites", "Inimigos", f"demonio_coracao_{q}.png")
    imgs["espinho"] = salvar(espinho(), "Sprites", "Cenario", "espinho.png")
    est = estalagmite()
    imgs["estalagmite"] = est
    # objeto com escala 1.75 x 10.23 -> pixels esticados 6x na horizontal
    salvar(esticar_linhas(est, 6, 1), "Sprites", "Cenario", "estalagmite.png")
    imgs["tile"] = salvar(tile_rocha(), "Sprites", "Cenario", "tile_rocha.png")
    for q in range(1, 4):
        salvar(tile_rocha(q), "Sprites", "Cenario", "Animacao", f"tile_rocha_{q}.png")
    imgs["plataforma"] = salvar(plataforma_dissolvivel(), "Sprites", "Cenario", "plataforma_dissolvivel.png")
    for q in range(4):
        imgs[f"trofeu{q}"] = salvar(trofeu(q), "Sprites", "Objetos", f"trofeu_{q}.png")
    fundo = fundo_inferno(757, 398)
    # o objeto do fundo tem escala 12.79 x 12.32: as linhas sao levemente esticadas
    salvar(fundo.resize((757, 413), Image.NEAREST), "Sprites", "Cenario", "fundo_inferno.png")
    # Paralaxe: o mesmo fundo em camadas (mesmo tamanho e esticamento do fundo_inferno.png)
    for nome, camada in fundo_inferno_camadas(757, 398).items():
        salvar(camada.resize((757, 413), Image.NEAREST), "Sprites", "Cenario", "Paralaxe", nome + ".png")
    for q in (0, 1):
        salvar(brasa(q), "Sprites", "Cenario", f"brasa_{q}.png")
    imgs["menu"] = salvar(fundo_menu(), "Sprites", "UI", "fundo_menu.png")
    imgs["botao"] = salvar(botao(), "Sprites", "UI", "botao.png")
    imgs["botao_hover"] = salvar(botao("hover"), "Sprites", "UI", "botao_hover.png")
    imgs["botao_press"] = salvar(botao("press"), "Sprites", "UI", "botao_press.png")
    imgs["faixa"] = salvar(faixa_titulo(), "Sprites", "UI", "faixa_titulo.png")
    imgs["painel"] = salvar(painel(), "Sprites", "UI", "painel.png")
    gerar_ttf(os.path.join(ART, "Fontes", "PixelInferno.ttf"))

    # folha de preview para a documentacao
    os.makedirs(DOCS, exist_ok=True)
    folha = Image.new("RGBA", (1200, 760), PAL["noite"])
    x, y = 10, 10
    for nome in ["agenor", "demonio0", "demonio1", "espinho", "tile", "trofeu0", "trofeu2", "botao", "botao_hover", "botao_press", "painel", "faixa"]:
        im = imgs[nome]
        esc = 6
        big = im.resize((im.width * esc, im.height * esc), Image.NEAREST)
        if x + big.width > 1190:
            x, y = 10, y + 230
        folha.alpha_composite(big, (x, y))
        x += big.width + 16
    est_p = imgs["estalagmite"].resize((38 * 2, 142 * 2), Image.NEAREST)
    folha.alpha_composite(est_p, (1110, 10))
    plat = Image.open(os.path.join(ART, "Sprites", "Cenario", "plataforma_dissolvivel.png")).resize((200, 16), Image.NEAREST)
    folha.alpha_composite(plat.resize((800, 64), Image.NEAREST), (10, 480))
    folha.alpha_composite(amostra_fonte("7 Hell's - Você Venceu! Pausado ÁÉÍÓÚ ãõç 0123456789"), (10, 560))
    folha.alpha_composite(fundo.resize((378, 199), Image.NEAREST), (10, 610 - 50 + 40))
    folha.alpha_composite(imgs["menu"].resize((240, 135), Image.NEAREST), (400, 600))
    folha.save(os.path.join(DOCS, "pixelart_preview.png"))
    print("  ok Docs/pixelart_preview.png")


if __name__ == "__main__":
    main()
