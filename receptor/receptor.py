import socket
import threading
import pickle
import queue
import time
import select

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
    readable, writable, errored = select.select([socket], [], [], 0.01)

    if readable:
        descarte = socket.recv(2048)    # Tem como propósito limpar o buffer de envio
    
    else:

        if mensagem_valida and mensagem_finalizada:
            for _ in range(8):
                socket.send('1'.encode("utf-8"))
        else:
            for _ in range(8):
                socket.send('0'.encode("utf-8"))

def deteccao_delimitadores(metodo_enquadramento, amostra):
    global thread_queue, buffer_quadro, buffer_contador, padding, buffer_byte, flag_inicio, flag_fim, mensagem_valida, mensagem_finalizada

    if thread_queue.qsize() > 1:
        (thread_queue.get()).join() # Espera até a thread anterior terminar

    if not(mensagem_finalizada):
        if metodo_enquadramento == "Contagem de caracteres":
            # Caso ainda não tenha sido identificado o contador
            if len(buffer_contador) < 8:
                buffer_contador += amostra

            elif len(padding) < 8:
                padding += amostra
            
            else:
                buffer_quadro += amostra
                if len(buffer_quadro) // 8 == ((int(buffer_contador, 2)) - 1):   # Se tiver atingido exatamente a contagem de bytes
                    if (int(padding, 2)) > 0:
                        buffer_quadro = buffer_quadro[:-(int(padding, 2))]
                    mensagem_finalizada = True
            
        elif metodo_enquadramento == "Inserção de bytes":
            # Sempre completa 8 bits antes da análise
            buffer_byte += amostra

            if len(buffer_byte) == 8:
                if buffer_byte == "01111110":    # Flag

                    if len(buffer_quadro) < 8:
                        buffer_quadro = buffer_byte
                        
                    if buffer_quadro[-8:] == "01111101":
                        buffer_quadro = buffer_quadro[:-8] + buffer_byte
                        
                    else:

                        if not(flag_inicio):
                            flag_inicio = True
                                
                        else:
                            if not(flag_fim):
                                flag_fim = True
                                mensagem_finalizada = True

                                if (int(padding, 2)) > 0:
                                    buffer_quadro = buffer_quadro[16:]
                                    buffer_quadro = buffer_quadro[:-(int(padding, 2))]

                elif flag_inicio and not(flag_fim):

                    if buffer_byte == "01111101":     # Escape

                        if len(buffer_quadro) < 8:
                            buffer_quadro = buffer_byte

                        else:
                            if buffer_quadro[-8:] == "01111101":
                                buffer_quadro = buffer_quadro[:-8] + buffer_byte
                        
                            else:
                                buffer_quadro += buffer_byte

                    else:
                        if len(buffer_quadro) < 16:
                            padding = buffer_byte

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
                        buffer_quadro = buffer_quadro[:-7]

                elif flag_inicio and not(flag_fim):
                    
                    # Caso sejam cinco 1s seguindos de um 0
                    if buffer_byte[-6:] == "111110":
                        pass

                    # Caso sejam sete 1s seguidos
                    elif buffer_byte[-7:] == "1111111":
                        mensagem_valida = False

                    # Outros casos
                    else:
                        buffer_quadro += amostra

                buffer_byte = buffer_byte[1:]

def demodulacao_amostra(modulacao_digital, metodo_enquadramento, amostra):
    global n_manchester, n_bipolar

    if modulacao_digital == "NRZ-Polar":
        amostra_demodulada = demodulacao_digital.NRZ_polar(amostra)
    elif modulacao_digital == "Manchester":
        amostra_demodulada, n_manchester = demodulacao_digital.Manchester(amostra, n_manchester)
    else:
        amostra_demodulada, n_bipolar = demodulacao_digital.Bipolar(amostra, n_bipolar)

    if modulacao_digital != "Manchester" or len(n_manchester) == 0:
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
    padding = ""     # Quantidade de zeros adicionados ao final da mensagem

    buffer_byte = ""        # Armazena o último byte lido na inserção de bytes
    flag_inicio = False     # Sinaliza que foi encontrado o byte de flag no início
    flag_fim = False        # Sinaliza que foi encontrado o byte de flag no final

    mensagem_valida = True     # Sinaliza se a mensagem é válida ou não
    mensagem_finalizada = False     # Sinaliza se todos os delimitadores já foram encontrados

    thread_queue = queue.Queue()    # Fila que irá armazenar as threads em andamento, para garantir que não ocorra erro de corrida

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
            elif amostra == 'n':
                amostra = "null"

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

                    n_hamming = len(buffer_quadro) - n_hamming
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
                    buffer_quadro, verificador = deteccao_correcao_erro.hamming(buffer_quadro, hamming)

                if not(verificador) and not("Hamming" in metodo_deteccao_correcao):
                    mensagem_valida = False
                    thread2 = threading.Thread(target = enviar_ack, args = (conn, mensagem_valida, mensagem_finalizada))  # Thread para enviar o ack
                    thread2.start()
                    break

                else:
                    verificador = True

            # Único caso de envio do ack confirmando o recebimento correto do código
            if verificador:
                thread2 = threading.Thread(target = enviar_ack, args = (conn, mensagem_valida, mensagem_finalizada))  # Thread para enviar o ack
                thread2.start()
                quadros.append(buffer_quadro)
                break 

    # Recebimento da confirmação do ack ou nack pelo transmissor
    ack_check = ""
    while True:
        sinal = conn.recv(1).decode("utf-8")  # Recebimento da confirmação do ack
        if sinal != '0' and sinal != '1':
            continue
        elif sinal:
            ack_check += sinal
            if len(ack_check) == 8:
                if ack_check.count('0') > 4:
                    flag_encerrar = True
                break

mensagem_completa = ""
for quadro in quadros:
    mensagem_completa += quadro

print(mensagem_completa)
print(len(mensagem_completa))