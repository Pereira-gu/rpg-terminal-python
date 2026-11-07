"""Gera imagens SVG das telas do jogo para o README.

O rich consegue "gravar" tudo que foi impresso e exportar como SVG.
Aqui montamos um momento de jogo de mentira (sem input) e salvamos a imagem.

Como rodar (na pasta do projeto):
    python -m ferramentas.capturar_tela
"""

from pathlib import Path

from rich.console import Console

from rpg import interface, mundo
from rpg.combate import Resultado
from rpg.itens import CATALOGO
from rpg.personagem import criar_heroi, criar_inimigo

PASTA_DOCS = Path(__file__).resolve().parent.parent / "docs"


def novo_console() -> Console:
    # Troca o console da interface por um que grava. Como as funções da interface
    # usam a variável global "console" do módulo, elas passam a imprimir aqui.
    interface.console = Console(record=True, width=84, force_terminal=True, color_system="truecolor")
    return interface.console


def tela_combate() -> None:
    console = novo_console()
    heroi = criar_heroi("Aldric")
    heroi.ganhar_xp(30)
    heroi.arma, heroi.armadura = CATALOGO[2], CATALOGO[4]  # machado e cota de malha
    heroi.receber_dano(38)
    heroi.pocoes = 2
    dragao = criar_inimigo("dragao")
    dragao.receber_dano(61)
    dragao.enfurecido, dragao.ataque = True, dragao.ataque + 5
    dragao.preparando = True
    log = [
        interface.texto(Resultado("Aldric", "atacar", "Dragão Ancestral", 22, critico=True)),
        interface.texto(Resultado("Dragão Ancestral", "preparar", detalhe="sopro de fogo")),
    ]
    interface.tela_turno(heroi, dragao, "Covil do Dragão", 7, log)
    interface.mostrar_menu(heroi)
    console.print("Sua ação: [bold]2[/]")
    console.save_svg(str(PASTA_DOCS / "tela_combate.svg"), title="Masmorra de Pedra")


def tela_portas() -> None:
    console = novo_console()
    heroi = criar_heroi("Aldric")
    heroi.ganhar_xp(12)
    heroi.ouro = 35
    heroi.receber_dano(14)
    portas = (mundo.Sala("tesouro"), mundo.Sala("combate", "goblin"))
    interface.mostrar_portas(heroi, 3, mundo.ANDARES, portas)
    console.print("Qual porta: [bold]1[/]")
    console.save_svg(str(PASTA_DOCS / "tela_portas.svg"), title="Masmorra de Pedra")


if __name__ == "__main__":
    PASTA_DOCS.mkdir(exist_ok=True)
    tela_combate()
    tela_portas()
    print(f"Telas salvas em {PASTA_DOCS}")
