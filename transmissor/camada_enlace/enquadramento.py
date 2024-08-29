# Este arquivo contem os métodos de enquadramento contagem de caracteres, inserção de bytes e inserção de caracteres

# Conversão de inteiro até 255 em byte
def int_para_byte(inteiro):
    byte = bin(inteiro)[2:]
    byte = ((8 - len(byte)) * '0') + byte
    return byte

# Contagem de caracteres
def contagem_caracteres(mensagem, tamanho_quadro):
    quadros = []
    quadro = ""
    contador = 0
    for i in range(len(mensagem)):
        if (i + 1) % 8 == 0:
            contador += 1

        quadro += mensagem[i]

        if contador == tamanho_quadro:

            quadros.append([int_para_byte(tamanho_quadro + 1), int_para_byte(0) + quadro])
            quadro = ""
            contador = 0

            continue

        if i + 1 == len(mensagem):

            if (len(quadro)) % 8 == 0:
                quadros.append([int_para_byte(contador + 1), int_para_byte(0) + quadro])
            
            else:
                preencher_bits = 8 - ((len(quadro)) % 8)

                quadro = quadro + ('0' * preencher_bits)

                quadros.append([int_para_byte(contador + 2), (int_para_byte(preencher_bits)) + quadro])

    return quadros

# Inserção de bytes
def insercao_bytes(mensagem, tamanho_quadro):
    quadros = []
    quadro = ""
    byte = ""
    contador = 0
    for i in range(len(mensagem)):

        byte += mensagem[i]

        if (i + 1) % 8 == 0:
            contador += 1
            # Flag
            if byte == "01111110":
                quadro += "01111101"
            
            # Escape
            if byte == "01111101":
                quadro += "01111101"
            
            quadro += byte

            byte = ""

        if contador == tamanho_quadro:

            quadros.append(["01111110" + int_para_byte(0), quadro, "01111110"])
            quadro = ""
            contador = 0

            continue

        if i + 1 == len(mensagem):

            quadro += byte

            preencher_bits = 8 - ((len(quadro)) % 8)

            quadro = quadro + ('0' * preencher_bits)

            quadros.append(["01111110" + (int_para_byte(preencher_bits)), quadro, "01111110"])

    return quadros

# Inserção de caracteres
def insercao_caracteres(mensagem, tamanho_quadro):
    quadros = []
    quadro = ""
    seq_bits = ""
    contador = 0

    for i in range(len(mensagem)):
        seq_bits += mensagem[i]
        quadro += mensagem[i]

        if len(seq_bits) > 5:
            seq_bits = seq_bits[1:]

        if seq_bits == "11111":
            quadro += '0'
            seq_bits = ""

        if (i + 1) % 8 == 0:
            contador += 1

        if contador == tamanho_quadro or (i + 1) == len(mensagem):
            quadros.append(["01111110", quadro, "01111110"])

            quadro = ""
            seq_bits = ""
            contador = 0

    return quadros