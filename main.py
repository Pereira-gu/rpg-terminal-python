"""Ponto de entrada do jogo: liga as regras (combate, itens, mundo) com a tela (interface)."""

import random

from rpg import combate, interface, itens, mundo
from rpg.combate import Estatisticas
from rpg.personagem import Heroi, Inimigo, criar_heroi, criar_inimigo

CHEFE = "dragao"


def batalha(heroi: Heroi, inimigo: Inimigo, local: str, est: Estatisticas, rng: random.Random) -> bool:
    """Roda uma batalha até alguém cair. Retorna True se o herói venceu."""
    turno = 1
    log: list[str] = []  # frases do último turno, mostradas no painel
    while heroi.vivo and inimigo.vivo:
        interface.tela_turno(heroi, inimigo, local, turno, log)
        escolha = interface.escolher_acao(heroi)
        r_heroi = combate.turno_heroi(heroi, inimigo, escolha, rng)
        est.registrar(r_heroi, do_heroi=True)
        log = [interface.texto(r_heroi)]
        if inimigo.vivo:
            r_inimigo = combate.turno_inimigo(inimigo, heroi, rng)
            est.registrar(r_inimigo, do_heroi=False)
            log.append(interface.texto(r_inimigo))
        est.turnos += 1
        turno += 1

    # Mostra a tela uma última vez, para o jogador ver o golpe final.
    interface.tela_turno(heroi, inimigo, local, turno, log)
    return heroi.vivo


def lutar(heroi: Heroi, tipo_inimigo: str, local: str, est: Estatisticas, rng: random.Random) -> bool:
    """Apresenta o inimigo, luta e entrega as recompensas."""
    inimigo = criar_inimigo(tipo_inimigo)
    interface.anunciar_inimigo(inimigo, local)
    if not batalha(heroi, inimigo, local, est, rng):
        return False
    est.monstros += 1
    heroi.ouro += inimigo.ouro
    subidas = heroi.ganhar_xp(inimigo.xp)
    if tipo_inimigo != CHEFE:  # depois do chefe vem direto a tela final
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


def entrar_na_sala(heroi: Heroi, sala: mundo.Sala, local: str, est: Estatisticas, rng: random.Random) -> bool:
    """Resolve a sala escolhida. Retorna False se o herói morreu."""
    if sala.tipo == "combate":
        return lutar(heroi, sala.inimigo, local, est, rng)
    if sala.tipo == "loja":
        visitar_loja(heroi)
        return True
    resultado = mundo.resolver_sala(sala, heroi, rng)
    if resultado.tipo == "armadilha":
        est.dano_sofrido += resultado.valor
    interface.mostrar_evento(resultado, heroi)
    return heroi.vivo  # uma armadilha também pode derrubar o herói


def jogar() -> None:
    """Uma partida completa, do nome do herói até a tela final."""
    rng = random.Random()  # sem semente: cada partida é diferente
    est = Estatisticas()
    interface.titulo()
    heroi = criar_heroi(interface.pedir_nome())
    masmorra = mundo.gerar_masmorra(rng)

    for andar, portas in enumerate(masmorra, start=1):
        local = f"Andar {andar}/{len(masmorra)}"
        sala = interface.escolher_porta(heroi, andar, len(masmorra), portas)
        if not entrar_na_sala(heroi, sala, local, est, rng):
            interface.fim_de_jogo(False, heroi, est, local)
            return

    # Antes do chefe: um acampamento com loja garantida.
    interface.chegada_ao_chefe()
    visitar_loja(heroi)
    local = "Covil do Dragão"
    venceu = lutar(heroi, CHEFE, local, est, rng)
    interface.fim_de_jogo(venceu, heroi, est, local)


def main() -> None:
    while True:
        jogar()
        if not interface.jogar_de_novo():
            interface.console.print("[dim]Até a próxima, aventureiro.[/]")
            return


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):  # Ctrl+C (ou fim da entrada) sai sem erro feio
        interface.console.print("\n[dim]Até a próxima, aventureiro.[/]")
