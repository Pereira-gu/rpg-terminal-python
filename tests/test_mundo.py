"""Testes da masmorra: geração dos andares e efeitos das salas."""

import random

import pytest

from rpg import mundo
from rpg.mundo import Sala
from rpg.personagem import criar_heroi


class DadoViciado:
    """randint devolve sempre o menor valor possível; random devolve o valor escolhido."""

    def __init__(self, chance: float = 0.99):
        self.chance = chance

    def randint(self, a: int, b: int) -> int:
        return a

    def random(self) -> float:
        return self.chance


@pytest.mark.parametrize("semente", range(20))  # roda o teste com 20 mapas diferentes
def test_todo_andar_tem_exatamente_um_combate(semente):
    masmorra = mundo.gerar_masmorra(random.Random(semente))
    assert len(masmorra) == mundo.ANDARES
    for portas in masmorra:
        assert [s.tipo for s in portas].count("combate") == 1


def test_monstros_ficam_mais_fortes_no_fundo():
    assert mundo.inimigo_do_andar(1) == "rato"
    assert mundo.inimigo_do_andar(mundo.ANDARES) == "goblin"


def test_tesouro_da_ouro():
    heroi = criar_heroi("Teste")
    ouro_antes = heroi.ouro
    r = mundo.resolver_sala(Sala("tesouro"), heroi, DadoViciado())
    assert r.valor == mundo.OURO_TESOURO[0]
    assert heroi.ouro == ouro_antes + r.valor


def test_fonte_cura_sem_passar_do_maximo():
    heroi = criar_heroi("Teste")
    heroi.receber_dano(5)
    r = mundo.resolver_sala(Sala("fonte"), heroi, DadoViciado())
    assert heroi.vida == heroi.vida_max
    assert r.valor == 5


def test_armadilha_causa_dano():
    heroi = criar_heroi("Teste")
    r = mundo.resolver_sala(Sala("armadilha"), heroi, DadoViciado(chance=0.99))
    assert not r.esquivou
    assert heroi.vida == heroi.vida_max - mundo.DANO_ARMADILHA[0]


def test_armadilha_pode_ser_esquivada():
    heroi = criar_heroi("Teste")
    r = mundo.resolver_sala(Sala("armadilha"), heroi, DadoViciado(chance=0.0))
    assert r.esquivou
    assert heroi.vida == heroi.vida_max


def test_tesouro_e_armadilha_tem_a_mesma_pista():
    assert Sala("tesouro").pista == Sala("armadilha").pista
