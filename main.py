"""Ponto de entrada do jogo: liga as regras (combate) com a tela (interface)."""

import random

from rpg import combate, interface
from rpg.personagem import Heroi, Inimigo, criar_heroi, criar_inimigo

SEQUENCIA_INIMIGOS = ["rato", "goblin", "orc"]


def batalha(heroi: Heroi, inimigo: Inimigo, rng: random.Random) -> bool:
    """Roda uma batalha até alguém cair. Retorna True se o herói venceu."""
    while heroi.vivo and inimigo.vivo:
        interface.mostrar_status(heroi, inimigo)
        escolha = interface.escolher_acao()
        interface.descrever(combate.turno_heroi(heroi, inimigo, escolha, rng))

        if inimigo.vivo:
            interface.descrever(combate.turno_inimigo(inimigo, heroi, rng))
    return heroi.vivo


def main() -> None:
    rng = random.Random()  # sem semente: cada partida é diferente
    interface.titulo()
    heroi = criar_heroi(interface.pedir_nome())

    for numero, tipo in enumerate(SEQUENCIA_INIMIGOS, start=1):
        inimigo = criar_inimigo(tipo)
        interface.anunciar_inimigo(inimigo, numero, len(SEQUENCIA_INIMIGOS))
        if not batalha(heroi, inimigo, rng):
            interface.fim_de_jogo(venceu=False, heroi=heroi)
            return
        interface.vitoria_batalha(inimigo)

    interface.fim_de_jogo(venceu=True, heroi=heroi)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # Ctrl+C sai sem mostrar erro feio
        interface.console.print("\n[dim]Até a próxima, aventureiro.[/]")
