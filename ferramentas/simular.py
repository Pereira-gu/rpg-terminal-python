"""Simulador de balanceamento: joga milhares de partidas sozinho, sem tela.

Usa as MESMAS regras do jogo (rpg/), só troca o jogador humano por "estilos"
automáticos. Gera uma tabela no terminal e dois gráficos em docs/.

Como rodar (na pasta do projeto):
    python -m ferramentas.simular
"""

import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # gera arquivos de imagem sem abrir janela
import matplotlib.pyplot as plt  # noqa: E402

from rpg import combate, itens, mundo  # noqa: E402
from rpg.personagem import MODELOS_INIMIGOS, Heroi, Inimigo, criar_heroi, criar_inimigo  # noqa: E402

PASTA_DOCS = Path(__file__).resolve().parent.parent / "docs"
CHEFE = "dragao"
PARTIDAS = 3000

# Cores validadas para daltonismo (paleta categórica, ordem fixa).
AZUL, LARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"
TEXTO, TEXTO_2, GRADE = "#0b0b0b", "#52514e", "#e4e3df"


# ---------- Como cada estilo decide ----------

def acao_estrategica(heroi: Heroi, inimigo: Inimigo, rng: random.Random) -> str:
    if inimigo.preparando:
        return "defender"
    if heroi.vida < heroi.vida_max * 0.4 and heroi.pocoes > 0:
        return "pocao"
    return "atacar"


def acao_so_ataca(heroi: Heroi, inimigo: Inimigo, rng: random.Random) -> str:
    return "atacar"


def acao_aleatoria(heroi: Heroi, inimigo: Inimigo, rng: random.Random) -> str:
    return rng.choice(["atacar", "defender", "pocao"])


def porta_estrategica(heroi, portas, rng):
    """Luta se a vida está acima da metade; senão, arrisca a surpresa."""
    luta, surpresa = sorted(portas, key=lambda s: s.tipo != "combate")
    return luta if heroi.vida >= heroi.vida_max * 0.5 else surpresa


def porta_sempre_luta(heroi, portas, rng):
    return next(s for s in portas if s.tipo == "combate")


def porta_foge(heroi, portas, rng):
    return next(s for s in portas if s.tipo != "combate")


def porta_aleatoria(heroi, portas, rng):
    return rng.choice(portas)


# Cada estilo = (como escolhe a porta, como luta, se faz compras)
ESTILOS = {
    "Estratégico": (porta_estrategica, acao_estrategica, True),
    "Só ataca": (porta_sempre_luta, acao_so_ataca, True),
    "Aleatório": (porta_aleatoria, acao_aleatoria, False),
    "Foge das lutas": (porta_foge, acao_estrategica, True),
}


# ---------- Uma partida completa ----------

def comprar_o_melhor(heroi: Heroi) -> None:
    melhores_primeiro = sorted(itens.CATALOGO[1:], key=lambda i: -i.bonus)
    for item in melhores_primeiro + [itens.POCAO] * itens.LIMITE_POCOES:
        itens.comprar(heroi, item)


def lutar(heroi: Heroi, tipo: str, decidir, rng: random.Random) -> bool:
    inimigo = criar_inimigo(tipo)
    while heroi.vivo and inimigo.vivo:
        combate.turno_heroi(heroi, inimigo, decidir(heroi, inimigo, rng), rng)
        if inimigo.vivo:
            combate.turno_inimigo(inimigo, heroi, rng)
    if heroi.vivo:
        heroi.ouro += inimigo.ouro
        heroi.ganhar_xp(inimigo.xp)
    return heroi.vivo


def partida(estilo: str, rng: random.Random) -> bool:
    """Joga uma partida inteira e retorna True se venceu o dragão."""
    escolher_porta, decidir, compra = ESTILOS[estilo]
    heroi = criar_heroi("Simulado")
    for portas in mundo.gerar_masmorra(rng):
        sala = escolher_porta(heroi, portas, rng)
        if sala.tipo == "combate":
            if not lutar(heroi, sala.inimigo, decidir, rng):
                return False
        elif sala.tipo == "loja":
            if compra:
                comprar_o_melhor(heroi)
        else:
            mundo.resolver_sala(sala, heroi, rng)
            if not heroi.vivo:
                return False
    if compra:
        comprar_o_melhor(heroi)  # acampamento
    return lutar(heroi, CHEFE, decidir, rng)


def taxa_vitoria(estilo: str, partidas: int, rng: random.Random) -> float:
    return sum(partida(estilo, rng) for _ in range(partidas)) / partidas


