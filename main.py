"""Ponto de entrada do jogo: liga as regras (combate) com a tela (interface)."""

import random

from rpg import combate, interface
from rpg.personagem import Heroi, Inimigo, criar_heroi, criar_inimigo

SEQUENCIA_INIMIGOS = ["rato", "goblin", "orc"]


def batalha(heroi: Heroi, inimigo: Inimigo, numero: int, total: int, rng: random.Random) -> bool:
    """Roda uma batalha até alguém cair. Retorna True se o herói venceu."""
    turno = 1
    log: list[str] = []  # frases do último turno, mostradas no painel
    while heroi.vivo and inimigo.vivo:
        interface.tela_turno(heroi, inimigo, numero, total, turno, log)
        escolha = interface.escolher_acao(heroi)
        log = [interface.texto(combate.turno_heroi(heroi, inimigo, escolha, rng))]
        if inimigo.vivo:
            log.append(interface.texto(combate.turno_inimigo(inimigo, heroi, rng)))
        turno += 1

    # Mostra a tela uma última vez, para o jogador ver o golpe final.
    interface.tela_turno(heroi, inimigo, numero, total, turno, log)
    return heroi.vivo


def main() -> None:
    rng = random.Random()  # sem semente: cada partida é diferente
    interface.titulo()
    heroi = criar_heroi(interface.pedir_nome())

    for numero, tipo in enumerate(SEQUENCIA_INIMIGOS, start=1):
        inimigo = criar_inimigo(tipo)
        interface.anunciar_inimigo(inimigo, numero, len(SEQUENCIA_INIMIGOS))
        if not batalha(heroi, inimigo, numero, len(SEQUENCIA_INIMIGOS), rng):
            interface.fim_de_jogo(venceu=False, heroi=heroi)
            return
        subidas = heroi.ganhar_xp(inimigo.xp)
        interface.vitoria_batalha(inimigo, heroi, subidas)

    interface.fim_de_jogo(venceu=True, heroi=heroi)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # Ctrl+C sai sem mostrar erro feio
        interface.console.print("\n[dim]Até a próxima, aventureiro.[/]")
