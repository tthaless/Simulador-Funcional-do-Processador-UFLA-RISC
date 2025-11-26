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
        # 1. ESTÁGIO IF (Instruction Fetch) - Busca
        # Busca a instrução na memória usando o PC atual
        current_pc = self.state.pc
        instrucao = self.fetch_instruction() 
        
        # Incrementa o PC para a próxima instrução
        self.incr_pc()