# Este arquivo contem os métodos de enquadramento contagem de caracteres, inserção de bytes e inserção de caracteres

# Conversão de inteiro até 255 em byte
def int_para_byte(inteiro):
    byte = bin(inteiro)[2:]
    byte = ((8 - len(byte)) * '0') + byte
    return byte

# Contagem de caracteres
def contagem_caracteres(quadros):
    quadros_alterados = []

    # Inclusão de toda informação para delimitação do quadro
    for componentes in quadros:
        quadro = ""
        for componente in componentes:
            quadro += componente

        contador = 0

        for i in range(len(quadro)):
            if (i + 1) % 8 == 0:
                contador += 1

        preencher_bits = 8 - ((len(quadro)) % 8)

        if preencher_bits == 8:
            preencher_bits = 0

        # Completa o byte, caso a mensagem esteja fragmentada
        if preencher_bits > 0:
            quadro += '0' * preencher_bits
            contador += 1
        quadro = int_para_byte(preencher_bits) + quadro  # Adiciona um byte informando a quantidade de bits que foram inseridos ao final do payload

        quadro = int_para_byte(contador + 1) + quadro   # Inclusão no começo do quadro da contagem de bytes da mensagem

        quadros_alterados.append(quadro)

    return quadros_alterados

# Inserção de bytes
def insercao_bytes(quadros):
    quadros_alterados = []

    # Inclusão de toda informação para delimitação do quadro
    for componentes in quadros:
        quadro = ""
        for componente in componentes:
            quadro += componente

        quadro_alterado = ""
        byte = ""
        for i in range(len(quadro)):
            byte += quadro[i]

            if (i + 1) == len(quadro):
                # Completa o byte, caso a mensagem esteja fragmentada
                preencher_bits = 8 - ((len(quadro)) % 8)
                if preencher_bits == 8:
                    preencher_bits = 0
                if preencher_bits > 0:
                    byte += '0' * preencher_bits

            if len(byte) == 8:
                # Flag
                if byte == "01111110":
                    quadro_alterado += "01111101"
                
                # Escape
                if byte == "01111101":
                    quadro_alterado += "01111101"
                
                quadro_alterado += byte

                byte = ""

        quadro_alterado = "01111110" + int_para_byte(preencher_bits) + quadro_alterado + "01111110"
        quadros_alterados.append(quadro_alterado)

    return quadros_alterados

# Inserção de caracteres
def insercao_caracteres(quadros):
    quadros_alterados = []
    # Inclusão de toda informação para delimitação do quadro
    for componentes in quadros:
        quadro = ""
        for componente in componentes:
            quadro += componente
        
        seq_bits = ""
        quadro_alterado = ""
        for i in range(len(quadro)):

            quadro_alterado += quadro[i]

            if len(seq_bits) > 5:
                seq_bits = seq_bits[1:]

            if seq_bits == "11111":
                quadro_alterado += '0'
                seq_bits = ""

        quadro_alterado = "01111110" + quadro_alterado + "01111110"
        quadros_alterados.append(quadro_alterado)

    return quadros_alterados