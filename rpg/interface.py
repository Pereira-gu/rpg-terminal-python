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
from rpg.itens import LIMITE_POCOES, Item
from rpg.mundo import ResultadoSala, Sala
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


def anunciar_inimigo(inimigo: Inimigo, local: str) -> None:
    console.clear()
    console.print(
        Panel.fit(
            f"[bold red]{inimigo.nome}[/] bloqueia o caminho!\n"
            f"[dim]Vida {inimigo.vida_max} · Ataque {inimigo.ataque} · Defesa {inimigo.defesa}[/]",
            title=local,
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


def tela_turno(heroi: Heroi, inimigo: Inimigo, local: str, turno: int, log: list[str]) -> None:
    console.clear()
    console.rule(f"[bold]{local} · Turno {turno}[/]")

    status = Table(show_header=False, box=None, padding=(0, 2))
    status.add_row(
        f"[bold cyan]{heroi.nome}[/] [dim]Nv {heroi.nivel}[/]",
        barra_vida(heroi),
        f"🧪 {heroi.pocoes}",
        f"⭐ {heroi.xp}/{heroi.xp_para_proximo} XP",
    )
    status.add_row(
        "", f"[dim]⚔ Ataque {heroi.ataque_total} · 🛡 Defesa {heroi.defesa_total}[/]", f"💰 {heroi.ouro}", ""
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
    console.print(
        f"\n[bold green]✔ {inimigo.nome} foi derrotado![/]  "
        f"[yellow]+{inimigo.xp} XP[/]  [yellow]+{inimigo.ouro} de ouro 💰[/]"
    )
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


def resumo_heroi(heroi: Heroi) -> str:
    """Uma linha com o essencial do herói, usada fora do combate."""
    return (
        f"[bold cyan]{heroi.nome}[/] Nv {heroi.nivel}  {barra_vida(heroi, 15)}  "
        f"🧪 {heroi.pocoes}  💰 {heroi.ouro}  ⭐ {heroi.xp}/{heroi.xp_para_proximo}"
    )


def escolher_porta(heroi: Heroi, andar: int, total: int, portas: tuple[Sala, Sala]) -> Sala:
    console.clear()
    console.rule(f"[bold]Andar {andar}/{total}[/]")
    console.print(resumo_heroi(heroi), "\n")
    console.print(
        Panel(
            f"[bold][1] Porta da esquerda[/]  [italic]{portas[0].pista}[/]\n"
            f"[bold][2] Porta da direita[/]   [italic]{portas[1].pista}[/]",
            title="Duas portas à sua frente",
            title_align="left",
            border_style="magenta",
        )
    )
    console.print("[dim]Dica: uma das portas sempre leva a um monstro (XP e ouro garantidos).[/]")
    escolha = Prompt.ask("Qual porta", choices=["1", "2"], show_choices=False)
    return portas[int(escolha) - 1]


def mostrar_evento(r: ResultadoSala, heroi: Heroi) -> None:
    console.clear()
    if r.tipo == "tesouro":
        texto_evento, cor = f"💰 Um baú esquecido! Você encontra [bold]{r.valor}[/] de ouro.", "yellow"
    elif r.tipo == "fonte":
        texto_evento, cor = f"💧 Uma fonte de águas claras. Você recupera [green]{r.valor}[/] de vida.", "cyan"
    elif r.esquivou:
        texto_evento, cor = "⚠  O chão cede, mas você pula para trás a tempo! Era uma armadilha.", "yellow"
    else:
        texto_evento, cor = f"🪤 Era uma armadilha! Lanças saem da parede: [red]{r.valor}[/] de dano.", "red"
    console.print(Panel.fit(texto_evento, border_style=cor))
    console.print(resumo_heroi(heroi))
    pausar()


def chegada_ao_chefe() -> None:
    console.clear()
    console.print(
        Panel.fit(
            "Depois do último andar, um acampamento abandonado e uma escada que desce.\n"
            "Um mercador cansado oferece seus produtos antes da batalha final...",
            title="🔥 Acampamento",
            border_style="yellow",
        )
    )
    pausar()


def _situacao(item: Item, heroi: Heroi) -> str:
    """Etiqueta ao lado do item na loja."""
    if item.tipo != "pocao" and getattr(heroi, item.tipo) == item:
        return "[green]equipado[/]"
    if heroi.ouro < item.preco:
        return "[red]ouro insuficiente[/]"
    return ""


def tela_loja(heroi: Heroi, catalogo: list[Item], mensagem: str) -> Item | None:
    """Mostra a loja e devolve o item escolhido, ou None se o jogador sair."""
    console.clear()
    tabela = Table(box=None, padding=(0, 2))
    for coluna in ("#", "Item", "Efeito", "Preço", ""):
        tabela.add_column(coluna, style="bold" if coluna == "#" else None)
    for numero, item in enumerate(catalogo, start=1):
        tabela.add_row(str(numero), item.nome, item.descricao, f"{item.preco} 💰", _situacao(item, heroi))
    console.print(Panel(tabela, title="🏪 Loja do Ferreiro", subtitle=f"Você tem 💰 {heroi.ouro}", border_style="yellow"))

    arma = heroi.arma.nome if heroi.arma else "nenhuma"
    armadura = heroi.armadura.nome if heroi.armadura else "nenhuma"
    console.print(
        f"[dim]Equipado: ⚔ {arma} (ataque {heroi.ataque_total}) · "
        f"🛡 {armadura} (defesa {heroi.defesa_total}) · 🧪 {heroi.pocoes}/{LIMITE_POCOES} poções[/]"
    )
    if mensagem:
        console.print(mensagem)

    opcoes = ["0"] + [str(n) for n in range(1, len(catalogo) + 1)]
    escolha = Prompt.ask("\nNúmero do item para comprar, ou [bold]0[/] para seguir viagem", choices=opcoes, show_choices=False)
    return None if escolha == "0" else catalogo[int(escolha) - 1]


def texto_compra(codigo: str, item: Item) -> str:
    return {
        "ok": f"[green]✔ Você comprou {item.nome}![/]",
        "sem_ouro": f"[red]✖ Ouro insuficiente para {item.nome}.[/]",
        "bolsa_cheia": f"[yellow]✖ Sua bolsa já tem {LIMITE_POCOES} poções.[/]",
        "nao_melhora": f"[yellow]✖ {item.nome} não é melhor do que o que você já usa.[/]",
    }[codigo]


def fim_de_jogo(venceu: bool, heroi: Heroi) -> None:
    if venceu:
        texto_final, cor = f"🏆 {heroi.nome} limpou a masmorra no nível {heroi.nivel}! Vitória!", "green"
    else:
        texto_final, cor = f"💀 {heroi.nome} caiu em combate no nível {heroi.nivel}... Fim de jogo.", "red"
    console.print()
    console.print(Panel.fit(f"[bold]{texto_final}[/]", border_style=cor))
