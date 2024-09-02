import socket
import threading
import matplotlib.pyplot as plt
import pickle
import struct
import queue
import time

import camada_fisica.demodulacao_digital as demodulacao_digital
import camada_enlace.deteccao_correcao_erro as deteccao_correcao_erro

IP_receptor = socket.gethostbyname(socket.gethostname())  # IP da máquina receptora
PORT_receptor = 8002 # Port genérica
ADDR = (IP_receptor, PORT_receptor)

# Criação do canal como socket, fazendo uso de IPV4 e TCP para receber o sinal do transmissor
receptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associação do socket ao IP e porta definidos, para receber o sinal
receptor.bind(ADDR)

receptor.listen()

conn, addr1 = receptor.accept()

while True:
    dados_recebidos = conn.recv(256)
    if dados_recebidos:
        break

receptor.close()

lista_info = pickle.loads(dados_recebidos)

modulacao_digital = lista_info[0]
metodo_deteccao_correcao = lista_info[1]
metodo_enquadramento = lista_info[2]

# Criação do canal como socket, fazendo uso de IPV4 e TCP para receber o sinal do canal
receptor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associação do socket ao IP e porta definidos, para receber o sinal
receptor.bind(ADDR)

receptor.listen()

conn, addr1 = receptor.accept()

def enviar_ack(socket, mensagem_valida, mensagem_finalizada):
    if mensagem_valida and mensagem_finalizada:
        for _ in range(8):
            socket.send(b'1')
    else:
        for _ in range(8):
            socket.send(b'0')

def deteccao_delimitadores(metodo_enquadramento, amostra):
    global thread_queue, buffer_quadro, valor_contador, buffer_byte, flag_inicio, flag_fim, mensagem_valida, mensagem_finalizada
    if thread_queue.qsize() > 1:
        (thread_queue.get()).join() # Espera até a thread anterior terminar
    if metodo_enquadramento == "Contagem de caracteres":
        # Caso ainda não tenha sido identificado o contador
        if valor_contador == 0:
            buffer_contador += amostra
        
        else:
            buffer_quadro += amostra
            if len(buffer_quadro) // 8 == valor_contador:   # Se tiver atingido exatamente a contagem de bytes
                buffer_contador = ""
                valor_contador = 0
                mensagem_finalizada = True

        if len(buffer_contador) == 8:
            valor_contador = int(buffer_contador, 2)
        
    elif metodo_enquadramento == "Inserção de bytes":
        # Sempre completa 8 bits antes da análise
        buffer_byte += amostra

        if len(buffer_byte) == 8:
            if buffer_byte == "01111110":    # Flag

                if len(buffer_quadro) < 8:
                        buffer_quadro = buffer_byte

                else:
                    if buffer_quadro[-8:] == "01111101":
                        buffer_quadro = buffer_quadro[:-8] + buffer_byte
                    
                    else:

                        if not(flag_inicio):
                            flag_inicio = True
                            
                        else:
                            if not(flag_fim):
                                flag_fim = True
                                mensagem_finalizada = True

            if flag_inicio and not(flag_fim):

                if buffer_byte == "01111101":     # Escape

                    if len(buffer_quadro) < 8:
                        buffer_quadro = buffer_byte

                    else:
                        if buffer_quadro[-8:] == "01111101":
                            buffer_quadro = buffer_quadro[:-8] + buffer_byte
                    
                        else:
                            buffer_quadro += buffer_byte

                else:
                    buffer_quadro += buffer_byte

                buffer_byte = ""

    else:
        # Sempre completa 8 bits antes da análise
        buffer_byte += amostra

        if len(buffer_byte) == 8:
            if buffer_byte == "01111110":    # Flag
                            
                if not(flag_inicio):
                    flag_inicio = True
                            
                else:
                    if not(flag_fim):
                        flag_fim = True
                        mensagem_finalizada = True

                if len(buffer_quadro) > 0:
                    buffer_quadro = buffer_quadro[:-8]

            if flag_inicio and not(flag_fim):
                
                # Caso sejam cinco 1s seguindos de um 0
                if buffer_byte[-6:] == "111110":
                    pass

                # Caso sejam sete 1s seguidos
                if buffer_byte[-7:] == "1111111":
                    mensagem_valida = False

                # Outros casos
                else:
                    buffer_quadro += amostra

            buffer_byte = buffer_byte[:7]

def demodulacao_amostra(modulacao_digital, metodo_enquadramento, amostra):
    global n_manchester, n_bipolar

    if modulacao_digital == "NRZ-Polar":
        amostra_demodulada = demodulacao_digital.NRZ_polar(amostra)
    elif modulacao_digital == "Manchester":
        amostra_demodulada, n_manchester = demodulacao_digital.Manchester(amostra, n_manchester)
    else:
        amostra_demodulada, n_bipolar = demodulacao_digital.Bipolar(amostra, n_bipolar)

    if modulacao_digital != "Manchester" or len(n_manchester) == 2:
        deteccao_delimitadores(metodo_enquadramento, amostra_demodulada)

