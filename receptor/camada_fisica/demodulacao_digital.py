# Este arquivo contem as demodulacões digitais NRZ-Polar, Manchester e Bipolar

def NRZ_polar(amostra):
    if amostra == "low":
        return '0'
    else:
        return '1'
    
def Manchester(amostra, n_manchester):
    if n_manchester == "":
        return(amostra, amostra)
    
    else:
        if n_manchester == "high" and amostra == "low":
            return('1', "")

        else:
            return('0', "")
    # Neste caso, caso aconteça um erro gerando um "high-high" ou "low-low", é interpretado como "0" e o erro será possivelmente tratado na camada de enlace

def Bipolar(amostra, n_bipolar):
    if amostra == '0':
        return (amostra, n_bipolar)
    else:
        return('1', not(n_bipolar))
    
# Para o caso da demodulação Manchester e Bipolar, um erro poderia ser detectado ainda na camada física,
# e a retransmissão solicitada. Porém, como decisão de projeto, foi optado por não tomar nenhuma atitude
# aqui e prosseguir com um valor arbitrário (estando ele certo ou não). O motivo disso é que a detecção/
# correção de erro se tornaria sem propósito para estes casos, além de que, para taxas de erros maiores,
# potencialmente todos os quadros seriam parados pela camada física, onde uma retransmissão seria solici-
# tada.