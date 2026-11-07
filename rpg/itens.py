"""Itens à venda e a regra de compra.

Assim como o combate, este módulo não usa print nem input: comprar()
só devolve um código dizendo o que aconteceu, e a interface explica.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Só para as dicas de tipo. Importar Heroi "de verdade" criaria um ciclo:
    # personagem.py importa Item daqui, e itens.py importaria personagem.py.
    from rpg.personagem import Heroi

LIMITE_POCOES = 5


@dataclass(frozen=True)  # frozen: o item do catálogo não pode ser alterado sem querer
class Item:
    nome: str
    tipo: str  # "pocao", "arma" ou "armadura"
    bonus: int  # ataque (arma) ou defesa (armadura); poção não usa
    preco: int
    descricao: str


POCAO = Item("Poção de Cura", "pocao", 0, 12, "Mais uma poção na bolsa")

CATALOGO = [
    POCAO,
    Item("Espada de Ferro", "arma", 3, 25, "+3 de ataque"),
    Item("Machado de Guerra", "arma", 6, 55, "+6 de ataque"),
    Item("Gibão de Couro", "armadura", 2, 20, "+2 de defesa"),
    Item("Cota de Malha", "armadura", 4, 45, "+4 de defesa"),
]


def comprar(heroi: Heroi, item: Item) -> str:
    """Tenta comprar e retorna: "ok", "sem_ouro", "bolsa_cheia" ou "nao_melhora".

    As checagens vêm antes de mexer em qualquer coisa: se a compra não puder
    acontecer, o herói fica exatamente como estava.
    """
    if heroi.ouro < item.preco:
        return "sem_ouro"
    if item.tipo == "pocao" and heroi.pocoes >= LIMITE_POCOES:
        return "bolsa_cheia"
    if item.tipo in ("arma", "armadura"):
        atual = getattr(heroi, item.tipo)  # heroi.arma ou heroi.armadura
        if atual is not None and atual.bonus >= item.bonus:
            return "nao_melhora"

    heroi.ouro -= item.preco
    if item.tipo == "pocao":
        heroi.pocoes += 1
    else:
        setattr(heroi, item.tipo, item)  # equipa na hora; o item antigo é descartado
    return "ok"
