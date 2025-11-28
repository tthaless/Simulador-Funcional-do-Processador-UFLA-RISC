import sys

# DICIONÁRIO DE INSTRUÇÕES (OPCODES)
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
    "halt":     {"code": "11111111", "tipo": "NONE"},

    # --- 8 INSTRUÇÕES EXTRAS ---
    "mul":      {"code": "00100000", "tipo": "R_R_R"}, # Multiplicação
    "div":      {"code": "00100001", "tipo": "R_R_R"}, # Divisão
    "mod":      {"code": "00100010", "tipo": "R_R_R"}, # Resto da Divisão
    "inc":      {"code": "00100011", "tipo": "R_R"},   # Incremento (+1)
    "dec":      {"code": "00100100", "tipo": "R_R"},   # Decremento (-1)
    "movi":     {"code": "00100101", "tipo": "CONST"}, # Move Immediate (Carrega constante direta)
    "notbit":   {"code": "00100110", "tipo": "R_R_R"}, # Not Bit-a-Bit (Versão com 3 operandos)
    "nop":      {"code": "00100111", "tipo": "NOP"},   # No Operation (Não faz nada)
}

# FUNÇÕES AUXILIARES DE CONVERSÃO
def reg_to_bin(reg):
    """ 
    Converte o nome de um registrador (ex: 'r3', 'R10') para seu código binario de 8 bits.
    Exemplo: 'r3' -> '00000011'
    """
    try:
        # Remove o 'r' e caracteres extras, depois converte para inteiro e formata
        num = int(reg.lower().replace("r", "").replace(",", ""))
        return f"{num:08b}"
    except:
        return "00000000" # Retorna 0 se falhar (segurança)

def num_to_bin(num, bits):
    """ 
    Converte um nuero (string) para binário com N bits.
     Binario explicito começa com '0b' (ex: '0b101' -> 5)
     Decimal padrao apenas numeros (ex: '10' -> 10)
    """
    num = num.replace(",", "")
    
    # Se o usuário digitou binário (ex: 0b101)
    if num.startswith("0b"):
        bin_value = num[2:] # Remove o '0b'
        return bin_value.zfill(bits)[-bits:] # Preenche com zeros a esquerda
    
    # Se o usuário digitou decimal
    try:
        return f"{int(num):0{bits}b}"[-bits:]
    except:
        return "0" * bits # Retorna zeros se não for valido

# NÚCLEO DO MONTADOR (ASSEMBLER)
def montar_instrucao(linha):
    """
    Analisa uma linha de texto Assembly e converte para a instrução de maquina (32 bits)
    Identifica o tipo da instrução (R_R_R, CONST, J, etc) e organiza os bits na ordem correta
    """
    # Limpeza e separação da linha Lexer simples
    partes = linha.strip().replace(",", " ").split()

    # Ignora linhas vazias ou comentarios # ou //
    if not partes or linha.strip().startswith(("#", "//")):
        return None

    cmd = partes[0].lower()

    # Tratamento da diretiva ADDRESS posicao de memoria
    if cmd == "address":
        return f"address {num_to_bin(partes[1], 16)}"

    if cmd not in OPCODES:
        return None

    #Recupera os dados da instrucao
    op = OPCODES[cmd]["code"]
    tipo = OPCODES[cmd]["tipo"]
    args = partes[1:] 

    # Montagem dos bits baseada no TIPO da instrução Parser CodeGen
    
    # Tipo NOP: Instrução vazia enche de zeros
    if tipo == "NOP":
        return op + "0" * 24

    # Tipo R_R_R: Instruções Aritméticas (add, sub...)
    # Ordem Binaria: OPCODE | RA | RB | RC
    # Ordem Escrita: add rc, ra, rb
    if tipo == "R_R_R":
        return op + reg_to_bin(args[1]) + reg_to_bin(args[2]) + reg_to_bin(args[0])

    if tipo == "R_R":
        return op + reg_to_bin(args[1]) + "00000000" + reg_to_bin(args[0])

    # Tipo R: Instruções de 1 Operando zeros, jr
    if tipo == "R":
        return op + "00000000" + "00000000" + reg_to_bin(args[0])

    # Tipo CONST: Carregamento de valor imediato lcl
    if tipo == "CONST":
        return op + num_to_bin(args[1], 16) + reg_to_bin(args[0])

    # Tipo BRANCH: Desvios Condicionais beq, bne
    if tipo == "BRANCH":
        return op + reg_to_bin(args[0]) + reg_to_bin(args[1]) + num_to_bin(args[2], 8)

    # Tipo J: Desvios Incondicionais jump, jal
    if tipo == "J":
        return op + num_to_bin(args[0], 24)

    # Tipo HALT: Parada total
    if tipo == "NONE":
        return "1" * 32

    return None

def main():
    print("--- GERANDO BINÁRIO ---")

    try:
        # Lê o arquivo teste.txt e gera programa.bin
        with open("teste.txt", "r") as fin, open("programa.bin", "w") as fout:
            for linha in fin:
                b = montar_instrucao(linha)
                if b:
                    fout.write(b + "\n")

        print("SUCESSO! Arquivo 'programa.bin' gerado com as instruções binárias.")
    except Exception as e:
        print(f"ERRO: {e}")


if __name__ == "__main__":
    main()