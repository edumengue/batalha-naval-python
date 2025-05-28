import socket
import threading
import random
import json

from game import criar_tabuleiro, posicionar_navios, processar_tiro, tudo_afundado, BOARD_SIZE

HOST = '0.0.0.0'
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)
print("[SERVIDOR] Aguardando dois jogadores...")

jogadores = []
enderecos = []

for i in range(2):
    conn, addr = server.accept()
    jogadores.append(conn)
    enderecos.append(addr)
    conn.send(f"[SERVIDOR] Você é o Jogador {i+1}. Aguarde no lobby...\nPressione ENTER quando estiver pronto.".encode())
    print(f"[SERVIDOR] Jogador {i+1} conectado de {addr}")

# Criar tabuleiros para os dois jogadores
tabuleiros = [criar_tabuleiro(), criar_tabuleiro()]
for i in range(2):
    posicionar_navios(tabuleiros[i])

# Espera confirmação de prontos (lobby)
for i, conn in enumerate(jogadores):
    _ = conn.recv(1024)  # Espera ENTER / PRONTO do cliente

print("[SERVIDOR] Ambos os jogadores estão prontos! Sorteando quem começa...")

# Sorteio de quem começa
primeiro = random.choice([0, 1])
segundo = 1 - primeiro
jogadores[primeiro].send("PRIMEIRO".encode())
jogadores[segundo].send("SEGUNDO".encode())

def enviar_tabuleiro(conn, tabuleiro):
    conn.send(f"TABULEIRO:{json.dumps(tabuleiro)}".encode())

enviar_tabuleiro(jogadores[0], tabuleiros[0])
enviar_tabuleiro(jogadores[1], tabuleiros[1])

turno_atual = primeiro
lock = threading.Lock()

def enviar_atualizacoes():
    with lock:
        for i in [0, 1]:
            proprio = tabuleiros[i]
            inimigo = tabuleiros[1 - i]
            msg = f"ATUALIZACAO:{json.dumps(proprio)}|{json.dumps(inimigo)}"
            try:
                jogadores[i].send(msg.encode())
            except:
                pass

def handle_jogador(indice):
    global turno_atual
    conn = jogadores[indice]
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                print(f"[SERVIDOR] Jogador {indice+1} desconectou.")
                break

            texto = data.decode()
            if not texto.startswith("TIRO:"):
                continue

            with lock:
                if turno_atual != indice:
                    conn.send("Não é sua vez.".encode())
                    continue

            tiro = texto[5:]
            if len(tiro) < 2:
                conn.send("Tiro inválido.".encode())
                continue

            x = ord(tiro[0].upper()) - ord('A')
            try:
                y = int(tiro[1:])
            except:
                conn.send("Tiro inválido.".encode())
                continue

            if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                conn.send("Tiro fora do tabuleiro.".encode())
                continue

            adversario = 1 - indice
            resultado = processar_tiro(tabuleiros[adversario], x, y)

            if tudo_afundado(tabuleiros[adversario]):
                msg_fim = "Fim de jogo: você venceu!"
                jogadores[indice].send(msg_fim.encode())
                jogadores[adversario].send("Fim de jogo: você perdeu!".encode())
                print("[SERVIDOR] Jogo encerrado.")
                break

            jogadores[indice].send(resultado.encode())
            enviar_atualizacoes()

            with lock:
                turno_atual = adversario

        except Exception as e:
            print(f"[ERRO SERVIDOR] {e}")
            break

    conn.close()

threading.Thread(target=handle_jogador, args=(0,), daemon=True).start()
threading.Thread(target=handle_jogador, args=(1,), daemon=True).start()

while True:
    pass

