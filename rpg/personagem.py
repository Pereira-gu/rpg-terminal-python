"""Personagens do jogo: o herói e os inimigos.

Usamos @dataclass porque ela gera o __init__ automaticamente a partir dos
campos. Isso deixa as classes curtas e fáceis de ler.
"""

from dataclasses import dataclass, field

from rpg.itens import Item


@dataclass
class Personagem:
    """Tudo que herói e inimigos têm em comum."""

    nome: str
    vida_max: int
    ataque: int
    defesa: int
    # init=False: esses campos não são passados na criação, têm valor inicial próprio.
    vida: int = field(init=False)
    defendendo: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        # Roda logo depois do __init__: todo personagem começa com a vida cheia.
        self.vida = self.vida_max

    @property
    def vivo(self) -> bool:
        return self.vida > 0

    # "ataque" e "defesa" são os valores BASE. O combate usa os valores TOTAIS,
    # que no herói somam o equipamento. Inimigos não têm equipamento: total = base.
    @property
    def ataque_total(self) -> int:
        return self.ataque

    @property
    def defesa_total(self) -> int:
        return self.defesa

    def receber_dano(self, dano: int) -> int:
        """Tira vida sem deixar ficar negativa. Retorna o dano aplicado."""
        dano = max(0, dano)
        self.vida = max(0, self.vida - dano)
        return dano

    def curar(self, quantidade: int) -> int:
        """Recupera vida sem passar do máximo. Retorna quanto curou de fato."""
        antes = self.vida
        self.vida = min(self.vida_max, self.vida + quantidade)
        return self.vida - antes


XP_POR_NIVEL = 10  # nível 1→2 pede 10 XP, 2→3 pede 20, 3→4 pede 30...
BONUS_POR_NIVEL = {"vida_max": 8, "ataque": 2, "defesa": 1}


@dataclass
class SubidaDeNivel:
    """Registro de uma subida de nível, para a interface mostrar."""

    nivel: int
    curado: int


@dataclass
class Heroi(Personagem):
    """O personagem do jogador. Herda tudo de Personagem e ganha poções, nível e XP."""

    pocoes: int = 3
    nivel: int = 1
    xp: int = 0  # XP acumulado no nível atual
    ouro: int = 10
    arma: Item | None = None  # None = lutando com as mãos/arma básica
    armadura: Item | None = None

    # Sobrescreve (override) as versões de Personagem para somar o equipamento.
    @property
    def ataque_total(self) -> int:
        return self.ataque + (self.arma.bonus if self.arma else 0)

    @property
    def defesa_total(self) -> int:
        return self.defesa + (self.armadura.bonus if self.armadura else 0)

    @property
    def xp_para_proximo(self) -> int:
        return XP_POR_NIVEL * self.nivel

    def ganhar_xp(self, quantidade: int) -> list[SubidaDeNivel]:
        """Soma XP e sobe quantos níveis forem possíveis.

        Usamos while (e não if) porque muito XP de uma vez pode render
        mais de um nível. O XP que sobra passa para o nível seguinte.
        """
        self.xp += quantidade
        subidas = []
        while self.xp >= self.xp_para_proximo:
            self.xp -= self.xp_para_proximo  # subtrai ANTES de subir: o custo é o do nível atual
            subidas.append(self._subir_nivel())
        return subidas

    def _subir_nivel(self) -> SubidaDeNivel:
        # O _ no início indica "uso interno": quem usa a classe chama ganhar_xp.
        self.nivel += 1
        self.vida_max += BONUS_POR_NIVEL["vida_max"]
        self.ataque += BONUS_POR_NIVEL["ataque"]
        self.defesa += BONUS_POR_NIVEL["defesa"]
        # Cura só os pontos de vida novos: o dano das batalhas anteriores continua,
        # e é isso que dá valor às poções e à defesa.
        curado = self.curar(BONUS_POR_NIVEL["vida_max"])
        return SubidaDeNivel(self.nivel, curado)


@dataclass
class Inimigo(Personagem):
    """Um monstro. XP e ouro são o que o herói ganha ao derrotá-lo."""

    xp: int = 10
    ouro: int = 0
    # True quando o monstro está carregando um golpe pesado para o próximo turno.
    preparando: bool = False
    # O golpe pesado é descrito por dados: cada monstro pode ter o seu.
    chance_preparar: float = 0.30
    multiplicador_pesado: int = 2
    nome_golpe: str = "golpe pesado"
    # Fúria: ao cair para metade da vida, o monstro fica mais forte (uma vez só).
    furia: bool = False
    enfurecido: bool = False


# Os monstros ficam descritos como dados, não como código.
# Para criar um monstro novo, basta acrescentar uma linha aqui.
MODELOS_INIMIGOS = {
    # Valores calibrados com 5.000 partidas simuladas: quem só ataca vence ~45%,
    # quem defende do golpe pesado e usa poções na hora certa vence ~99%.
    "rato": dict(nome="Rato Gigante", vida_max=22, ataque=7, defesa=1, xp=12, ouro=15),
    "goblin": dict(nome="Goblin", vida_max=34, ataque=10, defesa=2, xp=18, ouro=25),
    "orc": dict(nome="Orc Brutamontes", vida_max=55, ataque=13, defesa=4, xp=30, ouro=40),
    # O chefe final: sopro de fogo triplo e fúria na metade da vida.
    # Calibrado com simulação (python -m ferramentas.simular):
    # com estratégia vence ~82%; só atacando ~2%; fugindo das lutas ~0,5%.
    "dragao": dict(
        nome="Dragão Ancestral", vida_max=110, ataque=16, defesa=5, xp=100, ouro=0,
        chance_preparar=0.35, multiplicador_pesado=3, nome_golpe="sopro de fogo", furia=True,
    ),
}


def criar_heroi(nome: str) -> Heroi:
    return Heroi(nome=nome, vida_max=50, ataque=10, defesa=3)


def criar_inimigo(tipo: str) -> Inimigo:
    # ** "desempacota" o dicionário em argumentos: nome=..., vida_max=..., etc.
    return Inimigo(**MODELOS_INIMIGOS[tipo])
