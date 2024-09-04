# Este arquivo contem as modulacões digitais NRZ-Polar, Manchester e Bipolar

# Modulação NRZ-Polar
def NRZ_polar(mensagem):
    mensagem_nrz = []
    for i in mensagem:
        if i == '0':
            mensagem_nrz.append("low")
        else:
            mensagem_nrz.append("high")

    return mensagem_nrz

# Modulação Manchester
def Manchester(mensagem):
    mensagem_manchester = []
    for i in mensagem:
        if i == '0':
            mensagem_manchester.append("low")
            mensagem_manchester.append("high")

        else:
            mensagem_manchester.append("high")
            mensagem_manchester.append("low")

    return mensagem_manchester

# Modulação Bipolar
def Bipolar(mensagem):
    mensagem_bipolar = []
    atual = "low"   # Variável que alterna entre 'low' e 'high' quando o bit for 1

    for i in mensagem:
        if i == '0':
            mensagem_bipolar.append("null")
        else:
            if atual == "low":
                atual = "high"
            else:
                atual = "low"
            mensagem_bipolar.append(atual)

    return mensagem_bipolar