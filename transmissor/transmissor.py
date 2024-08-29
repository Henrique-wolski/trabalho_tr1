import socket
import threading
import matplotlib.pyplot as plt

import camada_fisica.modulacao_digital as modulacao_digital
import camada_fisica.modulacao_por_portadora as modulacao_por_portadora
import camada_enlace.enquadramento as enquadramento
import camada_enlace.deteccao_correcao_erro as deteccao_correcao_erro

SERVER_IP = socket.gethostbyname(socket.gethostname())  # IP local
PORT = 8001 # Port genérica
ADDR = (SERVER_IP, PORT)

# Criação do tranmissor como socket, fazendo uso de IPV4 e TCP
transmissor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Associação do socket ao IP e porta definidos
transmissor.bind(ADDR)

# Solicitação da mensagem ao usuário
while True:
    mensagem = input("Entre com a mensagem (somente 0s e 1s):")

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

# Enquadramento

# Solicitação do método para 

with open("mensagem.txt", 'r') as arquivo:
    mensagem = arquivo.read()

while True:
    metodo_enquadramento = input("Método de enquadramento a ser aplicado (Contagem de caracteres, Inserção de bytes, Inserção de caracteres):")
    if metodo_enquadramento == "Contagem de caracteres":
        
        tamanho_quadro = 32

        quadros = enquadramento.contagem_caracteres(mensagem, tamanho_quadro)

        break

    elif metodo_enquadramento == "Inserção de bytes":

        tamanho_quadro = 32

        quadros = enquadramento.insercao_bytes(mensagem, tamanho_quadro)

        break

    elif metodo_enquadramento == "Inserção de caracteres":

        tamanho_quadro = 32

        quadros = enquadramento.insercao_caracteres(mensagem, tamanho_quadro)

        break

# Detecção e Correção de erros

metodo_deteccao_correcao = input("Método de detecção/correção de erro a ser aplicado (Bit_paridade, Checksum, CRC, Hamming):")

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

    elif metodo == "CRC":   # Não está funcionando corretamente

        quadros = deteccao_correcao_erro.crc(quadros)

        n_operacoes += 1

        continue

    elif metodo == "Hamming":

        quadros = deteccao_correcao_erro.hamming(quadros)

        n_operacoes += 1

        continue

# Junção do quadros em um grande trem de bits

mensagem_completa = ""
for quadro in quadros:
    for componente in quadro:
        mensagem_completa += componente

# Camada Física

# Modulação digital

# Solicitação do tipo de modulação digital ao usuário
while True:
    modulacao_digital_desejada = input("Modulação digital a ser aplicada (NRZ-Polar, Manchester ou Bipolar):")
    if modulacao_digital_desejada == "NRZ-Polar":
        mensagem_modulada = modulacao_digital.NRZ_polar(mensagem_completa)
        break

    elif modulacao_digital_desejada == "Manchester":
        mensagem_modulada = modulacao_digital.Manchester(mensagem_completa)
        break

    elif modulacao_digital_desejada == "Bipolar":
        mensagem_modulada = modulacao_digital.Bipolar(mensagem_completa)
        break
    
    else:
        print("Esta modulação digital é inválida.")

# Modulação por portadora

# Solicitação do tipo de modulação por portadora ao usuário

while True:
    modulacao_portadora_desejada = input("Modulação por portadora a ser aplicada (ASK, FSK ou 8-QAM):")
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

# Plotando os valores
plt.plot(valoresx, sinal_modulado)

# Títulos e rótulos (opcional)
plt.title('Gráfico de Linha')
plt.xlabel('Índice')
plt.ylabel('Valores')

# Tentar arrumar o plot para mostrar somente uma janela do sinal

# Mostrando o gráfico
plt.show()