"""Testes da loja e do equipamento."""

from rpg.itens import CATALOGO, LIMITE_POCOES, POCAO, comprar
from rpg.personagem import criar_heroi

ESPADA, MACHADO, GIBAO = CATALOGO[1], CATALOGO[2], CATALOGO[3]


def test_compra_desconta_ouro_e_equipa():
    heroi = criar_heroi("Teste")
    heroi.ouro = 100
    assert comprar(heroi, ESPADA) == "ok"
    assert heroi.ouro == 100 - ESPADA.preco
    assert heroi.arma == ESPADA


def test_sem_ouro_nao_muda_nada():
    heroi = criar_heroi("Teste")
    heroi.ouro = ESPADA.preco - 1
    assert comprar(heroi, ESPADA) == "sem_ouro"
    assert heroi.ouro == ESPADA.preco - 1
    assert heroi.arma is None


def test_equipamento_soma_no_ataque_e_defesa_totais():
    heroi = criar_heroi("Teste")
    heroi.ouro = 100
    comprar(heroi, ESPADA)
    comprar(heroi, GIBAO)
    assert heroi.ataque_total == heroi.ataque + ESPADA.bonus
    assert heroi.defesa_total == heroi.defesa + GIBAO.bonus


def test_nao_compra_arma_pior_ou_igual():
    heroi = criar_heroi("Teste")
    heroi.ouro = 200
    comprar(heroi, MACHADO)
    assert comprar(heroi, ESPADA) == "nao_melhora"
    assert comprar(heroi, MACHADO) == "nao_melhora"
    assert heroi.arma == MACHADO


def test_arma_melhor_substitui_a_atual():
    heroi = criar_heroi("Teste")
    heroi.ouro = 200
    comprar(heroi, ESPADA)
    assert comprar(heroi, MACHADO) == "ok"
    assert heroi.arma == MACHADO


def test_pocao_respeita_o_limite_da_bolsa():
    heroi = criar_heroi("Teste")
    heroi.ouro = 500
    heroi.pocoes = LIMITE_POCOES - 1
    assert comprar(heroi, POCAO) == "ok"
    assert heroi.pocoes == LIMITE_POCOES
    assert comprar(heroi, POCAO) == "bolsa_cheia"
    assert heroi.pocoes == LIMITE_POCOES
