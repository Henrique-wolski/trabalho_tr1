# Este arquivo contem os métodos de detecção de erros bit de paridade, Checksum e CRC
# e o método de detecção e correção de erros de Hamming para o receptor

# Bit de paridade
def bit_paridade(quadro, bit_paridade):
    verificador = '0'
    for bit in quadro:
        if bit == '1':
            if verificador == '0':
                verificador = '1'
            else:
                verificador = '0'
    
    verificador = verificador == bit_paridade
    return verificador

# Checksum
def checksum(quadro, checksum_recebido):
    checksum = []
    bloco = ""
    blocos = []
    tamanho_bloco = 16

    for i in range(len(quadro)):
        bloco += quadro[i]
        if (i + 1) % tamanho_bloco == 0:
            blocos.append(bloco)
            bloco = ""
            continue

        if (i + 1) == len(quadro):
            bloco += (tamanho_bloco - len(bloco)) * '0'
            blocos.append(bloco)

    blocos.append(checksum_recebido)

    carryout = 0
    soma = 0
    for i in range(tamanho_bloco):
        for bloco in blocos:
            soma += int(bloco[tamanho_bloco - i - 1])
            
        soma += carryout
        checksum = [str(soma % 2)] + checksum
            
        carryout = soma // 2

        soma = 0

    contador = tamanho_bloco - 1
    while carryout != 0:
        soma += int(checksum[contador])

        soma += carryout
            
        checksum[contador] = str(soma % 2)

        carryout = soma // 2

        soma = 0

        contador -= 1

        if contador < 0:
            contador = tamanho_bloco - 1

    verificador = True
    for i in checksum:
        if i == '0':
            verificador = False

    return verificador

# CRC
def crc(quadro, crc):
    quadros_alterados = []
    crc32 = "10000100110000010001110110110111"      # 0x04C11DB7

    posicao_1 = quadro.find('1')
    if posicao_1 >= 0:
        quadro = quadro[posicao_1:]
    else:
        quadro = ""

    quadro += crc

    while len(quadro) > 31:
            
        dividendo = quadro[:32]

        resto = ""

        for i in range(len(crc32)):
            if crc32[i] == dividendo[i]:
                resto += '0'
            else:
                resto += '1'

        posicao_1 = resto.find('1')

        if posicao_1 > 0:
            quadro = resto[posicao_1:] + quadro[32:]

        else:
            quadro = quadro[32:]

    quadro = ((31 - len(quadro)) * '0') + quadro

    verificador = True
    for i in quadro:
        if i == '1':
            verificador = False

    return verificador

# Hamming
def hamming(quadro, hamming):
    max_binario = bin(len(quadro))[2:]

    novo_max_binario = bin(len(quadro) + len(max_binario))[2:]

    potencias_2 = []

    for i in range(len(novo_max_binario)):
        potencias_2.append(2 ** i)

    quadro_list = []
    for i in range(len(quadro)):
        quadro_list.append(quadro[i])

    contador = 0
    for i in potencias_2:
        quadro_list.insert(i - 1, hamming(contador))
        contador += 1

    bits_hamming = ['0'] * len(potencias_2)

    for i in range(len(quadro_list)):

        if quadro_list[i] == '1':
            posicao_binario = (bin(i + 1))[2:]

            for j in range(len(posicao_binario)):
                if posicao_binario[len(posicao_binario) - j - 1] == '1':
                    if bits_hamming[j] == '1':
                        bits_hamming[j] = '0'
                    else:
                        bits_hamming[j] = '1'

    verificador = True
    posicao_errada = b""
    for i in bits_hamming[::-1]:
        posicao_errada += i
        verificador = False
    
    # Correção do erro
    if not(verificador):
        posicao_errada = int(posicao_errada, 2) - 1
        if quadro[posicao_errada] == '0':
            quadro = quadro[:posicao_errada] + '1' + quadro[posicao_errada + 1:]
        
        else:
            quadro = quadro[:posicao_errada] + '0' + quadro[posicao_errada + 1:]

        verificador = True

    return (quadro, verificador)

    