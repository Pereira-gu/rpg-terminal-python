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


@dataclass
class Heroi(Personagem):
    """O personagem do jogador. Herda tudo de Personagem e ganha poções."""

    pocoes: int = 3


@dataclass
class Inimigo(Personagem):
    """Um monstro. O XP será usado na etapa 2 (subir de nível)."""

    xp: int = 10


# Os monstros ficam descritos como dados, não como código.
# Para criar um monstro novo, basta acrescentar uma linha aqui.
MODELOS_INIMIGOS = {
    "rato": dict(nome="Rato Gigante", vida_max=18, ataque=5, defesa=1, xp=5),
    "goblin": dict(nome="Goblin", vida_max=28, ataque=7, defesa=2, xp=10),
    "orc": dict(nome="Orc Brutamontes", vida_max=40, ataque=9, defesa=3, xp=20),
}


def criar_heroi(nome: str) -> Heroi:
    return Heroi(nome=nome, vida_max=50, ataque=10, defesa=3)


def criar_inimigo(tipo: str) -> Inimigo:
    # ** "desempacota" o dicionário em argumentos: nome=..., vida_max=..., etc.
    return Inimigo(**MODELOS_INIMIGOS[tipo])
