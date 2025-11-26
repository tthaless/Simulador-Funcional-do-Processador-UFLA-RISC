from loader import MemoryLoader, MEMORY_SIZE, WORD_MASK

class CPU(MemoryLoader):
    """
    Implementação da CPU - Responsável pelo ciclo de busca, decodificação e gerenciamento da execução
    (Herda de MemoryLoader para ter acesso direto a memória e registradores)
    """

    def __init__(self):
        # Inicializa a memória e estados (feito pelo MemoryLoader)
        super().__init__()
        
        # Mapeamento pra debug
        self.OPCODE_NAMES = {
            1: "ADD", 2: "SUB", 3: "ZEROS", 4: "XOR", 5: "OR", 6: "NOT",
            7: "AND", 8: "ASL", 9: "ASR", 10: "LSL", 11: "LSR", 12: "COPY",
            14: "LCLH", 15: "LCLL", 16: "LOAD", 17: "STORE",
            18: "JAL", 19: "JR", 20: "BEQ", 21: "BNE", 22: "J",
            32: "MUL", 33: "DIV", 34: "MOD", 35: "INC", 
            36: "DEC", 37: "MOVI", 38: "NOTBIT", 39: "NOP",
            255: "HALT" 
        }

    def run(self): # Loop principal do processador. Executa instruções até encontrar a parada (HALT)
    
        print(f"--- Iniciando Execução (PC Inicial: {self.state.pc}) ---")
        
        cycle_count = 0
       
        # O loop roda enquanto halted for FALSE
        while not self.state.halted:
            self.step()
            cycle_count += 1
            
            # Limite para impedir loop infinito
            if cycle_count > 5000:
                print("AVISO: Limite de ciclos de segurança atingido (Loop infinito?)")
                break
        
        print(f"--- Execução Finalizada em {cycle_count} ciclos ---")

    
    def step(self): #Ciclo completo de instrução ( IF,ID,EX,WB)
        
        # 1. ESTÁGIO IF (Instruction Fetch) - Busca
        current_pc = self.state.pc
        instrucao = self.fetch_instruction() 
        self.incr_pc() 

        # 2. ESTÁGIO ID (Instruction Decode) - Decodificação

        # Tratamento antecipado do HALT (evita ler reg 255 inválido)
        if instrucao == 0xFFFFFFFF:
            self.state.halted = True
            print(f"PC({current_pc}): HALT encontrado.")
            return

        # Extração dos campos
        opcode = self.extract_field(instrucao, 24, 31)
        ra_idx = self.extract_field(instrucao, 16, 23)
        rb_idx = self.extract_field(instrucao, 8, 15)
        rc_idx = self.extract_field(instrucao, 0, 7)
        
        const16 = self.extract_field(instrucao, 8, 23)
        addr24  = self.extract_field(instrucao, 0, 23)

        # Leitura dos registradores (Busca de operandos)
        val_ra = self.read_reg(ra_idx)
        val_rb = self.read_reg(rb_idx)
        


        # 3. ESTÁGIO EX/MEM (Execução) e 4. WB (Write Back)
        
        # Debug 
        #nome_instrucao = self.OPCODE_NAMES.get(opcode, "DESCONHECIDO")
        #print(f"[DEBUG P3] Ciclo em PC={current_pc}: Inst={nome_instrucao}")

        self.execute_instruction(opcode, ra_idx, rb_idx, rc_idx, 
                                 val_ra, val_rb, const16, addr24, current_pc)
        
    def _update_flags_alu(self, result, overflow=False, carry=False):
        self.state.flags.zero = 1 if (result & WORD_MASK) == 0 else 0
        self.state.flags.neg = 1 if (result & (1 << 31)) else 0
        self.state.flags.overflow = 1 if overflow else 0
        self.state.flags.carry = 1 if carry else 0

    def execute_instruction(self, opcode, ra, rb, rc, val_ra, val_rb, const16, addr24, current_pc):

        # debug pra if e id
        #nome_instrucao = self.OPCODE_NAMES.get(opcode, "DESCONHECIDO")
        #print(f"[DEBUG P3] Ciclo em PC={current_pc}:")
       #print(f"   -> Instrução: {nome_instrucao} (Opcode {opcode})")
        #print(f"   -> Registradores decodificados: Ra=R{ra}, Rb=R{rb}, Rc=R{rc}")
        #print(f"   -> Valores lidos: Val_Ra={val_ra}, Val_Rb={val_rb}")
        #print("-" * 40)
        # ------------------------------------
        
        # Converter valores para inteiros com sinal (Necessário para contas matemáticas)
        signed_ra = self.uint32_to_signed(val_ra)
        signed_rb = self.uint32_to_signed(val_rb)

        # --- Instruções ALU
        if opcode == 1: # ADD
            res_signed = signed_ra + signed_rb
            # Overflow: Soma de dois positivos dá negativo ou dois negativos dá positivo
            overflow = (signed_ra > 0 and signed_rb > 0 and res_signed < 0) or \
                       (signed_ra < 0 and signed_rb < 0 and res_signed > 0)
            # Carry (unsigned overflow)
            carry = (val_ra + val_rb) > 0xFFFFFFFF
            
            self.write_reg(rc, res_signed)
            self._update_flags_alu(res_signed, overflow, carry)
            
        elif opcode == 2: # SUB
            res_signed = signed_ra - signed_rb
            # Overflow na subtração
            overflow = (signed_ra > 0 and signed_rb < 0 and res_signed < 0) or \
                       (signed_ra < 0 and signed_rb > 0 and res_signed > 0)
            carry = val_ra < val_rb
            
            self.write_reg(rc, res_signed)
            self._update_flags_alu(res_signed, overflow, carry)

        elif opcode == 3: # ZEROS
            self.write_reg(rc, 0)
            self._update_flags_alu(0)

        elif opcode == 4: # XOR
            res = val_ra ^ val_rb
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 5: # OR
            res = val_ra | val_rb
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 6: # NOT
            res = ~val_ra
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 7: # AND
            res = val_ra & val_rb
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 8: # ASL
            res = val_ra << (val_rb & 0x1F)
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 9: # ASR
            res = signed_ra >> (val_rb & 0x1F)
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 10: # LSL
            res = val_ra << (val_rb & 0x1F)
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 11: # LSR
            res = val_ra >> (val_rb & 0x1F)
            self.write_reg(rc, res)
            self._update_flags_alu(res)

        elif opcode == 12: # COPY
            self.write_reg(rc, val_ra)
            self._update_flags_alu(val_ra)
            
        elif opcode == 16: # LOAD
            pass
            
        elif opcode == 17: # STORE
            pass
            
        elif opcode == 22: # JUMP
            pass

        else:
            # Se não é HALT e não conhecemos o opcode, é uma instrução desconhecida (ou NOP)
            pass

# -----------------------------------------------------------------------------
# Bloco de Teste Rápido (Só roda se executar este arquivo diretamente)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    
    # Arquivo binário de entrada ( instruções)
    bin_file = "programa.bin"
    
    if os.path.exists(bin_file):
        print("Arquivo programa.bin encontrado. Iniciando teste da CPU...")
        
        cpu = CPU()
        cpu.load_from_file(bin_file, verbose=True) # carrega a memória
        
        # Executa a simulação
        cpu.run()
        
        # Mostra estado final
        print("\nEstado Final dos Registradores:")
        for r in cpu.dump_registers():
            if r[1] != 0: # Só mostra quem não é zero
                print(f"R{r[0]}: {r[1]} (Int: {r[2]})")
                
    else:
        print(f"ERRO: {bin_file} não encontrado")