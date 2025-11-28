"""
CPU com Sistema de Logging Integrado
 - Versão da CPU que registra todas as mudanças de estado
"""

from cpu import CPU
from logger import StateLogger

class CPULogged(CPU):
    """
    Extensão da CPU que integra o sistema de logging.
    Registra automaticamente todas as mudanças de estado a cada ciclo.
    """
    
    def __init__(self, enable_logging: bool = True, verbose: bool = False):
        """
        Inicializa a CPU com logging.
        
        Args:
            enable_logging: Se True, ativa o logging de mudanças de estado
            verbose: Se True, imprime logs no console durante a execução
        """
        super().__init__()
        self.enable_logging = enable_logging
        self.verbose = verbose
        
        if self.enable_logging:
            self.logger = StateLogger(self)
        else:
            self.logger = None
    
    def run(self):
        """Loop principal com logging integrado."""
        if self.enable_logging:
            self.logger.capture_initial_state()
        
        print(f"--- Iniciando Execução com Logging (PC Inicial: {self.state.pc}) ---")
        
        cycle_count = 0
        
        while not self.state.halted:
            self.step()
            cycle_count += 1
            
            # Registra o log após cada ciclo completo
            if self.enable_logging:
                log_data = self.logger.log_cycle("COMPLETE")
                if self.verbose:
                    self.logger.print_cycle_log(log_data)
            
            # Limite de segurança
            if cycle_count > 5000:
                print("AVISO: Limite de ciclos de segurança atingido (Loop infinito?)")
                break
        
        print(f"--- Execução Finalizada em {cycle_count} ciclos ---")
        
        # Exibe resumo
        if self.enable_logging:
            summary = self.logger.get_summary()
            print(f"\nResumo da Execução:")
            print(f"  Total de Ciclos: {summary['total_cycles']}")
            print(f"  PC Final: {summary['final_pc']}")
            print(f"  Flags Finais: {summary['final_flags']}")
    
    def save_execution_log(self, filepath: str):
        """Salva o log completo da execução em um arquivo."""
        if self.enable_logging and self.logger:
            self.logger.save_logs_to_file(filepath)
            print(f"Log de execução salvo em: {filepath}")
        else:
            print("Logging não está habilitado.")


# -----------------------------------------------------------------------------
# Teste da CPU com Logging
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    
    bin_file = "programa.bin"
    
    if os.path.exists(bin_file):
        print("Testando CPU com Logging...")
        
        cpu = CPULogged(enable_logging=True, verbose=True)
        cpu.load_from_file(bin_file, verbose=False)
        
        # Executa com logging
        cpu.run()
        
        # Salva logs
        cpu.save_execution_log("execution_log.txt")
        
        # Mostra estado final dos registradores
        print("\n--- Estado Final dos Registradores ---")
        for r in cpu.dump_registers():
            if r[1] != 0:
                print(f"R{r[0]}: {r[1]} (signed: {r[2]})")
    else:
        print(f"ERRO: {bin_file} não encontrado")
