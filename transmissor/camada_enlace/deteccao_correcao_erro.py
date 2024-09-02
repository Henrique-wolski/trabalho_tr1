# Este arquivo contem os métodos de detecção de erros bit de paridade, Checksum e CRC
# e o método de detecção e correção de erros de Hamming

# Bit de paridade
def bit_paridade(quadros):
    quadros_alterados = []
    for quadro in quadros:
        payload = quadro[0]
        
        paridade = (payload.count('1')) % 2 == 0
        
        quadros_alterados.append(quadro)

        if paridade:
            quadros_alterados[-1].insert(1, '0')
        else:
            quadros_alterados[-1].insert(1, '1')

    return quadros_alterados

# Checksum
def checksum(quadros):
    quadros_alterados = []
    for quadro in quadros:
        payload = quadro[0]
        
        checksum = []
        bloco = ""
        blocos = []
        tamanho_bloco = 16

        for i in range(len(payload)):
            bloco += payload[i]
            if (i + 1) % tamanho_bloco == 0:
                blocos.append(bloco)
                bloco = ""
                continue

            if (i + 1) == len(payload):
                bloco += (tamanho_bloco - len(bloco)) * '0'
                blocos.append(bloco)

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

        checksum_str = ""
        for i in checksum:
            if i == '0':
                checksum_str += '1'
            else:
                checksum_str += '0'
            
        quadros_alterados.append(quadro)

        quadros_alterados[-1].insert(1, checksum_str)

    return quadros_alterados

# CRC
def crc(quadros):
    quadros_alterados = []
    crc32 = "10000100110000010001110110110111"      # 0x04C11DB7

    for quadro in quadros:
        payload = quadro[0]
        posicao_1 = payload.find('1')
        if posicao_1 >= 0:
            payload = payload[posicao_1:]
        else:
            payload = ""

        payload += '0' * 31

        while len(payload) > 31:
            
            dividendo = payload[:32]

            resto = ""

            for i in range(len(crc32)):
                if crc32[i] == dividendo[i]:
                    resto += '0'
                else:
                    resto += '1'

            posicao_1 = resto.find('1')

            if posicao_1 > 0:
                payload = resto[posicao_1:] + payload[32:]

            else:
                payload = payload[32:]

        payload = ((31 - len(payload)) * '0') + payload
        quadros_alterados.append(quadro)

        quadros_alterados[-1].insert(1, payload)

    return quadros_alterados

# Hamming
def hamming(quadros):
    quadros_alterados = []

    for quadro in quadros:
        payload = quadro[0]

        max_binario = bin(len(payload))[2:]

        novo_max_binario = bin(len(payload) + len(max_binario))[2:]

        potencias_2 = []

        for i in range(len(novo_max_binario)):
            potencias_2.append(2 ** i)

        payload_list = []
        for i in range(len(payload)):
            payload_list.append(payload[i])

        for i in potencias_2:
            payload_list.insert(i - 1, '0')

        bits_hamming = ['0'] * len(potencias_2)

        for i in range(len(payload_list)):

            if payload_list[i] == '1':
                posicao_binario = (bin(i + 1))[2:]

                for j in range(len(posicao_binario)):
                    if posicao_binario[len(posicao_binario) - j - 1] == '1':
                        if bits_hamming[j] == '1':
                            bits_hamming[j] = '0'
                        else:
                            bits_hamming[j] = '1'

        bits_hamming_str = ""   
        for i in bits_hamming:
            bits_hamming_str += i

        quadros_alterados.append(quadro)

        quadros_alterados[-1].insert(1, bits_hamming_str)

    return quadros_alterados