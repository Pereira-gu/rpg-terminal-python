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

from rpg.personagem import Heroi, Inimigo, Personagem

CHANCE_CRITICO = 0.10  # 10% de chance de dano dobrado
VARIACAO_DANO = 2  # o dano varia de -2 a +2 a cada golpe
CURA_POCAO = 20
REDUCAO_DEFESA = 4  # defendendo, o dano é dividido por 4 (bloqueia 75%)
BONUS_FURIA = 5  # ataque extra do monstro enfurecido
# A chance e a força do golpe pesado agora ficam em cada Inimigo (personagem.py).


@dataclass
class Resultado:
    """O que aconteceu em uma ação, para a interface descrever."""

    ator: str
    acao: str  # "atacar", "defender", "pocao", "sem_pocao", "preparar", "golpe_pesado" ou "furia"
    alvo: str = ""
    valor: int = 0  # dano causado ou vida curada
    critico: bool = False
    detalhe: str = ""  # nome do golpe pesado ("sopro de fogo", por exemplo)


@dataclass
class Estatisticas:
    """Números da partida, mostrados na tela final."""

    monstros: int = 0
    turnos: int = 0
    dano_causado: int = 0
    dano_sofrido: int = 0
    pocoes_usadas: int = 0

    def registrar(self, r: Resultado, nome_heroi: str) -> None:
        if r.acao in ("atacar", "golpe_pesado"):
            if r.ator == nome_heroi:
                self.dano_causado += r.valor
            else:
                self.dano_sofrido += r.valor
        elif r.acao == "pocao":
            self.pocoes_usadas += 1


def calcular_dano(
    atacante: Personagem, defensor: Personagem, rng: random.Random, multiplicador: int = 1
) -> tuple[int, bool]:
    """Retorna (dano, foi_critico). O dano mínimo é 1, para todo golpe contar."""
    dano = (atacante.ataque_total + rng.randint(-VARIACAO_DANO, VARIACAO_DANO)) * multiplicador
    critico = rng.random() < CHANCE_CRITICO
    if critico:
        dano *= 2
    dano -= defensor.defesa_total
    if defensor.defendendo:
        dano //= REDUCAO_DEFESA
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


def turno_inimigo(inimigo: Inimigo, heroi: Heroi, rng: random.Random) -> Resultado:
    """Decide e executa a ação do inimigo, nesta ordem de prioridade:

    1. soltar o golpe pesado que estava preparando;
    2. entrar em fúria, se tem fúria e caiu para metade da vida (gasta o turno);
    3. com alguma chance, preparar um golpe pesado (anunciado um turno antes);
    4. atacar normalmente.
    """
    if inimigo.preparando:
        inimigo.preparando = False
        dano, critico = calcular_dano(inimigo, heroi, rng, inimigo.multiplicador_pesado)
        heroi.receber_dano(dano)
        return Resultado(inimigo.nome, "golpe_pesado", heroi.nome, dano, critico, inimigo.nome_golpe)

    if inimigo.furia and not inimigo.enfurecido and inimigo.vida <= inimigo.vida_max // 2:
        inimigo.enfurecido = True
        inimigo.ataque += BONUS_FURIA
        return Resultado(inimigo.nome, "furia", valor=BONUS_FURIA)

    if rng.random() < inimigo.chance_preparar:
        inimigo.preparando = True
        return Resultado(inimigo.nome, "preparar", detalhe=inimigo.nome_golpe)

    return atacar(inimigo, heroi, rng)
