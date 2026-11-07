"""Testes de XP e subida de nível."""

from rpg.personagem import BONUS_POR_NIVEL, XP_POR_NIVEL, criar_heroi


def test_xp_abaixo_do_necessario_nao_sobe_nivel():
    heroi = criar_heroi("Teste")
    subidas = heroi.ganhar_xp(XP_POR_NIVEL - 1)
    assert subidas == []
    assert heroi.nivel == 1
    assert heroi.xp == XP_POR_NIVEL - 1


def test_sobe_nivel_e_guarda_a_sobra():
    heroi = criar_heroi("Teste")
    heroi.ganhar_xp(12)  # precisa de 10: sobe e sobram 2
    assert heroi.nivel == 2
    assert heroi.xp == 2
    assert heroi.xp_para_proximo == 20


def test_subir_nivel_aumenta_atributos():
    heroi = criar_heroi("Teste")
    vida, ataque, defesa = heroi.vida_max, heroi.ataque, heroi.defesa
    heroi.ganhar_xp(XP_POR_NIVEL)
    assert heroi.vida_max == vida + BONUS_POR_NIVEL["vida_max"]
    assert heroi.ataque == ataque + BONUS_POR_NIVEL["ataque"]
    assert heroi.defesa == defesa + BONUS_POR_NIVEL["defesa"]


def test_cura_da_subida_nao_passa_do_maximo():
    heroi = criar_heroi("Teste")  # vida cheia
    subida = heroi.ganhar_xp(XP_POR_NIVEL)[0]
    assert heroi.vida == heroi.vida_max
    assert subida.curado == BONUS_POR_NIVEL["vida_max"]  # só os pontos novos de vida máxima


def test_subir_nivel_nao_apaga_o_dano_recebido():
    heroi = criar_heroi("Teste")
    heroi.receber_dano(30)  # 50 → 20
    heroi.ganhar_xp(XP_POR_NIVEL)
    assert heroi.vida == 20 + BONUS_POR_NIVEL["vida_max"]  # só os pontos novos


def test_muito_xp_sobe_varios_niveis():
    heroi = criar_heroi("Teste")
    subidas = heroi.ganhar_xp(10 + 20 + 5)  # nível 1→2 (10) e 2→3 (20), sobram 5
    assert [s.nivel for s in subidas] == [2, 3]
    assert heroi.nivel == 3
    assert heroi.xp == 5
