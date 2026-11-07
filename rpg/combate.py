"""Regras do combate por turnos.

Este módulo NÃO usa print nem input: ele só calcula e devolve resultados.
Quem mostra na tela é o interface.py. Essa separação permite testar as
regras sem precisar jogar.

O sorteio vem de um objeto `rng` (random.Random) recebido como parâmetro.
No jogo passamos um sorteio de verdade; nos testes passamos um "dado viciado"
para saber exatamente o que vai acontecer.
"""

import random
from dataclasses import dataclass

from rpg.personagem import Heroi, Personagem

CHANCE_CRITICO = 0.10  # 10% de chance de dano dobrado
VARIACAO_DANO = 2  # o dano varia de -2 a +2 a cada golpe
CURA_POCAO = 20


@dataclass
class Resultado:
    """O que aconteceu em uma ação, para a interface descrever."""

    ator: str
    acao: str  # "atacar", "defender", "pocao" ou "sem_pocao"
    alvo: str = ""
    valor: int = 0  # dano causado ou vida curada
    critico: bool = False


def calcular_dano(atacante: Personagem, defensor: Personagem, rng: random.Random) -> tuple[int, bool]:
    """Retorna (dano, foi_critico). O dano mínimo é 1, para todo golpe contar."""
    dano = atacante.ataque + rng.randint(-VARIACAO_DANO, VARIACAO_DANO)
    critico = rng.random() < CHANCE_CRITICO
    if critico:
        dano *= 2
    dano -= defensor.defesa
    if defensor.defendendo:
        dano //= 2  # defender corta o dano pela metade
    return max(1, dano), critico


def atacar(atacante: Personagem, defensor: Personagem, rng: random.Random) -> Resultado:
    dano, critico = calcular_dano(atacante, defensor, rng)
    defensor.receber_dano(dano)
    return Resultado(atacante.nome, "atacar", defensor.nome, dano, critico)


def defender(personagem: Personagem) -> Resultado:
    # Fica defendendo até o começo do próximo turno dele.
    personagem.defendendo = True
    return Resultado(personagem.nome, "defender")


def usar_pocao(heroi: Heroi) -> Resultado:
    if heroi.pocoes <= 0:
        return Resultado(heroi.nome, "sem_pocao")
    heroi.pocoes -= 1
    curado = heroi.curar(CURA_POCAO)
    return Resultado(heroi.nome, "pocao", valor=curado)


def turno_heroi(heroi: Heroi, inimigo: Personagem, escolha: str, rng: random.Random) -> Resultado:
    """Executa a ação escolhida pelo jogador."""
    heroi.defendendo = False  # a defesa do turno anterior acaba aqui
    if escolha == "atacar":
        return atacar(heroi, inimigo, rng)
    if escolha == "defender":
        return defender(heroi)
    if escolha == "pocao":
        return usar_pocao(heroi)
    raise ValueError(f"Ação desconhecida: {escolha}")


def turno_inimigo(inimigo: Personagem, heroi: Heroi, rng: random.Random) -> Resultado:
    """Por enquanto o inimigo sempre ataca. Na etapa 5 o chefe terá um ataque especial."""
    inimigo.defendendo = False
    return atacar(inimigo, heroi, rng)
