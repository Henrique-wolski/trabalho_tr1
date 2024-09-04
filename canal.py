import socket
import threading
import pickle
import random
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

erro = informacoes[0] / 100

modulacao_desejada = informacoes[1]

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

# Essa função é responsável por receber o ack do receptor e retransmitir ao transmissor
def receptor_transmissor(socket_transmissor, socket_receptor, erro):
    while True:
        amostra = socket_receptor.recv(1).decode("utf-8")  # Recebimento de parte do ack do receptor

        if amostra:
            if amostra == 'l':
                amostra = "low"
            elif amostra == 'h':
                amostra = "high"
            elif amostra == 'n':
                amostra = "null"

            # Inserir erro no ack
            amostra = introduzir_erro(amostra, erro)

            socket_transmissor.send(amostra[0].encode("utf-8"))

def introduzir_erro(amostra, erro):
    global thread_queue, modulacao_desejada

    if amostra == '0' or amostra == '1':
        if random.random() < erro:
            if amostra == '0':
                amostra  = '1'
            else:
                amostra = '0'
    
    else:
        if modulacao_desejada == "NRZ-Polar" or modulacao_desejada == "Manchester":
                if random.random() < erro:
                    if amostra == "high":
                        amostra = "low"
                    else:
                        amostra = "high"

        else:

            if random.random() < erro:
                if amostra == "high":
                    if random.randint(0, 1) == 0:
                        amostra = 'null'
                    else:
                        amostra = "low"
                
                elif amostra == 'null':
                    if random.randint(0, 1) == 0:
                        amostra = "high"
                    else:
                        amostra = "low"

                else:
                    if random.randint(0, 1) == 0:
                        amostra = "high"
                    else:
                        amostra = 'null'

    return amostra

# Inicia uma thread para verificar o recebimento do acknowledgement
while True:
    thread = threading.Thread(target = receptor_transmissor, args = (conn1, canal_transmitir, erro))
    thread.start()

    while True:

        # Dados enviados de transmissor para o receptor
        amostra = conn1.recv(1).decode("utf-8") # Recebe a amostra do transmissor

        if amostra:
            if amostra == 'l':
                amostra = "low"
            elif amostra == 'h':
                amostra = "high"
            elif amostra == 'n':
                amostra = "null"

            # Inserir erro no ack
            amostra = introduzir_erro(amostra, erro)

            canal_transmitir.send(amostra[0].encode("utf-8"))