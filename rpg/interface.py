"""Tudo que aparece na tela fica aqui, usando a biblioteca rich.

Se um dia quisermos trocar o visual (outra biblioteca ou uma versão web),
só este arquivo muda: as regras do jogo continuam iguais.

Organização da tela a cada turno (a tela é limpa antes):
    1. cabeçalho com batalha e turno
    2. painel de status (vida, poções, aviso de golpe pesado)
    3. painel "Último turno" com o que aconteceu
    4. menu de ações com a explicação de cada uma
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from rpg.combate import CURA_POCAO, Resultado
from rpg.personagem import BONUS_POR_NIVEL, Heroi, Inimigo, Personagem, SubidaDeNivel

console = Console()

# O jogador digita um número; o jogo trabalha com o nome da ação.
ACOES = {"1": "atacar", "2": "defender", "3": "pocao"}


def pausar() -> None:
    console.input("\n[dim]Pressione Enter para continuar...[/]")


def barra_vida(p: Personagem, largura: int = 20) -> str:
    """Desenha algo como ████████░░░░ 30/50, com cor conforme a vida restante."""
    proporcao = p.vida / p.vida_max
    cheios = round(proporcao * largura)
    cor = "green" if proporcao > 0.5 else "yellow" if proporcao > 0.25 else "red"
    return f"[{cor}]{'█' * cheios}[/][dim]{'░' * (largura - cheios)}[/] {p.vida}/{p.vida_max}"


def titulo() -> None:
    console.clear()
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
    console.clear()
    console.print(
        Panel.fit(
            f"[bold red]{inimigo.nome}[/] bloqueia o caminho!\n"
            f"[dim]Vida {inimigo.vida_max} · Ataque {inimigo.ataque} · Defesa {inimigo.defesa}[/]",
            title=f"Batalha {numero}/{total}",
            border_style="red",
        )
    )
    pausar()


def texto(r: Resultado) -> str:
    """Transforma o resultado de uma ação em uma frase para o painel do turno."""
    critico = " [bold magenta]CRÍTICO![/]" if r.critico else ""
    if r.acao == "atacar":
        return f"🗡  {r.ator} ataca {r.alvo}: [bold]{r.valor}[/] de dano.{critico}"
    if r.acao == "defender":
        return f"🛡  {r.ator} ergue o escudo."
    if r.acao == "pocao":
        return f"🧪 {r.ator} bebe uma poção: [green]+{r.valor}[/] de vida."
    if r.acao == "sem_pocao":
        return f"[yellow]🧪 {r.ator} procura uma poção, mas a bolsa está vazia! Turno perdido.[/]"
    if r.acao == "preparar":
        return f"[bold yellow]⚠  {r.ator} se prepara para um golpe pesado![/]"
    if r.acao == "golpe_pesado":
        return f"💥 {r.ator} solta o GOLPE PESADO em {r.alvo}: [bold red]{r.valor}[/] de dano.{critico}"
    return ""


def tela_turno(heroi: Heroi, inimigo: Inimigo, batalha: int, total: int, turno: int, log: list[str]) -> None:
    console.clear()
    console.rule(f"[bold]Batalha {batalha}/{total} · Turno {turno}[/]")

    status = Table(show_header=False, box=None, padding=(0, 2))
    status.add_row(
        f"[bold cyan]{heroi.nome}[/] [dim]Nv {heroi.nivel}[/]",
        barra_vida(heroi),
        f"🧪 {heroi.pocoes}",
        f"⭐ {heroi.xp}/{heroi.xp_para_proximo} XP",
    )
    status.add_row(f"[bold red]{inimigo.nome}[/]", barra_vida(inimigo), "", "")
    if inimigo.preparando and inimigo.vivo:
        status.add_row("", "[bold yellow]⚠ Golpe pesado no próximo turno![/]", "", "")
    console.print(Panel(status, border_style="blue"))

    if log:
        console.print(Panel("\n".join(log), title="Último turno", title_align="left", border_style="dim"))


def escolher_acao(heroi: Heroi) -> str:
    console.print(
        "[bold][1] Atacar[/]    causa dano no inimigo\n"
        "[bold][2] Defender[/]  bloqueia 75% do próximo golpe (ótimo contra golpe pesado)\n"
        f"[bold][3] Poção[/]     cura até {CURA_POCAO} de vida (restam {heroi.pocoes})"
    )
    numero = Prompt.ask("Sua ação", choices=list(ACOES), show_choices=False)
    return ACOES[numero]


def vitoria_batalha(inimigo: Inimigo, heroi: Heroi, subidas: list[SubidaDeNivel]) -> None:
    console.print(f"\n[bold green]✔ {inimigo.nome} foi derrotado![/]  [yellow]+{inimigo.xp} XP[/]")
    b = BONUS_POR_NIVEL
    for s in subidas:
        console.print(
            Panel.fit(
                f"[bold yellow]⬆  {heroi.nome} subiu para o nível {s.nivel}![/]\n"
                f"Vida máx +{b['vida_max']} · Ataque +{b['ataque']} · Defesa +{b['defesa']}\n"
                f"[green]Recuperou {s.curado} de vida[/]",
                border_style="yellow",
            )
        )
    if subidas:  # mostra os atributos finais uma vez só
        console.print(
            f"[dim]Agora: Vida {heroi.vida}/{heroi.vida_max} · "
            f"Ataque {heroi.ataque} · Defesa {heroi.defesa}[/]"
        )
    pausar()


def fim_de_jogo(venceu: bool, heroi: Heroi) -> None:
    if venceu:
        texto_final, cor = f"🏆 {heroi.nome} limpou a masmorra no nível {heroi.nivel}! Vitória!", "green"
    else:
        texto_final, cor = f"💀 {heroi.nome} caiu em combate no nível {heroi.nivel}... Fim de jogo.", "red"
    console.print()
    console.print(Panel.fit(f"[bold]{texto_final}[/]", border_style=cor))
