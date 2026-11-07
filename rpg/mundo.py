"""A masmorra: andares, portas e o que acontece em cada sala.

Cada andar tem duas portas. Uma sempre leva a um combate (XP e ouro garantidos);
a outra é uma surpresa: tesouro, fonte de cura, loja... ou uma armadilha.
Tesouro e armadilha têm a MESMA pista, então escolher a porta tranquila também é um risco.

Como nos outros módulos de regra, nada aqui usa print ou input.
"""

import random
from dataclasses import dataclass

from rpg.personagem import Heroi

ANDARES = 5
OURO_TESOURO = (10, 25)  # sorteado entre esses valores
CURA_FONTE = 0.30  # a fonte cura 30% da vida máxima
DANO_ARMADILHA = (6, 12)
CHANCE_ESQUIVA = 0.40

# Peso de cada surpresa: o tesouro sai com mais frequência que a loja, por exemplo.
PESOS_SURPRESA = {"tesouro": 3, "armadilha": 2, "fonte": 2, "loja": 1}

PISTAS = {
    "combate": "Rosnados e cheiro de sangue...",
    "tesouro": "Um brilho dourado no escuro...",
    "armadilha": "Um brilho dourado no escuro...",  # igual ao tesouro, de propósito
    "fonte": "Som de água corrente...",
    "loja": "Uma lamparina acesa e alguém assobiando...",
}


@dataclass(frozen=True)
class Sala:
    tipo: str  # "combate", "tesouro", "armadilha", "fonte" ou "loja"
    inimigo: str = ""  # só para combate: chave em MODELOS_INIMIGOS

    @property
    def pista(self) -> str:
        return PISTAS[self.tipo]


@dataclass
class ResultadoSala:
    tipo: str
    valor: int = 0  # ouro ganho, vida curada ou dano sofrido
    esquivou: bool = False


def inimigo_do_andar(andar: int) -> str:
    """Quanto mais fundo, mais forte o monstro."""
    if andar <= 2:
        return "rato"
    if andar <= 4:
        return "goblin"
    return "orc"


def gerar_masmorra(rng: random.Random, andares: int = ANDARES) -> list[tuple[Sala, Sala]]:
    """Sorteia os andares. Cada um vira um par (porta 1, porta 2)."""
    masmorra = []
    for andar in range(1, andares + 1):
        combate = Sala("combate", inimigo_do_andar(andar))
        tipo = rng.choices(list(PESOS_SURPRESA), weights=list(PESOS_SURPRESA.values()))[0]
        surpresa = Sala(tipo)
        # Sorteia o lado, para o combate não ficar sempre na mesma porta.
        masmorra.append((combate, surpresa) if rng.random() < 0.5 else (surpresa, combate))
    return masmorra


def resolver_sala(sala: Sala, heroi: Heroi, rng: random.Random) -> ResultadoSala:
    """Aplica o efeito das salas sem combate e sem loja (essas o main.py trata)."""
    if sala.tipo == "tesouro":
        ouro = rng.randint(*OURO_TESOURO)  # o * "abre" a tupla: randint(10, 25)
        heroi.ouro += ouro
        return ResultadoSala("tesouro", ouro)

    if sala.tipo == "fonte":
        curado = heroi.curar(round(heroi.vida_max * CURA_FONTE))
        return ResultadoSala("fonte", curado)

    if sala.tipo == "armadilha":
        if rng.random() < CHANCE_ESQUIVA:
            return ResultadoSala("armadilha", 0, esquivou=True)
        dano = heroi.receber_dano(rng.randint(*DANO_ARMADILHA))
        return ResultadoSala("armadilha", dano)

    raise ValueError(f"Sala sem efeito direto: {sala.tipo}")
