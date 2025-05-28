import random

BOARD_SIZE = 6
# Navios: 3 submarinos (1 casa), 2 torpedeiros (2 casas), 1 porta-aviões (3 casas)
SHIPS = [1, 1, 1, 2, 2, 3]

def criar_tabuleiro():
    return [['~'] * BOARD_SIZE for _ in range(BOARD_SIZE)]

def mostrar_tabuleiro(tabuleiro, revelar=False):
    print("  " + " ".join([chr(c) for c in range(ord('A'), ord('A') + BOARD_SIZE)]))
    for i, linha in enumerate(tabuleiro):
        row = []
        for cel in linha:
            if cel == 'S' and not revelar:
                row.append('~')
            else:
                row.append(cel)
        print(f"{i} {' '.join(row)}")

def posicao_valida(tabuleiro, x, y, tamanho, direcao):
    dx, dy = (1, 0) if direcao == 'H' else (0, 1)
    for i in range(tamanho):
        nx, ny = x + i * dx, y + i * dy
        if not (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE):
            return False
        if tabuleiro[ny][nx] == 'S':
            return False
    return True

def posicionar_navios(tabuleiro):
    for tamanho in SHIPS:
        while True:
            x = random.randint(0, BOARD_SIZE - 1)
            y = random.randint(0, BOARD_SIZE - 1)
            if tamanho == 1:
                direcao = 'H'  # para submarinos só uma casa, direção não importa
            else:
                direcao = random.choice(['H', 'V'])
            if posicao_valida(tabuleiro, x, y, tamanho, direcao):
                dx, dy = (1, 0) if direcao == 'H' else (0, 1)
                for i in range(tamanho):
                    tabuleiro[y + i * dy][x + i * dx] = 'S'
                break

def processar_tiro(tabuleiro, x, y):
    if tabuleiro[y][x] == 'S':
        tabuleiro[y][x] = 'X'
        return "Acertou!"
    elif tabuleiro[y][x] == '~':
        tabuleiro[y][x] = 'O'
        return "Água."
    else:
        return "Já atirou aí."

def tudo_afundado(tabuleiro):
    for linha in tabuleiro:
        if 'S' in linha:
            return False
    return True

