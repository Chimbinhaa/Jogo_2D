"""
Gera todos os efeitos sonoros do jogo (estilo 8 bits / chiptune), sem precisar de
nenhum programa de audio: so Python puro (modulos math, random, wave e struct).

Uso (na raiz do projeto):
    python Tools/Audio/gerar_sons.py

Os .wav vao para Assets/Audio/Resources/Sons/ (a pasta "Resources" deixa o script
Sons.cs carregar os sons pelo nome, sem precisar arrastar nada na Unity).
"""
import math
import os
import random
import struct
import wave

TAXA = 22050  # amostras por segundo
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PASTA = os.path.join(RAIZ, "Assets", "Audio", "Resources", "Sons")

random.seed(7)  # sempre gera os mesmos sons


# ---------------------------------------------------------------------------
# Blocos basicos
# ---------------------------------------------------------------------------
def quadrada(fase, ciclo=0.5):
    return 1.0 if (fase % 1.0) < ciclo else -1.0


def triangulo(fase):
    f = fase % 1.0
    return 4 * f - 1 if f < 0.5 else 3 - 4 * f


def ruido():
    return random.uniform(-1, 1)


def envelope(t, dur, ataque=0.005, queda=1.0):
    """Sobe rapido e cai ate zero no fim (queda > 1 = cai mais rapido)."""
    if t < ataque:
        return t / ataque
    return max(0.0, 1 - (t - ataque) / (dur - ataque)) ** queda


def tom(dur, f0, f1=None, onda="quadrada", ciclo=0.5, vol=0.5, queda=1.0, vibrato=0.0):
    """Nota com frequencia indo de f0 ate f1 (varredura)."""
    f1 = f0 if f1 is None else f1
    n = int(dur * TAXA)
    fase = 0.0
    out = []
    for i in range(n):
        t = i / TAXA
        f = f0 + (f1 - f0) * (t / dur)
        if vibrato:
            f *= 1 + 0.03 * math.sin(2 * math.pi * vibrato * t)
        fase += f / TAXA
        s = quadrada(fase, ciclo) if onda == "quadrada" else triangulo(fase)
        out.append(s * vol * envelope(t, dur, queda=queda))
    return out


def chiado(dur, vol=0.5, queda=2.0, grave=0.0, picotado=0):
    """Ruido. 'grave' (0-0.95) abafa o som; 'picotado' cria estalos de pedra."""
    n = int(dur * TAXA)
    out, ant = [], 0.0
    corte = 1.0
    for i in range(n):
        t = i / TAXA
        if picotado and i % (TAXA // picotado) == 0:
            corte = random.choice([0.0, 0.3, 1.0, 1.0])
        ant = ant * grave + ruido() * (1 - grave)
        out.append(ant * vol * corte * envelope(t, dur, queda=queda))
    return out


def mix(*faixas):
    n = max(len(f) for f in faixas)
    return [sum(f[i] for f in faixas if i < len(f)) for i in range(n)]


def seguida(*partes):
    out = []
    for p in partes:
        out += p
    return out


def silencio(dur):
    return [0.0] * int(dur * TAXA)


def nota(nome):
    """'C5' -> frequencia em Hz."""
    idx = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}[nome[0]]
    oit = int(nome[-1])
    if "#" in nome:
        idx += 1
    return 440.0 * 2 ** ((idx + (oit - 4) * 12) / 12)


def salvar(nome, amostras):
    os.makedirs(PASTA, exist_ok=True)
    pico = max(1e-9, max(abs(s) for s in amostras))
    ganho = min(1.0, 0.9 / pico)
    caminho = os.path.join(PASTA, nome + ".wav")
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(b"".join(struct.pack("<h", int(s * ganho * 32767)) for s in amostras))
    print("  ok", os.path.relpath(caminho, RAIZ), f"({len(amostras) / TAXA:.2f}s)")


# ---------------------------------------------------------------------------
# Efeitos
# ---------------------------------------------------------------------------
def som_pulo():
    return tom(0.16, 260, 720, ciclo=0.25, vol=0.45, queda=1.5)


def som_aterrissar():
    return mix(chiado(0.09, vol=0.6, grave=0.85, queda=2.5), tom(0.07, 120, 60, onda="tri", vol=0.5))


def som_morte():
    queda = tom(0.7, 520, 70, ciclo=0.5, vol=0.4, queda=0.8, vibrato=14)
    batida = chiado(0.25, vol=0.5, grave=0.6, queda=2)
    return mix(seguida(tom(0.06, 880, 880, vol=0.35), queda), batida)


def som_plataforma():
    # pedra rachando e desmoronando
    return mix(chiado(0.45, vol=0.55, grave=0.7, queda=1.2, picotado=40),
               tom(0.3, 180, 90, onda="tri", vol=0.25))


def som_fase():
    notas = ["C5", "E5", "G5", "C6"]
    return seguida(*[tom(0.08, nota(n), ciclo=0.25, vol=0.35, queda=0.6) for n in notas[:-1]],
                   tom(0.3, nota(notas[-1]), ciclo=0.25, vol=0.4, queda=1.2))


def som_vitoria():
    mel = [("G4", 0.1), ("C5", 0.1), ("E5", 0.1), ("G5", 0.2), ("E5", 0.1), ("G5", 0.5)]
    voz = seguida(*[tom(d, nota(n), ciclo=0.25, vol=0.35, queda=0.5) for n, d in mel])
    baixo = seguida(tom(0.3, nota("C3"), onda="tri", vol=0.4, queda=0.5),
                    tom(0.3, nota("G3"), onda="tri", vol=0.4, queda=0.5),
                    tom(0.5, nota("C3"), onda="tri", vol=0.45, queda=1))
    brilho = seguida(silencio(0.6), tom(0.5, nota("C6"), ciclo=0.125, vol=0.15, queda=1.5, vibrato=6))
    return mix(voz, baixo, brilho)


def som_clique():
    return seguida(tom(0.03, 980, vol=0.35, ciclo=0.25), tom(0.04, 1470, vol=0.25, ciclo=0.25, queda=2))


def som_pause():
    return seguida(tom(0.06, nota("E5"), vol=0.3, ciclo=0.25), tom(0.1, nota("B4"), vol=0.3, ciclo=0.25, queda=1.5))


SONS = {
    "pulo": som_pulo,
    "aterrissar": som_aterrissar,
    "morte": som_morte,
    "plataforma": som_plataforma,
    "fase": som_fase,
    "vitoria": som_vitoria,
    "clique": som_clique,
    "pause": som_pause,
}

if __name__ == "__main__":
    print("Gerando sons em", PASTA)
    for nome, func in SONS.items():
        salvar(nome, func())
