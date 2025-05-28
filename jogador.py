import socket
import json
import time
import os

BOARD_SIZE = 6  # atualizado para 6x6

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def animar_caminho(col, row, board_size=6):
    col_letras = [chr(ord('A') + i) for i in range(board_size)]
    grid = [['.' for _ in range(board_size)] for _ in range(board_size)]
    
    # Desce a coluna até a linha
    for r in range(row + 1):
        limpar_tela()
        print("  " + " ".join(col_letras))
        for i in range(board_size):
            linha = []
            for j in range(board_size):
                if j == col and i <= r:
                    linha.append('|')
                else:
                    linha.append(grid[i][j])
            print(f"{i} {' '.join(linha)}")
        time.sleep(0.4)  # Mais devagar

    # Vai na linha até a coluna (horizontal no "L")
    for c in range(col + 1):
        limpar_tela()
        print("  " + " ".join(col_letras))
        for i in range(board_size):
            linha = []
            for j in range(board_size):
                if j == col and i <= row:
                    linha.append('|')
                elif i == row and j <= c:
                    linha.append('-')
                else:
                    linha.append(grid[i][j])
            print(f"{i} {' '.join(linha)}")
        time.sleep(0.4)  # Mais devagar

    # Marca o alvo final com X
    limpar_tela()
    print("  " + " ".join(col_letras))
    for i in range(board_size):
        linha = []
        for j in range(board_size):
            if i == row and j == col:
                linha.append('X')
            elif j == col and i <= row:
                linha.append('|')
            elif i == row and j <= col:
                linha.append('-')
            else:
                linha.append(grid[i][j])
        print(f"{i} {' '.join(linha)}")
    print("\nAlvo atingido!\n")
    time.sleep(0.8)

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

def parse_tiro(input_str):
    try:
        col = ord(input_str[0].upper()) - ord('A')
        row = int(input_str[1:])
        if 0 <= col < BOARD_SIZE and 0 <= row < BOARD_SIZE:
            return col, row
    except:
        pass
    return None

HOST = input("Digite o IP do servidor: ")
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

print(client.recv(1024).decode())  # Mensagem do servidor

input("Pressione ENTER quando estiver pronto...")

client.send(b"PRONTO")

# Receber quem começa
turno = client.recv(1024).decode()
print("[SERVIDOR]:", turno)

# Receber tabuleiro inicial
tabuleiro = None
tabuleiro_inimigo = None

def receber_mensagem():
    data = client.recv(4096).decode()
    return data

# Recebe o tabuleiro próprio inicial
while True:
    msg = receber_mensagem()
    if msg.startswith("TABULEIRO:"):
        tabuleiro = json.loads(msg[len("TABULEIRO:"):])
        break
    else:
        print(msg)

print("\n=== Seu tabuleiro com embarcações ===")
mostrar_tabuleiro(tabuleiro, revelar=True)

if turno == "PRIMEIRO":
    sua_vez = True
else:
    sua_vez = False

while True:
    if sua_vez:
        if tabuleiro_inimigo:
            print("\n=== Tabuleiro inimigo ===")
            mostrar_tabuleiro(tabuleiro_inimigo)
        else:
            print("\nTabuleiro inimigo ainda não recebido.")

        tiro = input("Digite sua jogada (ex: A5): ")
        pos = parse_tiro(tiro)
        if pos is None:
            print("Jogada inválida, tente novamente.")
            continue
        
        col, row = pos
        animar_caminho(col, row, BOARD_SIZE)  # animação antes de enviar

        client.send(f"TIRO:{tiro}".encode())

        resposta = client.recv(1024).decode()
        print("[RESPOSTA DO SERVIDOR]:", resposta)

        if "Fim de jogo" in resposta:
            break

        atualizacao = client.recv(4096).decode()
        if atualizacao.startswith("ATUALIZACAO:"):
            proprio_str, inimigo_str = atualizacao[len("ATUALIZACAO:"):].split("|")
            tabuleiro = json.loads(proprio_str)
            tabuleiro_inimigo = json.loads(inimigo_str)

            print("\n=== Seu tabuleiro atualizado ===")
            mostrar_tabuleiro(tabuleiro, revelar=True)
            print("\n=== Tabuleiro inimigo atualizado ===")
            mostrar_tabuleiro(tabuleiro_inimigo)

        sua_vez = False
    else:
        print("[AGUARDANDO JOGADA DO OPONENTE...]")
        data = client.recv(4096).decode()
        if data.startswith("ATUALIZACAO:"):
            proprio_str, inimigo_str = data[len("ATUALIZACAO:"):].split("|")
            tabuleiro = json.loads(proprio_str)
            tabuleiro_inimigo = json.loads(inimigo_str)

            print("\n=== Seu tabuleiro atualizado ===")
            mostrar_tabuleiro(tabuleiro, revelar=True)
            print("\n=== Tabuleiro inimigo atualizado ===")
            mostrar_tabuleiro(tabuleiro_inimigo)
        else:
            print("[MENSAGEM DO SERVIDOR]:", data)

        sua_vez = True

