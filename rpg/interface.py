"""Tudo que aparece na tela fica aqui, usando a biblioteca rich.

Se um dia quisermos trocar o visual (outra biblioteca ou uma versão web),
só este arquivo muda: as regras do jogo continuam iguais.
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from rpg.combate import Resultado
from rpg.personagem import Heroi, Inimigo, Personagem

console = Console()

# O jogador digita um número; o jogo trabalha com o nome da ação.
ACOES = {"1": "atacar", "2": "defender", "3": "pocao"}


def barra_vida(p: Personagem, largura: int = 20) -> str:
    """Desenha algo como ████████░░░░ 30/50, com cor conforme a vida restante."""
    proporcao = p.vida / p.vida_max
    cheios = round(proporcao * largura)
    cor = "green" if proporcao > 0.5 else "yellow" if proporcao > 0.25 else "red"
    return f"[{cor}]{'█' * cheios}[/][dim]{'░' * (largura - cheios)}[/] {p.vida}/{p.vida_max}"


def titulo() -> None:
    console.print(
        Panel.fit(
            "[bold yellow]⚔  MASMORRA DE PEDRA  ⚔[/]\n[dim]Um mini RPG de terminal[/]",
            border_style="yellow",
        )
    )


def pedir_nome() -> str:
    nome = Prompt.ask("[bold]Qual é o nome do seu herói?[/]", default="Aldric")
    return nome.strip() or "Aldric"


def anunciar_inimigo(inimigo: Inimigo, numero: int, total: int) -> None:
    console.rule(f"[bold red]Batalha {numero}/{total}: {inimigo.nome} aparece![/]")


def mostrar_status(heroi: Heroi, inimigo: Inimigo) -> None:
    tabela = Table(show_header=False, box=None, padding=(0, 2))
    tabela.add_row(f"[bold cyan]{heroi.nome}[/]", barra_vida(heroi), f"🧪 {heroi.pocoes}")
    tabela.add_row(f"[bold red]{inimigo.nome}[/]", barra_vida(inimigo), "")
    console.print(Panel(tabela, border_style="blue"))


def escolher_acao() -> str:
    console.print("[1] Atacar   [2] Defender   [3] Usar poção")
    numero = Prompt.ask("Sua ação", choices=list(ACOES), show_choices=False)
    return ACOES[numero]


def descrever(r: Resultado) -> None:
    if r.acao == "atacar":
        critico = " [bold magenta]GOLPE CRÍTICO![/]" if r.critico else ""
        console.print(f"🗡  {r.ator} ataca {r.alvo} e causa [bold]{r.valor}[/] de dano.{critico}")
    elif r.acao == "defender":
        console.print(f"🛡  {r.ator} ergue o escudo e se prepara.")
    elif r.acao == "pocao":
        console.print(f"🧪 {r.ator} bebe uma poção e recupera [green]{r.valor}[/] de vida.")
    elif r.acao == "sem_pocao":
        console.print(f"[yellow]{r.ator} procura uma poção, mas a bolsa está vazia! O turno foi perdido.[/]")


def vitoria_batalha(inimigo: Inimigo) -> None:
    console.print(f"[bold green]✔ {inimigo.nome} foi derrotado![/]\n")


def fim_de_jogo(venceu: bool, heroi: Heroi) -> None:
    if venceu:
        texto, cor = f"🏆 {heroi.nome} limpou a masmorra! Vitória!", "green"
    else:
        texto, cor = f"💀 {heroi.nome} caiu em combate... Fim de jogo.", "red"
    console.print(Panel.fit(f"[bold]{texto}[/]", border_style=cor))
