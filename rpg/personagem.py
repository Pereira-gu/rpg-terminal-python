"""Personagens do jogo: o herói e os inimigos.

Usamos @dataclass porque ela gera o __init__ automaticamente a partir dos
campos. Isso deixa as classes curtas e fáceis de ler.
"""

from dataclasses import dataclass, field


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
        curado = self.curar(self.vida_max // 2)  # recupera metade da vida máxima
        return SubidaDeNivel(self.nivel, curado)


@dataclass
class Inimigo(Personagem):
    """Um monstro. O XP é o que o herói ganha ao derrotá-lo."""

    xp: int = 10
    # True quando o monstro está carregando um golpe pesado para o próximo turno.
    preparando: bool = False


# Os monstros ficam descritos como dados, não como código.
# Para criar um monstro novo, basta acrescentar uma linha aqui.
MODELOS_INIMIGOS = {
    "rato": dict(nome="Rato Gigante", vida_max=18, ataque=5, defesa=1, xp=12),
    "goblin": dict(nome="Goblin", vida_max=28, ataque=7, defesa=2, xp=18),
    "orc": dict(nome="Orc Brutamontes", vida_max=40, ataque=9, defesa=3, xp=30),
}


def criar_heroi(nome: str) -> Heroi:
    return Heroi(nome=nome, vida_max=50, ataque=10, defesa=3)


def criar_inimigo(tipo: str) -> Inimigo:
    # ** "desempacota" o dicionário em argumentos: nome=..., vida_max=..., etc.
    return Inimigo(**MODELOS_INIMIGOS[tipo])
