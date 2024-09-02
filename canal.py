import socket
import threading
import pickle
import struct
import random
import queue

IP_canal = socket.gethostbyname(socket.gethostname())  # IP local
PORT_canal = 8001 # Port genérica
ADDR = (IP_canal, PORT_canal)

# Criação do canal como socket, fazendo uso de IPV4 e TCP para receber o sinal
canal_receber = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associação do socket ao IP e porta definidos, para receber o sinal
canal_receber.bind(ADDR)

canal_receber.listen()

conn1, addr1 = canal_receber.accept()

while True:
    dados_recebidos = conn1.recv(1024)
    if not dados_recebidos:
        break

# Desserializar os dados
informacoes = pickle.loads(dados_recebidos)

erro = dados_recebidos[0] / 100

modulacao_desejada = dados_recebidos[1]

# Configurar a conexão com o receptor

IP_receptor = socket.gethostbyname(socket.gethostname())  # IP da máquina receptora
PORT_receptor = 8002 # Port genérica (deve ser a mesma definida no receptor)
ADDR = (IP_receptor, PORT_receptor)

# Criação do tranmissor como socket, fazendo uso de IPV4 e TCP
canal_transmitir = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conexão do socket criado com aquele do canal, para que possa enviar o sinal
canal_transmitir.connect(ADDR)

# Lógica do recebimento da amostra, inserção de erro e envio para o receptor

def espera_ack(socket_receptor, socket_transmissor, erro):
    global contador
    while True:
        sinal = socket_receptor.recv(1)  # Recebimento de parte do ack do receptor

        # Inserir erro no ack
        if random.random() < erro:
            if sinal == b'0':
                sinal = b'1'

            else:
                sinal = b'0'
        
        socket_transmissor.send(sinal)  # Envio de parte do ack ao transmissor
        contador += 1

        if contador >= 8:
            break

def introduzir_erro(socket, modulacao, amostra):
    if modulacao == "NRZ-Polar" or modulacao == "Manchester":
        if random.random() < erro:
            if amostra == "high":
                amostra = "low"
            else:
                amostra = "high"

    else:

        if random.random() < erro:
            if amostra == "high":
                if random.randint(0, 1) == 0:
                    amostra = '0'
                else:
                    amostra = "low"
            
            elif amostra == '0':
                if random.randint(0, 1) == 0:
                    amostra = "high"
                else:
                    amostra = "low"

            else:
                if random.randint(0, 1) == 0:
                    amostra = "high"
                else:
                    amostra = '0'

    canal_transmitir.send(amostra.encode("utf-8"))

# Inicia uma thread para verificar o recebimento do acknowledgement
while True:
    contador = 0
    thread1 = threading.Thread(target = espera_ack, args = (canal_receber, canal_transmitir, erro))
    thread1.start()

    while True:
        amostra = canal_receber.recv(4).decode("utf-8") # Recebe a amostra, que pode ser "low", "high" ou '0'

        if amostra:
            thread2 = threading.Thread(target = introduzir_erro, args = (canal_transmitir, modulacao_desejada, amostra))

        if contador >= 8:
            break