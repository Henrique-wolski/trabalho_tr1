# Este arquivo contem as modulacões por portadora ASK, FSK e 8-QAM

import math

# Modulação ASK
def ASK(bitstream, frequencia, amplitude1, amplitude2, amplitude3):
    signal = []
    
    for i in bitstream:
        if i == "high":
            for j in range(1, 101):
                signal.append(amplitude1 * (math.sin(2 * math.pi * frequencia * (j / 100))))
        
        elif i == "null":
            for j in range(1, 101):
                signal.append(amplitude2 * (math.sin(2 * math.pi * frequencia * (j / 100))))

        else:
            for j in range(1, 101):
                signal.append(amplitude3 * (math.sin(2 * math.pi * frequencia * (j / 100))))

    return signal

# Modulação FSK
def FSK(bitstream, frequencia1, frequencia2, frequencia3, amplitude):
    signal = []
    
    for i in bitstream:
        if i == "high":
            for j in range(1, 101):
                signal.append(amplitude * (math.sin(2 * math.pi * frequencia1 * (j / 100))))
        
        elif i == "null":
            for j in range(1, 101):
                signal.append(amplitude * (math.sin(2 * math.pi * frequencia2 * (j / 100))))

        else:
            for j in range(1, 101):
                signal.append(amplitude * (math.sin(2 * math.pi * frequencia3 * (j / 100))))

    return signal

# Modulação 8-QAM
def QAM8(bitstream, frequencia, amplitude, flag):
    signal = []
    sequencia_3bits = ""
    amplitudes = [(1,0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), (0.7, -0.7)]    # Valores arbitrários

    if flag:
        for i in bitstream:
            if i == "low":
                amp_i = amplitudes[0][0]
                amp_q = amplitudes[0][1]

            if i == "null":
                amp_i = amplitudes[2][0]
                amp_q = amplitudes[2][1]

            if i == "high":
                amp_i = amplitudes[4][0]
                amp_q = amplitudes[4][1]
            
            for j in range(1, 101):
                signal.append((amp_i * amplitude * (math.cos(2 * math.pi * frequencia * (j / 100))))
                                + (amp_q * amplitude * (math.sin(2 * math.pi * frequencia * (j / 100)))))
            
    else:
        for i in range(len(bitstream)):

            if bitstream[i] == "low":
                sequencia_3bits += '0'
            else:
                sequencia_3bits += '1'

            # Caso a sequência não seja um múltiplo de 3

            if i + 1 == len(bitstream):
                if len(sequencia_3bits) == 1:
                    sequencia_3bits += "00"
                elif len(sequencia_3bits) == 2:
                    sequencia_3bits += '0'

            if len(sequencia_3bits) == 3:
                if sequencia_3bits == "000":
                    amp_i = amplitudes[0][0]
                    amp_q = amplitudes[0][1]

                elif sequencia_3bits == "001":
                    amp_i = amplitudes[1][0]
                    amp_q = amplitudes[1][1]

                elif sequencia_3bits == "011":
                    amp_i = amplitudes[2][0]
                    amp_q = amplitudes[2][1]

                elif sequencia_3bits == "010":
                    amp_i = amplitudes[3][0]
                    amp_q = amplitudes[3][1]

                elif sequencia_3bits == "110":
                    amp_i = amplitudes[4][0]
                    amp_q = amplitudes[4][1]

                elif sequencia_3bits == "111":
                    amp_i = amplitudes[5][0]
                    amp_q = amplitudes[5][1]

                elif sequencia_3bits == "101":
                    amp_i = amplitudes[6][0]
                    amp_q = amplitudes[6][1]

                else:
                    amp_i = amplitudes[7][0]
                    amp_q = amplitudes[7][1]

                for j in range(1, 101):
                    signal.append((amp_i * amplitude * (math.cos(2 * math.pi * frequencia * (j / 100))))
                                    + (amp_q * amplitude * (math.sin(2 * math.pi * frequencia * (j / 100)))))
                    
                sequencia_3bits = ""
                
    return signal