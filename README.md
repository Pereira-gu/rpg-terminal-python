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

- [x] **Etapa 1: Combate.** Herói contra 3 monstros, com as ações atacar, defender e usar poção.
- [ ] **Etapa 2: Evolução.** XP, subir de nível e atributos que crescem.
- [ ] **Etapa 3: Itens.** Inventário, armas e armaduras, ouro e loja.
- [ ] **Etapa 4: Exploração.** Salas da masmorra, escolha de caminho e eventos.
- [ ] **Etapa 5: Chefe final.** Um dragão com um ataque especial, e as telas de vitória e derrota.
- [ ] **Etapa 6: Portfólio.** README com prints, revisão de código e publicação no GitHub.

## Estrutura

```
main.py            ponto de entrada: monta o jogo e roda o loop
rpg/personagem.py  classes Personagem, Heroi, Inimigo e os modelos de monstros
rpg/combate.py     regras do combate (lógica pura, sem print/input)
rpg/interface.py   tudo que aparece na tela (rich)
tests/             testes automáticos com pytest
```
