import sys

# OPCODES 
OPCODES = {
    "add":      {"code": "00000001", "tipo": "R_R_R"},
    "sub":      {"code": "00000010", "tipo": "R_R_R"},
    "zero":     {"code": "00000011", "tipo": "R"},
    "xor":      {"code": "00000100", "tipo": "R_R_R"},
    "or":       {"code": "00000101", "tipo": "R_R_R"},
    "passnota": {"code": "00000110", "tipo": "R_R"},
    "and":      {"code": "00000111", "tipo": "R_R_R"},
    "asl":      {"code": "00001000", "tipo": "R_R_R"},
    "asr":      {"code": "00001001", "tipo": "R_R_R"},
    "lsl":      {"code": "00001010", "tipo": "R_R_R"},
    "lsr":      {"code": "00001011", "tipo": "R_R_R"},
    "passa":    {"code": "00001100", "tipo": "R_R"},
    "lclh":     {"code": "00001110", "tipo": "CONST"},
    "lcll":     {"code": "00001111", "tipo": "CONST"},
    "load":     {"code": "00010000", "tipo": "R_R"},
    "store":    {"code": "00010001", "tipo": "R_R"},
    "jr":       {"code": "00010011", "tipo": "R"},
    "beq":      {"code": "00010100", "tipo": "BRANCH"},
    "bne":      {"code": "00010101", "tipo": "BRANCH"},
    "jal":      {"code": "00010010", "tipo": "J"},
    "j":        {"code": "00010110", "tipo": "J"},
    "halt":     {"code": "11111111", "tipo": "NONE"}
}

# FUNÇÕES AUXILIARES
def reg_to_bin(reg):
    """ Converte 'r3' para '00000011' """
    try:
        num = int(reg.lower().replace("r", "").replace(",", ""))
        return f"{num:08b}"
    except:
        return "00000000"

def num_to_bin(num, bits):
    """ Converte decimal **ou binário** para binário com N bits """
    num = num.replace(",", "")

    # Se já é binário puro (ex: 101010)
    if all(c in "01" for c in num) and len(num) <= bits:
        return num.zfill(bits)
    # Se for decimal
    try:
        return f"{int(num):0{bits}b}"[-bits:]
    except:
        return "0" * bits

# FUNÇÃO DE MONTAGEM DE LINHA
def montar_instrucao(linha):
    partes = linha.strip().replace(",", " ").split()

    if not partes or linha.strip().startswith(("#", "//")):
        return None

    cmd = partes[0].lower()

    if cmd == "address":
        return f"address {num_to_bin(partes[1], 16)}"

    if cmd not in OPCODES:
        return None

    op, tipo = OPCODES[cmd]["code"], OPCODES[cmd]["tipo"]
    args = partes[1:]

    # R_R_R  opcode | ra | rb | rc
    if tipo == "R_R_R":
        return op + reg_to_bin(args[1]) + reg_to_bin(args[2]) + reg_to_bin(args[0])

    # R_R  opcode | ra | 00 | rc
    if tipo == "R_R":
        return op + reg_to_bin(args[1]) + "00000000" + reg_to_bin(args[0])

    # R  opcode | 00 | 00 | rc
    if tipo == "R":
        return op + "00000000" + "00000000" + reg_to_bin(args[0])

    # CONST  opcode | const16 | rc
    if tipo == "CONST":
        return op + num_to_bin(args[1], 16) + reg_to_bin(args[0])

    # BRANCH  opcode | ra | rb | end(8 bits)
    if tipo == "BRANCH":
        return op + reg_to_bin(args[0]) + reg_to_bin(args[1]) + num_to_bin(args[2], 8)

    # J opcode | end(24 bits)
    if tipo == "J":
        return op + num_to_bin(args[0], 24)

    # NONE HALT
    if tipo == "NONE":
        return "1" * 32

    return None

def main():
    print("--- GERANDO BINÁRIO ---")

    try:
        with open("teste.txt", "r") as fin, open("programa.bin", "w") as fout:
            for linha in fin:
                b = montar_instrucao(linha)
                if b:
                    fout.write(b + "\n")

        print("SUCESSO! Arquivo 'programa.bin' gerado!")
    except Exception as e:
        print(f"ERRO: {e}")


if __name__ == "__main__":
    main()