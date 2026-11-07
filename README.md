# Masmorra de Pedra (RPG de terminal)

Mini RPG de fantasia medieval jogado no terminal, feito em Python 3.13 com a biblioteca [rich](https://github.com/Textualize/rich).

## Como jogar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Como rodar os testes

```bash
python -m pytest
```

## Roteiro

- [x] **Etapa 1: Combate.** Herói contra 3 monstros, com as ações atacar, defender e usar poção. O inimigo anuncia golpes pesados, que podem ser bloqueados com a defesa.
- [x] **Etapa 2: Evolução.** XP, subir de nível e atributos que crescem.
- [x] **Etapa 3: Itens.** Armas e armaduras, ouro e uma loja entre as batalhas.
- [x] **Etapa 4: Exploração.** 5 andares com duas portas cada: um combate ou uma surpresa (tesouro, fonte, loja ou armadilha). No fim, um acampamento e o chefe.
- [x] **Etapa 5: Chefe final.** O Dragão Ancestral, com sopro de fogo e fúria, as telas de vitória e derrota com estatísticas, e a opção de jogar de novo.
- [ ] **Etapa 6: Portfólio.** README com prints, revisão de código e publicação no GitHub.

## Estrutura

```
main.py            ponto de entrada: monta o jogo e roda o loop
rpg/personagem.py  classes Personagem, Heroi, Inimigo e os modelos de monstros
rpg/combate.py     regras do combate (lógica pura, sem print/input)
rpg/itens.py       catálogo da loja e regra de compra
rpg/mundo.py       geração dos andares e efeitos das salas
rpg/interface.py   tudo que aparece na tela (rich)
tests/             testes automáticos com pytest
```
