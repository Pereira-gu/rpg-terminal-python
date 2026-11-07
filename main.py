"""Ponto de entrada do jogo: liga as regras (combate, itens, mundo) com a tela (interface)."""

import random

from rpg import combate, interface, itens, mundo
from rpg.personagem import Heroi, Inimigo, criar_heroi, criar_inimigo

CHEFE = "orc"  # na etapa 5 vira o dragão


def batalha(heroi: Heroi, inimigo: Inimigo, local: str, rng: random.Random) -> bool:
    """Roda uma batalha até alguém cair. Retorna True se o herói venceu."""
    turno = 1
    log: list[str] = []  # frases do último turno, mostradas no painel
    while heroi.vivo and inimigo.vivo:
        interface.tela_turno(heroi, inimigo, local, turno, log)
        escolha = interface.escolher_acao(heroi)
        log = [interface.texto(combate.turno_heroi(heroi, inimigo, escolha, rng))]
        if inimigo.vivo:
            log.append(interface.texto(combate.turno_inimigo(inimigo, heroi, rng)))
        turno += 1

    # Mostra a tela uma última vez, para o jogador ver o golpe final.
    interface.tela_turno(heroi, inimigo, local, turno, log)
    return heroi.vivo


def lutar(heroi: Heroi, tipo_inimigo: str, local: str, rng: random.Random) -> bool:
    """Apresenta o inimigo, luta e entrega as recompensas."""
    inimigo = criar_inimigo(tipo_inimigo)
    interface.anunciar_inimigo(inimigo, local)
    if not batalha(heroi, inimigo, local, rng):
        return False
    heroi.ouro += inimigo.ouro
    subidas = heroi.ganhar_xp(inimigo.xp)
    interface.vitoria_batalha(inimigo, heroi, subidas)
    return True


def visitar_loja(heroi: Heroi) -> None:
    """Fica na loja até o jogador escolher sair."""
    mensagem = ""
    while True:
        item = interface.tela_loja(heroi, itens.CATALOGO, mensagem)
        if item is None:
            return
        mensagem = interface.texto_compra(itens.comprar(heroi, item), item)


def entrar_na_sala(heroi: Heroi, sala: mundo.Sala, local: str, rng: random.Random) -> bool:
    """Resolve a sala escolhida. Retorna False se o herói morreu."""
    if sala.tipo == "combate":
        return lutar(heroi, sala.inimigo, local, rng)
    if sala.tipo == "loja":
        visitar_loja(heroi)
        return True
    interface.mostrar_evento(mundo.resolver_sala(sala, heroi, rng), heroi)
    return heroi.vivo  # uma armadilha também pode derrubar o herói


def main() -> None:
    rng = random.Random()  # sem semente: cada partida é diferente
    interface.titulo()
    heroi = criar_heroi(interface.pedir_nome())
    masmorra = mundo.gerar_masmorra(rng)

    for andar, portas in enumerate(masmorra, start=1):
        sala = interface.escolher_porta(heroi, andar, len(masmorra), portas)
        if not entrar_na_sala(heroi, sala, f"Andar {andar}/{len(masmorra)}", rng):
            interface.fim_de_jogo(venceu=False, heroi=heroi)
            return

    # Antes do chefe: um acampamento com loja garantida.
    interface.chegada_ao_chefe()
    visitar_loja(heroi)
    venceu = lutar(heroi, CHEFE, "Covil do chefe", rng)
    interface.fim_de_jogo(venceu=venceu, heroi=heroi)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:  # Ctrl+C sai sem mostrar erro feio
        interface.console.print("\n[dim]Até a próxima, aventureiro.[/]")
