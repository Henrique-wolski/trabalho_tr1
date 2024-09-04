import socket
import matplotlib.pyplot as plt
import pickle
import threading
import time

import camada_fisica.modulacao_digital as modulacao_digital
import camada_fisica.modulacao_por_portadora as modulacao_por_portadora
import camada_enlace.enquadramento as enquadramento
import camada_enlace.deteccao_correcao_erro as deteccao_correcao_erro

# Solicitação da mensagem ao usuário
while True:
    mensagem = "010101010" #input("Entre com a mensagem (somente 0s e 1s):")

    # Caso a mensagem seja nula
    if len(mensagem) == 0:
        print("Esta mensagem é nula.")
        continue

    flag = False    # flag para saber se houve algum valor diferente de 0 ou 1
    for i in mensagem:
        if i != '0' and i != '1':
            flag = True
            continue
    
    if flag:
        print("A mensagem contem valores diferentes de 0 e 1.")
        continue
    
    break

# Camada de Enlace

with open("mensagem.txt", 'r') as arquivo:
    mensagem = arquivo.read()

# Primeiramente, definimos o payload que irá compor cada quadro

tamanho_payload = 32    # bytes

quadros = []
quadro = ""

# Processor de divisão da mensagem em quadros, para processamento posterior
for i in range(len(mensagem)):
    quadro += mensagem[i]
    if (i + 1) % (8 * 32) == 0:
        quadros.append([quadro])
        quadro = ""
quadros.append([quadro])

# Detecção e Correção de erros

while True:
    metodo_deteccao_correcao = "Bit_paridade Checksum CRC" #input("Método de detecção/correção de erro a ser aplicado (Bit_paridade, Checksum, CRC, Hamming):")

    if metodo_deteccao_correcao == "":
        metodo_deteccao_correcao = []
        break

    metodo_deteccao_correcao = metodo_deteccao_correcao.split()

    n_operacoes = 0

    for metodo in metodo_deteccao_correcao:

        if n_operacoes >= 4:
            break

        if metodo == "Bit_paridade":

            quadros = deteccao_correcao_erro.bit_paridade(quadros)

            n_operacoes += 1

            continue

        elif metodo == "Checksum":

            quadros = deteccao_correcao_erro.checksum(quadros)

            n_operacoes += 1

            continue

        elif metodo == "CRC":

            quadros = deteccao_correcao_erro.crc(quadros)

            n_operacoes += 1

            continue

        elif metodo == "Hamming":

            quadros = deteccao_correcao_erro.hamming(quadros)

            n_operacoes += 1

            continue

    if n_operacoes >= 1:
        break

# Solicitação do método para enquadramento
while True:
    metodo_enquadramento = "Inserção de bytes" #input("Método de enquadramento a ser aplicado (Contagem de caracteres, Inserção de bytes, Inserção de caracteres):")
    if metodo_enquadramento == "Contagem de caracteres":
        
        tamanho_quadro = 32

        quadros = enquadramento.contagem_caracteres(quadros)

        break

    elif metodo_enquadramento == "Inserção de bytes":

        tamanho_quadro = 32

        quadros = enquadramento.insercao_bytes(quadros)

        break

    elif metodo_enquadramento == "Inserção de caracteres":

        tamanho_quadro = 32

        quadros = enquadramento.insercao_caracteres(quadros)

        break

# Camada Física

# Modulação digital

# Solicitação do tipo de modulação digital ao usuário
while True:
    modulacao_digital_desejada = "Manchester"    #input("Modulação digital a ser aplicada (NRZ-Polar, Manchester ou Bipolar):")
    if modulacao_digital_desejada == "NRZ-Polar":
        quadros_modulados = []
        for quadro in quadros:
            quadro_modulado = modulacao_digital.NRZ_polar(quadro)
            quadros_modulados.append(quadro_modulado)
        break

    elif modulacao_digital_desejada == "Manchester":
        quadros_modulados = []
        for quadro in quadros:
            quadro_modulado = modulacao_digital.Manchester(quadro)
            quadros_modulados.append(quadro_modulado)
        break

    elif modulacao_digital_desejada == "Bipolar":
        quadros_modulados = []
        for quadro in quadros:
            quadro_modulado = modulacao_digital.Bipolar(quadro)
            quadros_modulados.append(quadro_modulado)
        break
    
    else:
        print("Esta modulação digital é inválida.")

# Modulação por portadora

# Colapsar os quadros para visualização da modulação por portadora

mensagem_modulada = ""
for quadro in quadros_modulados:
    for componente in quadro:
        mensagem_modulada += componente
