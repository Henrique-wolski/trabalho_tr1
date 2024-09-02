import socket
import threading
import pickle
import struct
import random
import queue
import time

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
    if dados_recebidos:
        break

# Desserializar os dados
informacoes = pickle.loads(dados_recebidos)

erro = dados_recebidos[0] / 100

modulacao_desejada = dados_recebidos[1]

# Configurar a conexão com o receptor

time.sleep(1)   # Tempo para permitir que o receptor espere por conexões

IP_receptor = socket.gethostbyname(socket.gethostname())  # IP da máquina receptora
PORT_receptor = 8002 # Port genérica (deve ser a mesma definida no receptor)
ADDR = (IP_receptor, PORT_receptor)

# Criação do tranmissor como socket, fazendo uso de IPV4 e TCP
canal_transmitir = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conexão do socket criado com aquele do canal, para que possa enviar o sinal
canal_transmitir.connect(ADDR)

# Lógica do recebimento da amostra, inserção de erro e envio para o receptor

def espera_ack(socket_transmissor, socket_receptor, erro):
    global contador, contador2
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
            while True:
                sinal = socket_transmissor.recv(1)  # Recebimento de parte da confirmação do ack do transmissor

                # Inserir erro na confirmação do ack
                if random.random() < erro:
                    if sinal == b'0':
                        sinal = b'1'

                    else:
                        sinal = b'0'
        
                socket_receptor.send(sinal)  # Envio de parte do ack ao transmissor
                contador2 += 1

                if contador2 == 8:
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

    socket.send(amostra[0].encode("utf-8"))

# Inicia uma thread para verificar o recebimento do acknowledgement
while True:
    contador = 0
    contador2 = 0
    thread1 = threading.Thread(target = espera_ack, args = (conn1, canal_transmitir, erro))
    thread1.start()

    while True:
        amostra = conn1.recv(1).decode("utf-8") # Recebe a amostra, que pode ser "low", "high" ou '0'

        if amostra:
            if amostra == 'l':
                amostra = "low"
            elif amostra == 'h':
                amostra = "high"

            thread2 = threading.Thread(target = introduzir_erro, args = (canal_transmitir, modulacao_desejada, amostra))
            thread2.start()

        if contador >= 8:
            break