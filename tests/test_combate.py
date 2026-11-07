"""Testes das regras de combate.

DadoViciado substitui o random: sempre "sorteia" os valores que mandarmos.
Assim cada teste sabe exatamente qual deve ser o resultado.
"""

import pytest

from rpg import combate
from rpg.personagem import criar_heroi, criar_inimigo


class DadoViciado:
    def __init__(self, variacao: int = 0, chance: float = 0.99):
        self.variacao = variacao  # o que randint devolve
        self.chance = chance  # o que random devolve (0.99 = nunca crítico)

    def randint(self, a: int, b: int) -> int:
        return self.variacao

    def random(self) -> float:
        return self.chance


def test_dano_normal_desconta_defesa():
    heroi, goblin = criar_heroi("Teste"), criar_inimigo("goblin")
    dano, critico = combate.calcular_dano(heroi, goblin, DadoViciado())
    assert dano == heroi.ataque - goblin.defesa  # 10 - 2 = 8
    assert not critico


def test_critico_dobra_o_dano_antes_da_defesa():
    heroi, goblin = criar_heroi("Teste"), criar_inimigo("goblin")
    dano, critico = combate.calcular_dano(heroi, goblin, DadoViciado(chance=0.0))
    assert dano == heroi.ataque * 2 - goblin.defesa  # 20 - 2 = 18
    assert critico


def test_defender_bloqueia_75_por_cento():
    heroi, orc = criar_heroi("Teste"), criar_inimigo("orc")
    combate.defender(heroi)
    dano, _ = combate.calcular_dano(orc, heroi, DadoViciado())
    assert dano == max(1, (orc.ataque - heroi.defesa) // combate.REDUCAO_DEFESA)  # 6 // 4 = 1


def test_inimigo_prepara_golpe_pesado():
    heroi, orc = criar_heroi("Teste"), criar_inimigo("orc")
    resultado = combate.turno_inimigo(orc, heroi, DadoViciado(chance=0.0))
    assert resultado.acao == "preparar"
    assert orc.preparando
    assert heroi.vida == heroi.vida_max  # preparar não causa dano


def test_golpe_pesado_dobra_a_forca_e_zera_preparo():
    heroi, orc = criar_heroi("Teste"), criar_inimigo("orc")
    orc.preparando = True
    resultado = combate.turno_inimigo(orc, heroi, DadoViciado())
    assert resultado.acao == "golpe_pesado"
    assert resultado.valor == orc.ataque * 2 - heroi.defesa
    assert not orc.preparando


def test_defender_contra_golpe_pesado_compensa():
    heroi, orc = criar_heroi("Teste"), criar_inimigo("orc")
    orc.preparando = True
    combate.defender(heroi)
    resultado = combate.turno_inimigo(orc, heroi, DadoViciado())
    assert resultado.valor == (orc.ataque * 2 - heroi.defesa) // combate.REDUCAO_DEFESA


def test_dano_minimo_e_1():
    rato, heroi = criar_inimigo("rato"), criar_heroi("Teste")
    heroi.defesa = 100
    dano, _ = combate.calcular_dano(rato, heroi, DadoViciado())
    assert dano == 1


def test_vida_nunca_fica_negativa():
    rato = criar_inimigo("rato")
    rato.receber_dano(999)
    assert rato.vida == 0
    assert not rato.vivo


def test_pocao_cura_sem_passar_do_maximo():
    heroi = criar_heroi("Teste")
    heroi.receber_dano(5)
    resultado = combate.usar_pocao(heroi)
    assert heroi.vida == heroi.vida_max
    assert resultado.valor == 5  # curou só o que faltava
    assert heroi.pocoes == 2


def test_sem_pocao_nao_cura():
    heroi = criar_heroi("Teste")
    heroi.pocoes = 0
    heroi.receber_dano(10)
    resultado = combate.usar_pocao(heroi)
    assert resultado.acao == "sem_pocao"
    assert heroi.vida == heroi.vida_max - 10


def test_defesa_acaba_no_turno_seguinte_do_heroi():
    heroi, rato = criar_heroi("Teste"), criar_inimigo("rato")
    combate.turno_heroi(heroi, rato, "defender", DadoViciado())
    assert heroi.defendendo
    combate.turno_heroi(heroi, rato, "atacar", DadoViciado())
    assert not heroi.defendendo


def test_acao_invalida_gera_erro():
    heroi, rato = criar_heroi("Teste"), criar_inimigo("rato")
    with pytest.raises(ValueError):
        combate.turno_heroi(heroi, rato, "dançar", DadoViciado())