'''
# Solicitação do tipo de modulação por portadora ao usuário

while True:
    modulacao_portadora_desejada = "ASK" #input("Modulação por portadora a ser aplicada (ASK, FSK ou 8-QAM):")
    if modulacao_portadora_desejada == "ASK":
        frequencia = float(input("Frequência:"))
        amplitude1 = float(input("Primeira amplitude:"))
        amplitude2 = float(input("Segunda amplitude:"))
        amplitude3 = float(input("Terceira amplitude:"))

        sinal_modulado = modulacao_por_portadora.ASK(mensagem_modulada, frequencia, amplitude1, amplitude2, amplitude3)
        break

    elif modulacao_portadora_desejada == "FSK":
        frequencia1 = float(input("Primeira frequência:"))
        frequencia2 = float(input("Segunda frequência:"))
        frequencia3 = float(input("Terceira frequência:"))
        amplitude = float(input("Amplitude:"))

        sinal_modulado = modulacao_por_portadora.FSK(mensagem_modulada, frequencia1, frequencia2, frequencia3, amplitude)
        break

    elif modulacao_portadora_desejada == "8-QAM":
        frequencia = float(input("Frequência:"))
        amplitude = float(input("Amplitude:"))
        flag = modulacao_digital_desejada == "Bipolar"

        sinal_modulado = modulacao_por_portadora.QAM8(mensagem_modulada, frequencia, amplitude, flag)
        break

    else:
        print("Esta modulação por portadora é inválida.")

valoresx = list(range(len(sinal_modulado)))

for i in range(len(valoresx)):
    valoresx[i] = valoresx[i] / 100

# Trabalhar melhor essa visualização quando a GUI estiver pronta
# Incluir sinal de clock e visualização da modulação digital

# Plotando os valores
plt.plot(valoresx, sinal_modulado)

# Títulos e rótulos (opcional)
plt.title('Gráfico de Linha')
plt.xlabel('Índice')
plt.ylabel('Valores')

# Tentar arrumar o plot para mostrar somente uma janela do sinal

# Mostrando o gráfico
plt.show()

'''


# Envio das modulações e métodos utilizados diretamente para a máquina receptora

IP_receptor = socket.gethostbyname(socket.gethostname())  # IP da máquina receptora
PORT_receptor = 8002 # Port genérica (deve ser a mesma definida no receptor)
ADDR = (IP_receptor, PORT_receptor)

# Criação do tranmissor como socket, fazendo uso de IPV4 e TCP
transmissor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conexão do socket criado com aquele do canal, para que possa enviar o sinal
transmissor.connect(ADDR)

# Com os seguintes dados, o receptor irá se organizar para fazer a demodulação e o desenquadramento corretamente
dados_envio = [modulacao_digital_desejada, metodo_deteccao_correcao, metodo_enquadramento]

# Serializar os dados
dados_envio = pickle.dumps(dados_envio)

transmissor.sendall(dados_envio)

transmissor.close()

# Envio da taxa de erro definida ao canal

IP_canal = socket.gethostbyname(socket.gethostname())  # IP da máquina local
PORT_canal = 8001 # Port genérica (deve ser a mesma definida no canal)
ADDR = (IP_canal, PORT_canal)

# Criação do tranmissor como socket, fazendo uso de IPV4 e TCP
transmissor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conexão do socket criado com aquele do canal, para que possa enviar o sinal
transmissor.connect(ADDR)

# Definição da probabilidade de ocorrência de erro
erro = float(input("Probabilidade de erro (%):"))

dados_envio = [erro, modulacao_digital_desejada]

dados_envio = pickle.dumps(dados_envio)

transmissor.sendall(dados_envio)

time.sleep(1)   # Para garantir que os quadros não comecem a ser enviados antes da probabilidade de erro ser processada pelo canal

def espera_ack(socket, flag):
    global ack

    while True:

        sinal = socket.recv(1).decode("utf-8")  # Recebimento do ack
        if sinal:
            ack += sinal
        if len(ack) == 8:
            if ack.count('0') >= 4:
                ack = '0'
            else:
                ack = '1'

            break

def recebimento_ack(socket, ack, termino):
    if ack == '0':
        for _ in range(8):      
            socket.send('1'.encode("utf-8"))    # Confirmação do recebimento do nack
    else:
        if termino:
            for _ in range(8):
                socket.send('0'.encode("utf-8"))    # Sinalização para finalizar o processo
        else:
            for _ in range(8):
                socket.send('1'.encode("utf-8"))    # Confirmação do recebimento do ack

# Envio da mensagem modulada bit a bit para o canal, onde será introduzido o erro
for i in range(len(quadros_modulados)):
    flag = False
    ack = ""

    # Criação de uma thread para receber o ack
    thread = threading.Thread(target = espera_ack, args = (transmissor, i + 1 == len(quadros_modulados)))
    thread.start()

    while not(flag):

        for amostra in quadros_modulados[i]:

            transmissor.sendall(amostra[0].encode("utf-8"))    # Envio da amostra do sinal

        thread.join()   # Espera a thread terminar
        termino = (i + 1) >= len(quadros_modulados)
        time.sleep(0.01)
        recebimento_ack(transmissor, ack, termino)
        flag = ack == '1'

print(mensagem)
print(len(mensagem))