quadros = []
flag_encerrar = False
while True:
    if flag_encerrar:
        break

    n_manchester = ""        # Valor acumulado do sinal Manchester durante um ciclo de clock
    n_bipolar = True        # Verifica se o valor atualmente esperado é "high" ou "low"

    buffer_quadro = ""    # Armazena o conteúdo da mensagem sem delimitadores

    buffer_contador = ""    # Armazena o buffer do contador para o caso da contagem de caracteres
    valor_contador = 0      # Valor do contador para o caso da contagem de caracteres

    buffer_byte = ""        # Armazena o último byte lido na inserção de bytes
    flag_inicio = False     # Sinaliza que foi encontrado o byte de flag no início
    flag_fim = False        # Sinaliza que foi encontrado o byte de flag no final

    mensagem_valida = True     # Sinaliza se a mensagem é válida ou não
    mensagem_finalizada = False     # Sinaliza se todos os delimitadores já foram encontrados

    thread_queue = queue.Queue()    # Fila que irá armazenar as threads em andamento, para garantir que não ocorra erro de runtime

    flag_tempo = False
    while True:
        amostra = conn.recv(1).decode("utf-8") # Recebe a amostra, que pode ser "low", "high" ou '0'

        if flag_tempo:
            if time.time() - tempo_referencia > 5:
                mensagem_valida = False
                thread2 = threading.Thread(target = enviar_ack, args = (conn, mensagem_valida, mensagem_finalizada))  # Thread para enviar o ack
                break

        if not(mensagem_valida):
            thread2 = threading.Thread(target = enviar_ack, args = (conn, mensagem_valida, mensagem_finalizada))  # Thread para enviar o ack
            thread2.start()
            break
                
        if amostra:
            if amostra == 'l':
                amostra = "low"
            elif amostra == 'h':
                amostra = "high"

            if mensagem_valida:
                flag_tempo = True
                tempo_referencia = time.time()

                thread = threading.Thread(target = demodulacao_amostra, args = (modulacao_digital, metodo_enquadramento, amostra))
                thread_queue.put(thread)
                thread.start()

        if mensagem_finalizada and mensagem_valida:

            # Com um quadro "válido", podemos agora fazer a detecção/correção de erros como última etapa
            for i in range(len(metodo_deteccao_correcao)):
                if metodo_deteccao_correcao[i] == "Bit_paridade":
                    bit_paridade = buffer_quadro[-1]
                    buffer_quadro = buffer_quadro[:-1]
                
                elif metodo_deteccao_correcao[i] == "Checksum":
                    checksum = buffer_quadro[-16:]
                    buffer_quadro = buffer_quadro[:-16]

                elif metodo_deteccao_correcao[i] == "CRC":
                    crc = buffer_quadro[-31:]
                    buffer_quadro = buffer_quadro[:-31]

                elif metodo_deteccao_correcao[i] == "Hamming":
                    n_hamming = 0
                    if len(metodo_deteccao_correcao) == i + 1:
                        n_hamming = 0
                    else:
                        for metodo in metodo_deteccao_correcao[i + 1:]:
                            if metodo == "Bit_paridade":
                                n_hamming += 1
                            elif metodo == "Checksum":
                                n_hamming += 16
                            elif metodo == "CRC":
                                n_hamming += 31

                    n_hamming = len(buffer_byte) - n_hamming
                    n_hamming = (bin(n_hamming))[2:]    # Valor binário do número de posições identificadas
                    n_hamming = len(n_hamming)  # Quantidade de valores em binário necessários para codificar a mensagem inteira

                    hamming = buffer_quadro[-n_hamming:]
                    buffer_quadro =  buffer_quadro[:-n_hamming]

            for metodo in metodo_deteccao_correcao:
                if metodo == "Bit_paridade":
                    verificador = deteccao_correcao_erro.bit_paridade(buffer_quadro, bit_paridade)
                
                elif metodo == "Checksum":
                    verificador = deteccao_correcao_erro.checksum(buffer_quadro, checksum)

                elif metodo == "CRC":
                    verificador = deteccao_correcao_erro.crc(buffer_quadro, crc)

                elif metodo == "Hamming":
                    quadro, verificador = deteccao_correcao_erro.crc(buffer_quadro, hamming)

                if not(verificador):
                    mensagem_valida = False
                    thread2 = threading.Thread(target = enviar_ack, args = (conn, mensagem_valida, mensagem_finalizada))  # Thread para enviar o ack
                    thread2.start()
                    break

            # Único caso de envio do ack confirmando o recebimento correto do código
            if verificador:
                thread2 = threading.Thread(target = enviar_ack, args = (conn, mensagem_valida, mensagem_finalizada))  # Thread para enviar o ack
                thread2.start()
                quadros.append(quadro)    

    # Recebimento da confirmação do ack ou nack pelo transmissor
    ack_check = ""
    while True:
        sinal = socket.recv(1)  # Recebimento da confirmação do ack
        ack_check += sinal
        if len(ack_check) == 8:
            if ack_check.count(0) > 4:
                flag_encerrar = True
            break

mensagem_completa = ""
for quadro in quadros:
    mensagem_completa += quadro

print(mensagem_completa)