# ---------- Gráficos ----------

def _estilo_base(ax) -> None:
    """Eixos e grade discretos: o destaque fica nos dados."""
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(GRADE)
    ax.tick_params(colors=TEXTO_2, length=0)
    ax.grid(color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)


def grafico_estilos(taxas: dict[str, float], caminho: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.2), dpi=150)
    nomes = list(taxas)[::-1]  # o primeiro estilo fica no topo
    valores = [taxas[n] * 100 for n in nomes]
    ax.barh(nomes, valores, color=AZUL, height=0.55)
    for y, v in enumerate(valores):
        texto = f"{v:.0f}%" if v >= 10 or v == 0 else f"{v:.1f}%".replace(".", ",")
        ax.text(v + 1.5, y, texto, va="center", color=TEXTO, fontsize=10)
    _estilo_base(ax)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 108)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.tick_params(axis="y", colors=TEXTO, labelsize=10)
    ax.set_title(f"Taxa de vitória por estilo de jogo ({PARTIDAS:,} partidas cada)".replace(",", "."),
                 loc="left", color=TEXTO, fontsize=12, pad=12)
    fig.tight_layout()
    fig.savefig(caminho)
    plt.close(fig)


def grafico_vida_dragao(vidas: list[int], curvas: dict[str, list[float]], escolhida: int, caminho: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=150)
    cores = [AZUL, LARANJA, VERDE]
    finais = []  # (y final, nome) para os rótulos diretos
    for (nome, taxas), cor in zip(curvas.items(), cores):
        ys = [t * 100 for t in taxas]
        ax.plot(vidas, ys, color=cor, linewidth=2, marker="o", markersize=5, label=nome)
        finais.append((ys[-1], nome))
    # Rótulos no fim das linhas, afastados entre si para não se sobreporem.
    ultimo_y = -100.0
    for y, nome in sorted(finais):
        y = max(y, ultimo_y + 7)
        ax.text(vidas[-1] + 3, y, nome, color=TEXTO, va="center", fontsize=9)
        ultimo_y = y
    ax.axvline(escolhida, color=TEXTO_2, linewidth=1, linestyle="--")
    ax.text(escolhida + 1.5, 103, f"valor usado no jogo ({escolhida})", color=TEXTO_2, fontsize=9)
    _estilo_base(ax)
    ax.set_xlim(vidas[0] - 5, vidas[-1] + 28)
    ax.set_ylim(-3, 110)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("Vida máxima do dragão", color=TEXTO_2)
    ax.set_title("Como a vida do dragão muda a taxa de vitória", loc="left", color=TEXTO, fontsize=12, pad=12)
    ax.legend(frameon=False, loc="upper right", labelcolor=TEXTO, fontsize=9)
    fig.tight_layout()
    fig.savefig(caminho)
    plt.close(fig)


# ---------- Programa principal ----------

def main() -> None:
    PASTA_DOCS.mkdir(exist_ok=True)
    rng = random.Random(42)  # semente fixa: o resultado é reproduzível

    print(f"Simulando {PARTIDAS} partidas por estilo...")
    taxas = {estilo: taxa_vitoria(estilo, PARTIDAS, rng) for estilo in ESTILOS}
    for estilo, taxa in taxas.items():
        print(f"  {estilo:15} {taxa:6.1%}")
    grafico_estilos(taxas, PASTA_DOCS / "taxa_vitoria_estilos.png")

    print("Variando a vida do dragão...")
    vida_original = MODELOS_INIMIGOS[CHEFE]["vida_max"]
    vidas = list(range(80, 151, 10))
    curvas: dict[str, list[float]] = {e: [] for e in ("Estratégico", "Só ataca", "Foge das lutas")}
    try:
        for vida in vidas:
            MODELOS_INIMIGOS[CHEFE]["vida_max"] = vida
            for estilo in curvas:
                curvas[estilo].append(taxa_vitoria(estilo, PARTIDAS // 3, rng))
    finally:
        MODELOS_INIMIGOS[CHEFE]["vida_max"] = vida_original  # sempre devolve o valor certo
    print("  vida   " + "  ".join(f"{v:>4}" for v in vidas))
    for estilo, taxas_curva in curvas.items():
        print(f"  {estilo[:6]:6} " + "  ".join(f"{t:4.0%}" for t in taxas_curva))
    grafico_vida_dragao(vidas, curvas, vida_original, PASTA_DOCS / "vida_dragao.png")
    print(f"Gráficos salvos em {PASTA_DOCS}")


if __name__ == "__main__":
    main()
