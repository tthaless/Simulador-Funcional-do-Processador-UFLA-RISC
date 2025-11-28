"""
Testes Massivos - 
Testa programas completos e realistas para verificar robustez do simulador
"""

import sys
import os
from test_framework import TestFramework

def run_all_massive_tests():
    """Executa todos os testes massivos (programas reais)."""
    
    framework = TestFramework(output_dir="../testes/massivos")
    
    print("\n" + "="*80)
    print("EXECUTANDO TESTES MASSIVOS - PROGRAMAS REAIS")
    print("="*80)
    
    # ========================================================================
    # TESTE MASSIVO 1: Cálculo de Fatorial
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_fatorial",
        assembly_code=[
            "# Calcula fatorial de 4 (4! = 24) - desenrolado",
            "lclh r1, 0",
            "lcll r1, 1",       # R1 = 1
            "lclh r2, 0",
            "lcll r2, 2",       # R2 = 2
            "lclh r3, 0",
            "lcll r3, 3",       # R3 = 3
            "lclh r4, 0",
            "lcll r4, 4",       # R4 = 4
            "mul r5, r1, r2",   # R5 = 1 * 2 = 2
            "mul r5, r5, r3",   # R5 = 2 * 3 = 6
            "mul r5, r5, r4",   # R5 = 6 * 4 = 24
            "halt"
        ],
        expected_results={
            "registers": {1: 1, 2: 2, 3: 3, 4: 4, 5: 24}  # 4! = 24
        },
        description="Calcula fatorial de 4 usando multiplicações sequenciais"
    )
    framework.run_test("programa_fatorial", bin_path, {"registers": {1: 1, 2: 2, 3: 3, 4: 4, 5: 24}})
    
    # ========================================================================
    # TESTE MASSIVO 2: Soma de Array
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_soma_array",
        assembly_code=[
            "# Soma elementos de um array armazenado na memória",
            "# Array: [10, 20, 30, 40, 50] nos endereços 100-104",
            "# Primeiro, armazena os valores na memória",
            "lclh r10, 0",
            "lcll r10, 100",    # R10 = endereço base = 100
            "lclh r1, 0",
            "lcll r1, 10",      # R1 = 10
            "passa r11, r10",   # R11 = 100
            "store r11, r1",    # MEM[100] = 10",
            "lclh r1, 0",
            "lcll r1, 20",      # R1 = 20
            "inc r11, r10",     # R11 = 101
            "store r11, r1",    # MEM[101] = 20",
            "lclh r1, 0",
            "lcll r1, 30",      # R1 = 30
            "lclh r11, 0",
            "lcll r11, 102",    # R11 = 102
            "store r11, r1",    # MEM[102] = 30",
            "lclh r1, 0",
            "lcll r1, 40",      # R1 = 40
            "lclh r11, 0",
            "lcll r11, 103",    # R11 = 103
            "store r11, r1",    # MEM[103] = 40",
            "lclh r1, 0",
            "lcll r1, 50",      # R1 = 50
            "lclh r11, 0",
            "lcll r11, 104",    # R11 = 104
            "store r11, r1",    # MEM[104] = 50",
            "# Agora soma os elementos",
            "lclh r2, 0",
            "lcll r2, 0",       # R2 = soma = 0
            "lclh r3, 0",
            "lcll r3, 0",       # R3 = índice = 0
            "lclh r4, 0",
            "lcll r4, 5",       # R4 = tamanho = 5
            "# Loop de soma (endereço 30)",
            "add r5, r10, r3",  # R5 = endereço_base + índice
            "load r6, r5",      # R6 = MEM[R5]
            "add r2, r2, r6",   # soma = soma + elemento
            "inc r3, r3",       # índice++
            "sub r7, r4, r3",   # R7 = tamanho - índice
            "bne r7, r0, 30",   # Se R7 != 0, continua loop
            "halt"
        ],
        expected_results={
            "registers": {2: 150, 4: 5},  # soma = 10+20+30+40+50 = 150
            "memory": {100: 10, 101: 20, 102: 30, 103: 40, 104: 50}
        },
        description="Soma elementos de um array na memória"
    )
    framework.run_test("programa_soma_array", bin_path, 
                      {"registers": {2: 150}, "memory": {100: 10, 101: 20, 102: 30, 103: 40, 104: 50}})
    
    # ========================================================================
    # TESTE MASSIVO 3: Fibonacci
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_fibonacci",
        assembly_code=[
            "# Calcula os primeiros 7 números de Fibonacci (desenrolado)",
            "# F(0)=0, F(1)=1, F(2)=1, F(3)=2, F(4)=3, F(5)=5, F(6)=8",
            "lclh r1, 0",
            "lcll r1, 0",       # R1 = F(0) = 0
            "lclh r2, 0",
            "lcll r2, 1",       # R2 = F(1) = 1
            "add r3, r1, r2",   # R3 = F(2) = 0 + 1 = 1
            "add r4, r2, r3",   # R4 = F(3) = 1 + 1 = 2
            "add r5, r3, r4",   # R5 = F(4) = 1 + 2 = 3
            "add r6, r4, r5",   # R6 = F(5) = 2 + 3 = 5
            "add r7, r5, r6",   # R7 = F(6) = 3 + 5 = 8
            "halt"
        ],
        expected_results={
            "registers": {1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 5, 7: 8}
        },
        description="Calcula sequência de Fibonacci até F(6)=8"
    )
    framework.run_test("programa_fibonacci", bin_path, {"registers": {1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 5, 7: 8}})
    
    # ========================================================================
    # TESTE MASSIVO 4: Máximo de 3 Números
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_maximo",
        assembly_code=[
            "# Encontra o máximo entre 3 números: 15, 42, 28 (usando subtrações)",
            "lclh r1, 0",
            "lcll r1, 15",      # R1 = 15
            "lclh r2, 0",
            "lcll r2, 42",      # R2 = 42
            "lclh r3, 0",
            "lcll r3, 28",      # R3 = 28
            "# Compara R1 e R2, pega o maior",
            "sub r4, r2, r1",   # R4 = R2 - R1 = 27 (positivo, R2 > R1)
            "passa r5, r2",     # R5 = R2 (assumimos R2 é maior)
            "# Compara R5 e R3, pega o maior",
            "sub r6, r3, r5",   # R6 = R3 - R5 = 28 - 42 = -14 (negativo, R5 > R3)
            "# R5 já contém o máximo (42)",
            "halt"
        ],
        expected_results={
            "registers": {1: 15, 2: 42, 3: 28, 5: 42}  # máximo em R5 = 42
        },
        description="Encontra o máximo entre 3 números"
    )
    framework.run_test("programa_maximo", bin_path, {"registers": {1: 15, 2: 42, 3: 28, 5: 42}})
    
    # ========================================================================
    # TESTE MASSIVO 5: Operações Bit a Bit Complexas
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_bitwise",
        assembly_code=[
            "# Testa combinações complexas de operações bit a bit",
            "lclh r1, 0",
            "lcll r1, 170",     # R1 = 170 (0b10101010)
            "lclh r2, 0",
            "lcll r2, 85",      # R2 = 85  (0b01010101)
            "and r3, r1, r2",   # R3 = 170 AND 85 = 0
            "or r4, r1, r2",    # R4 = 170 OR 85 = 255
            "xor r5, r1, r2",   # R5 = 170 XOR 85 = 255
            "passnota r6, r1",  # R6 = NOT 170
            "lclh r7, 0",
            "lcll r7, 2",       # R7 = 2
            "lsl r8, r1, r7",   # R8 = 170 << 2 = 680
            "lsr r9, r1, r7",   # R9 = 170 >> 2 = 42
            "halt"
        ],
        expected_results={
            "registers": {
                1: 170, 2: 85, 3: 0, 4: 255, 5: 255,
                6: ~170 & 0xFFFFFFFF, 7: 2, 8: 680, 9: 42
            }
        },
        description="Testa operações bit a bit complexas"
    )
    framework.run_test("programa_bitwise", bin_path, {
        "registers": {1: 170, 2: 85, 3: 0, 4: 255, 5: 255, 7: 2, 8: 680, 9: 42}
    })
    
    # ========================================================================
    # TESTE MASSIVO 6: Subrotina com JAL e JR
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_subrotina",
        assembly_code=[
            "# Programa principal chama subrotina que dobra um número",
            "lclh r1, 0",       # endereço 0
            "lcll r1, 21",      # endereço 1: R1 = 21
            "jal 5",            # endereço 2: Chama subrotina no endereço 5
            "passa r3, r2",     # endereço 3: R3 = resultado (42)
            "halt",             # endereço 4
            "# Subrotina: dobra o valor de R1 e retorna em R2",
            "add r2, r1, r1",   # endereço 5: R2 = R1 + R1 (dobra)
            "jr r31"            # endereço 6: Retorna para quem chamou (PC=3)
        ],
        expected_results={
            "registers": {1: 21, 2: 42, 3: 42, 31: 3}
        },
        description="Testa chamada de subrotina com JAL e retorno com JR"
    )
    framework.run_test("programa_subrotina", bin_path, {"registers": {1: 21, 2: 42, 3: 42, 31: 3}})
    
    # ========================================================================
    # TESTE MASSIVO 7: Divisão e Resto (Instruções Extras)
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_divisao_resto",
        assembly_code=[
            "# Calcula quociente e resto de 100 / 7",
            "lclh r1, 0",
            "lcll r1, 100",     # R1 = 100
            "lclh r2, 0",
            "lcll r2, 7",       # R2 = 7
            "div r3, r1, r2",   # R3 = 100 / 7 = 14
            "mod r4, r1, r2",   # R4 = 100 % 7 = 2
            "# Verifica: 100 = 14*7 + 2",
            "mul r5, r3, r2",   # R5 = 14 * 7 = 98
            "add r6, r5, r4",   # R6 = 98 + 2 = 100
            "halt"
        ],
        expected_results={
            "registers": {1: 100, 2: 7, 3: 14, 4: 2, 5: 98, 6: 100}
        },
        description="Testa divisão e resto com verificação"
    )
    framework.run_test("programa_divisao_resto", bin_path, 
                      {"registers": {1: 100, 2: 7, 3: 14, 4: 2, 5: 98, 6: 100}})
    
    # ========================================================================
    # TESTE MASSIVO 8: Contador Decrescente com Flags
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_contador_decrescente",
        assembly_code=[
            "# Contador decrescente de 10 até 0",
            "lclh r1, 0",
            "lcll r1, 10",      # R1 = 10
            "# Loop (endereço 2)",
            "dec r1, r1",       # R1--
            "bne r1, r0, 2",    # Se R1 != 0, continua
            "halt"
        ],
        expected_results={
            "registers": {1: 0},
            "flags": {"zero": 1}  # Flag zero deve estar ativada
        },
        description="Contador decrescente até zero"
    )
    framework.run_test("programa_contador_decrescente", bin_path, 
                      {"registers": {1: 0}, "flags": {"zero": 1}})
    
    # ========================================================================
    # TESTE MASSIVO 9: Manipulação de Memória Complexa
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_memoria_complexa",
        assembly_code=[
            "# Copia valores de um array para outro, invertendo a ordem",
            "# Array origem: endereços 200-204 com valores [1,2,3,4,5]",
            "# Array destino: endereços 300-304",
            "# Primeiro, preenche array origem",
            "lclh r10, 0",
            "lcll r10, 200",    # R10 = base origem
            "lclh r1, 0",
            "lcll r1, 1",
            "passa r11, r10",
            "store r11, r1",    # MEM[200] = 1
            "lclh r1, 0",
            "lcll r1, 2",
            "inc r11, r10",
            "store r11, r1",    # MEM[201] = 2
            "lclh r1, 0",
            "lcll r1, 3",
            "lclh r11, 0",
            "lcll r11, 202",
            "store r11, r1",    # MEM[202] = 3
            "lclh r1, 0",
            "lcll r1, 4",
            "lclh r11, 0",
            "lcll r11, 203",
            "store r11, r1",    # MEM[203] = 4
            "lclh r1, 0",
            "lcll r1, 5",
            "lclh r11, 0",
            "lcll r11, 204",
            "store r11, r1",    # MEM[204] = 5
            "# Agora copia invertido",
            "lclh r20, 0",
            "lcll r20, 300",    # R20 = base destino
            "lclh r3, 0",
            "lcll r3, 0",       # R3 = índice = 0
            "lclh r4, 0",
            "lcll r4, 5",       # R4 = tamanho
            "# Loop (endereço 30)",
            "sub r5, r4, r3",   # R5 = tamanho - índice
            "dec r5, r5",       # R5-- (índice invertido)
            "add r6, r10, r5",  # R6 = origem + índice_invertido
            "load r7, r6",      # R7 = valor
            "add r8, r20, r3",  # R8 = destino + índice
            "store r8, r7",     # MEM[destino] = valor
            "inc r3, r3",       # índice++
            "sub r9, r4, r3",
            "bne r9, r0, 30",   # Continua se não terminou
            "halt"
        ],
        expected_results={
            "memory": {
                200: 1, 201: 2, 202: 3, 203: 4, 204: 5,
                300: 5, 301: 4, 302: 3, 303: 2, 304: 1
            }
        },
        description="Copia array invertendo a ordem"
    )
    framework.run_test("programa_memoria_complexa", bin_path, {
        "memory": {200: 1, 201: 2, 202: 3, 203: 4, 204: 5,
                  300: 5, 301: 4, 302: 3, 303: 2, 304: 1}
    })
    
    # ========================================================================
    # TESTE MASSIVO 10: Todas as Instruções Extras
    # ========================================================================
    
    bin_path = framework.create_test_program(
        name="programa_instrucoes_extras",
        assembly_code=[
            "# Testa todas as 8 instruções extras em sequência",
            "movi r1, 100",     # MOVI: R1 = 100
            "movi r2, 10",      # R2 = 10
            "mul r3, r1, r2",   # MUL: R3 = 100 * 10 = 1000
            "div r4, r3, r2",   # DIV: R4 = 1000 / 10 = 100
            "mod r5, r1, r2",   # MOD: R5 = 100 % 10 = 0
            "inc r6, r1",       # INC: R6 = 100 + 1 = 101
            "dec r7, r1",       # DEC: R7 = 100 - 1 = 99
            "movi r8, 15",      # R8 = 15
            "movi r9, 15",      # R9 = 15
            "notbit r10, r8, r9", # NOTBIT: R10 = ~(15 & 15)
            "nop",              # NOP: não faz nada
            "nop",
            "halt"
        ],
        expected_results={
            "registers": {
                1: 100, 2: 10, 3: 1000, 4: 100, 5: 0,
                6: 101, 7: 99, 8: 15, 9: 15, 10: ~15 & 0xFFFFFFFF
            }
        },
        description="Testa todas as 8 instruções extras"
    )
    framework.run_test("programa_instrucoes_extras", bin_path, {
        "registers": {1: 100, 2: 10, 3: 1000, 4: 100, 5: 0, 6: 101, 7: 99, 8: 15, 9: 15}
    })
    
    # ========================================================================
    # GERA RELATÓRIO FINAL
    # ========================================================================
    
    framework.generate_report("../testes/massivos/relatorio_testes_massivos.txt")
    
    print("\n" + "="*80)
    print("TESTES MASSIVOS CONCLUÍDOS")
    print("="*80)


if __name__ == "__main__":
    run_all_massive_tests()
