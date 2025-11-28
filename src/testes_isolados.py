"""
Testes Isolados - 
Testa cada instrução individualmente para verificar corretude
"""

import sys
import os
from test_framework import TestFramework

def run_all_isolated_tests():
    """Executa todos os testes isolados de instruções."""
    
    framework = TestFramework(output_dir="../testes/isolados")
    
    print("\n" + "="*80)
    print("EXECUTANDO TESTES ISOLADOS - TODAS AS INSTRUÇÕES")
    print("="*80)
    
    # ========================================================================
    # TESTES DE INSTRUÇÕES ARITMÉTICAS (ALU)
    # ========================================================================
    
    # Teste 1: ADD (Adição)
    bin_path = framework.create_test_program(
        name="test_add",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 10",      # R1 = 10
            "lclh r2, 0",
            "lcll r2, 20",      # R2 = 20
            "add r3, r1, r2",   # R3 = R1 + R2 = 30
            "halt"
        ],
        expected_results={
            "registers": {1: 10, 2: 20, 3: 30},
            "flags": {"zero": 0, "neg": 0}
        },
        description="Testa adição de dois números positivos"
    )
    framework.run_test("test_add", bin_path, {"registers": {1: 10, 2: 20, 3: 30}})
    
    # Teste 2: SUB (Subtração)
    bin_path = framework.create_test_program(
        name="test_sub",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 50",      # R1 = 50
            "lclh r2, 0",
            "lcll r2, 30",      # R2 = 30
            "sub r3, r1, r2",   # R3 = R1 - R2 = 20
            "halt"
        ],
        expected_results={
            "registers": {1: 50, 2: 30, 3: 20},
            "flags": {"zero": 0, "neg": 0}
        },
        description="Testa subtração resultando em número positivo"
    )
    framework.run_test("test_sub", bin_path, {"registers": {1: 50, 2: 30, 3: 20}})
    
    # Teste 3: ZEROS
    bin_path = framework.create_test_program(
        name="test_zeros",
        assembly_code=[
            "lclh r5, 0",
            "lcll r5, 999",     # R5 = 999
            "zero r5",          # R5 = 0
            "halt"
        ],
        expected_results={
            "registers": {5: 0},
            "flags": {"zero": 1}
        },
        description="Testa instrução ZEROS"
    )
    framework.run_test("test_zeros", bin_path, {"registers": {5: 0}, "flags": {"zero": 1}})
    
    # Teste 4: XOR
    bin_path = framework.create_test_program(
        name="test_xor",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 15",      # R1 = 15 (0b1111)
            "lclh r2, 0",
            "lcll r2, 7",       # R2 = 7  (0b0111)
            "xor r3, r1, r2",   # R3 = 15 XOR 7 = 8 (0b1000)
            "halt"
        ],
        expected_results={
            "registers": {1: 15, 2: 7, 3: 8}
        },
        description="Testa operação XOR lógica"
    )
    framework.run_test("test_xor", bin_path, {"registers": {1: 15, 2: 7, 3: 8}})
    
    # Teste 5: OR
    bin_path = framework.create_test_program(
        name="test_or",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 12",      # R1 = 12 (0b1100)
            "lclh r2, 0",
            "lcll r2, 10",      # R2 = 10 (0b1010)
            "or r3, r1, r2",    # R3 = 12 OR 10 = 14 (0b1110)
            "halt"
        ],
        expected_results={
            "registers": {1: 12, 2: 10, 3: 14}
        },
        description="Testa operação OR lógica"
    )
    framework.run_test("test_or", bin_path, {"registers": {1: 12, 2: 10, 3: 14}})
    
    # Teste 6: AND
    bin_path = framework.create_test_program(
        name="test_and",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 12",      # R1 = 12 (0b1100)
            "lclh r2, 0",
            "lcll r2, 10",      # R2 = 10 (0b1010)
            "and r3, r1, r2",   # R3 = 12 AND 10 = 8 (0b1000)
            "halt"
        ],
        expected_results={
            "registers": {1: 12, 2: 10, 3: 8}
        },
        description="Testa operação AND lógica"
    )
    framework.run_test("test_and", bin_path, {"registers": {1: 12, 2: 10, 3: 8}})
    
    # Teste 7: NOT
    bin_path = framework.create_test_program(
        name="test_not",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 0",       # R1 = 0
            "passnota r2, r1",  # R2 = NOT(0) = 0xFFFFFFFF
            "halt"
        ],
        expected_results={
            "registers": {1: 0, 2: 0xFFFFFFFF}
        },
        description="Testa operação NOT"
    )
    framework.run_test("test_not", bin_path, {"registers": {1: 0, 2: 0xFFFFFFFF}})
    
    # Teste 8: ASL (Arithmetic Shift Left)
    bin_path = framework.create_test_program(
        name="test_asl",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 5",       # R1 = 5
            "lclh r2, 0",
            "lcll r2, 2",       # R2 = 2 (shift de 2 bits)
            "asl r3, r1, r2",   # R3 = 5 << 2 = 20
            "halt"
        ],
        expected_results={
            "registers": {1: 5, 2: 2, 3: 20}
        },
        description="Testa shift aritmético à esquerda"
    )
    framework.run_test("test_asl", bin_path, {"registers": {1: 5, 2: 2, 3: 20}})
    
    # Teste 9: LSR (Logical Shift Right)
    bin_path = framework.create_test_program(
        name="test_lsr",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 20",      # R1 = 20
            "lclh r2, 0",
            "lcll r2, 2",       # R2 = 2 (shift de 2 bits)
            "lsr r3, r1, r2",   # R3 = 20 >> 2 = 5
            "halt"
        ],
        expected_results={
            "registers": {1: 20, 2: 2, 3: 5}
        },
        description="Testa shift lógico à direita"
    )
    framework.run_test("test_lsr", bin_path, {"registers": {1: 20, 2: 2, 3: 5}})
    
    # Teste 10: COPY (PASSA)
    bin_path = framework.create_test_program(
        name="test_copy",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 42",      # R1 = 42
            "passa r2, r1",     # R2 = R1 = 42
            "halt"
        ],
        expected_results={
            "registers": {1: 42, 2: 42}
        },
        description="Testa cópia de registrador"
    )
    framework.run_test("test_copy", bin_path, {"registers": {1: 42, 2: 42}})
    
    # ========================================================================
    # TESTES DE CONSTANTES E MEMÓRIA
    # ========================================================================
    
    # Teste 11: LCLH (Load Constant High)
    bin_path = framework.create_test_program(
        name="test_lclh",
        assembly_code=[
            "lclh r1, 255",     # R1[31:16] = 255
            "halt"
        ],
        expected_results={
            "registers": {1: 255 << 16}  # 16711680
        },
        description="Testa carregamento de constante nos 16 bits superiores"
    )
    framework.run_test("test_lclh", bin_path, {"registers": {1: 255 << 16}})
    
    # Teste 12: LCLL (Load Constant Low)
    bin_path = framework.create_test_program(
        name="test_lcll",
        assembly_code=[
            "lcll r1, 255",     # R1[15:0] = 255
            "halt"
        ],
        expected_results={
            "registers": {1: 255}
        },
        description="Testa carregamento de constante nos 16 bits inferiores"
    )
    framework.run_test("test_lcll", bin_path, {"registers": {1: 255}})
    
    # Teste 13: LOAD e STORE
    bin_path = framework.create_test_program(
        name="test_load_store",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 100",     # R1 = 100 (endereço)
            "lclh r2, 0",
            "lcll r2, 999",     # R2 = 999 (valor a armazenar)
            "passa r3, r1",     # R3 = 100 (endereço para STORE)
            "store r3, r2",     # MEM[100] = 999
            "load r4, r1",      # R4 = MEM[100] = 999
            "halt"
        ],
        expected_results={
            "registers": {1: 100, 2: 999, 3: 100, 4: 999},
            "memory": {100: 999}
        },
        description="Testa operações de LOAD e STORE"
    )
    framework.run_test("test_load_store", bin_path, 
                      {"registers": {1: 100, 2: 999, 3: 100, 4: 999}, "memory": {100: 999}})
    
    # ========================================================================
    # TESTES DE CONTROLE DE FLUXO
    # ========================================================================
    
    # Teste 14: J (Jump Incondicional)
    bin_path = framework.create_test_program(
        name="test_jump",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 10",      # R1 = 10
            "j 5",              # Pula para endereço 5
            "lclh r2, 0",       # Esta instrução será pulada
            "lcll r2, 99",      # Esta instrução será pulada
            "halt"              # Endereço 5: HALT
        ],
        expected_results={
            "registers": {1: 10, 2: 0}  # R2 não deve ser modificado
        },
        description="Testa jump incondicional"
    )
    framework.run_test("test_jump", bin_path, {"registers": {1: 10, 2: 0}})
    
    # Teste 15: BEQ (Branch if Equal)
    bin_path = framework.create_test_program(
        name="test_beq",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 5",       # R1 = 5
            "lclh r2, 0",
            "lcll r2, 5",       # R2 = 5
            "beq r1, r2, 8",    # Se R1 == R2, pula para endereço 8
            "lclh r3, 0",       # Esta instrução será pulada
            "lcll r3, 99",      # Esta instrução será pulada
            "halt"              # Endereço 8: HALT
        ],
        expected_results={
            "registers": {1: 5, 2: 5, 3: 0}
        },
        description="Testa branch condicional (igual)"
    )
    framework.run_test("test_beq", bin_path, {"registers": {1: 5, 2: 5, 3: 0}})
    
    # Teste 16: BNE (Branch if Not Equal)
    bin_path = framework.create_test_program(
        name="test_bne",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 5",       # R1 = 5
            "lclh r2, 0",
            "lcll r2, 10",      # R2 = 10
            "bne r1, r2, 8",    # Se R1 != R2, pula para endereço 8
            "lclh r3, 0",       # Esta instrução será pulada
            "lcll r3, 99",      # Esta instrução será pulada
            "halt"              # Endereço 8: HALT
        ],
        expected_results={
            "registers": {1: 5, 2: 10, 3: 0}
        },
        description="Testa branch condicional (diferente)"
    )
    framework.run_test("test_bne", bin_path, {"registers": {1: 5, 2: 10, 3: 0}})
    
    # Teste 17: JAL (Jump and Link)
    bin_path = framework.create_test_program(
        name="test_jal",
        assembly_code=[
            "jal 5",            # Pula para 5, salva PC+1 em R31
            "lclh r1, 0",       # Endereço 1
            "lcll r1, 99",      # Endereço 2
            "halt",             # Endereço 3
            "nop",              # Endereço 4
            "halt"              # Endereço 5: destino do JAL
        ],
        expected_results={
            "registers": {1: 0, 31: 1}  # R31 deve ter PC+1 = 1
        },
        description="Testa jump and link (salva endereço de retorno)"
    )
    framework.run_test("test_jal", bin_path, {"registers": {1: 0, 31: 1}})
    
    # Teste 18: JR (Jump Register)
    bin_path = framework.create_test_program(
        name="test_jr",
        assembly_code=[
            "lclh r5, 0",
            "lcll r5, 4",       # R5 = 4 (endereço de destino)
            "jr r5",            # Pula para endereço em R5
            "lclh r1, 0",       # Esta instrução será pulada
            "halt"              # Endereço 4: HALT
        ],
        expected_results={
            "registers": {5: 4, 1: 0}
        },
        description="Testa jump via registrador"
    )
    framework.run_test("test_jr", bin_path, {"registers": {5: 4, 1: 0}})
    
    # ========================================================================
    # TESTES DE INSTRUÇÕES EXTRAS (8 NOVAS)
    # ========================================================================
    
    # Teste 19: MUL (Multiplicação)
    bin_path = framework.create_test_program(
        name="test_mul",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 6",       # R1 = 6
            "lclh r2, 0",
            "lcll r2, 7",       # R2 = 7
            "mul r3, r1, r2",   # R3 = 6 * 7 = 42
            "halt"
        ],
        expected_results={
            "registers": {1: 6, 2: 7, 3: 42}
        },
        description="Testa multiplicação"
    )
    framework.run_test("test_mul", bin_path, {"registers": {1: 6, 2: 7, 3: 42}})
    
    # Teste 20: DIV (Divisão)
    bin_path = framework.create_test_program(
        name="test_div",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 20",      # R1 = 20
            "lclh r2, 0",
            "lcll r2, 4",       # R2 = 4
            "div r3, r1, r2",   # R3 = 20 / 4 = 5
            "halt"
        ],
        expected_results={
            "registers": {1: 20, 2: 4, 3: 5}
        },
        description="Testa divisão"
    )
    framework.run_test("test_div", bin_path, {"registers": {1: 20, 2: 4, 3: 5}})
    
    # Teste 21: MOD (Resto da Divisão)
    bin_path = framework.create_test_program(
        name="test_mod",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 17",      # R1 = 17
            "lclh r2, 0",
            "lcll r2, 5",       # R2 = 5
            "mod r3, r1, r2",   # R3 = 17 % 5 = 2
            "halt"
        ],
        expected_results={
            "registers": {1: 17, 2: 5, 3: 2}
        },
        description="Testa resto da divisão (módulo)"
    )
    framework.run_test("test_mod", bin_path, {"registers": {1: 17, 2: 5, 3: 2}})
    
    # Teste 22: INC (Incremento)
    bin_path = framework.create_test_program(
        name="test_inc",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 10",      # R1 = 10
            "inc r2, r1",       # R2 = R1 + 1 = 11
            "halt"
        ],
        expected_results={
            "registers": {1: 10, 2: 11}
        },
        description="Testa incremento (+1)"
    )
    framework.run_test("test_inc", bin_path, {"registers": {1: 10, 2: 11}})
    
    # Teste 23: DEC (Decremento)
    bin_path = framework.create_test_program(
        name="test_dec",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 10",      # R1 = 10
            "dec r2, r1",       # R2 = R1 - 1 = 9
            "halt"
        ],
        expected_results={
            "registers": {1: 10, 2: 9}
        },
        description="Testa decremento (-1)"
    )
    framework.run_test("test_dec", bin_path, {"registers": {1: 10, 2: 9}})
    
    # Teste 24: MOVI (Move Immediate)
    bin_path = framework.create_test_program(
        name="test_movi",
        assembly_code=[
            "movi r1, 1234",    # R1 = 1234 (carrega constante diretamente)
            "halt"
        ],
        expected_results={
            "registers": {1: 1234}
        },
        description="Testa carregamento imediato de constante"
    )
    framework.run_test("test_movi", bin_path, {"registers": {1: 1234}})
    
    # Teste 25: NOTBIT (Not Bit-a-Bit com 3 operandos)
    bin_path = framework.create_test_program(
        name="test_notbit",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 15",      # R1 = 15 (0b1111)
            "lclh r2, 0",
            "lcll r2, 15",      # R2 = 15 (0b1111)
            "notbit r3, r1, r2", # R3 = ~(R1 & R2) = ~15
            "halt"
        ],
        expected_results={
            "registers": {1: 15, 2: 15, 3: ~15 & 0xFFFFFFFF}
        },
        description="Testa NOT bit-a-bit com 3 operandos"
    )
    framework.run_test("test_notbit", bin_path, {"registers": {1: 15, 2: 15, 3: ~15 & 0xFFFFFFFF}})
    
    # Teste 26: NOP (No Operation)
    bin_path = framework.create_test_program(
        name="test_nop",
        assembly_code=[
            "lclh r1, 0",
            "lcll r1, 5",       # R1 = 5
            "nop",              # Não faz nada
            "nop",              # Não faz nada
            "lclh r2, 0",
            "lcll r2, 10",      # R2 = 10
            "halt"
        ],
        expected_results={
            "registers": {1: 5, 2: 10}
        },
        description="Testa instrução NOP (não faz nada)"
    )
    framework.run_test("test_nop", bin_path, {"registers": {1: 5, 2: 10}})
    
    # ========================================================================
    # GERA RELATÓRIO FINAL
    # ========================================================================
    
    framework.generate_report("../testes/isolados/relatorio_testes_isolados.txt")
    
    print("\n" + "="*80)
    print("TESTES ISOLADOS CONCLUÍDOS")
    print("="*80)


if __name__ == "__main__":
    run_all_isolated_tests()
