from loader import MemoryLoader, MEMORY_SIZE, WORD_MASK

class CPU(MemoryLoader):
    """
    Implementação da CPU - Responsável pelo ciclo de busca, decodificação e gerenciamento da execução
    (Herda de MemoryLoader para ter acesso direto a memória e registradores)
    """

    def __init__(self):
        super().__init__()
        # Mapeamento para debug 
        self.OPCODE_NAMES = {
            1: "ADD", 2: "SUB", 3: "ZEROS", 4: "XOR", 5: "OR", 6: "NOT",
            7: "AND", 8: "ASL", 9: "ASR", 10: "LSL", 11: "LSR", 12: "COPY",
            14: "LCLH", 15: "LCLL", 16: "LOAD", 17: "STORE",
            18: "JAL", 19: "JR", 20: "BEQ", 21: "BNE", 22: "J",
            255: "HALT" 
        }

    def run(self): 
        print(f"--- Iniciando Execução (PC Inicial: {self.state.pc}) ---")
        
        cycle_count = 0
        # Loop principal
        while not self.state.halted:
            self.step()
            cycle_count += 1
            
            
            if cycle_count > 1000:
                print("AVISO: Limite de ciclos atingido (Loop infinito?)")
                break
        
        print(f"--- Execução Finalizada em {cycle_count} ciclos ---")

   def step(self):
        # 1. ESTÁGIO IF (Instruction Fetch)
        current_pc = self.state.pc
        instrucao = self.fetch_instruction() 
        self.incr_pc() 

        # 2. ESTÁGIO ID (Instruction Decode)
        
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

        # 3. ESTÁGIO EX/MEM e WB
        self.execute_instruction(opcode, ra_idx, rb_idx, rc_idx, 
                                 val_ra, val_rb, const16, addr24, current_pc)

    def execute_instruction(self, opcode, ra, rb, rc, val_ra, val_rb, const16, addr24, current_pc):
        # --- Instruções ALU (Esqueleto para a Pessoa 4) ---
        if opcode == 1: # ADD
            pass
        elif opcode == 2: # SUB
            pass
        elif opcode == 16: # LOAD
            pass
        elif opcode == 17: # STORE
            pass
        elif opcode == 22: # JUMP
            pass
        else:
            pass

# -----------------------------------------------------------------------------
# Bloco de Teste Rápido
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    bin_file = "programa.bin"
    
    if os.path.exists(bin_file):
        print("Arquivo programa.bin encontrado. Iniciando teste da CPU...")
        cpu = CPU()
        cpu.load_from_file(bin_file, verbose=True)
        cpu.run()
        
        print("\nEstado Final dos Registradores:")
        for r in cpu.dump_registers():
            if r[1] != 0:
                print(f"R{r[0]}: {r[1]} (Int: {r[2]})")
    else:
        print(f"ERRO: {bin_file} não encontrado")