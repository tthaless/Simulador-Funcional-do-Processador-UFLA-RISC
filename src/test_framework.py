"""
Framework de Testes para o Simulador UFLA-RISC
 - Sistema automatizado para testar instruções isoladas e programas completos
"""

import os
import sys
from typing import Dict, List, Tuple, Optional
from cpu_logged import CPULogged
from interpretador import montar_instrucao

class TestFramework:
    """
    Framework para criar e executar testes do simulador.
    Suporta testes isolados (por instrução) e testes massivos (programas completos).
    """
    
    def __init__(self, output_dir: str = "../testes"):
        self.output_dir = output_dir
        self.test_results = []
        
    def create_test_program(self, name: str, assembly_code: List[str], 
                           expected_results: Dict, description: str = "") -> str:
        """
        Cria um programa de teste em assembly e retorna o caminho do arquivo binário.
        
        Args:
            name: Nome do teste
            assembly_code: Lista de linhas de código assembly
            expected_results: Dicionário com resultados esperados (registradores, flags, memória)
            description: Descrição do teste
            
        Returns:
            Caminho do arquivo binário gerado
        """
        # Cria arquivo assembly
        asm_path = os.path.join(self.output_dir, f"{name}.asm")
        bin_path = os.path.join(self.output_dir, f"{name}.bin")
        
        with open(asm_path, 'w', encoding='utf-8') as f:
            f.write(f"# Teste: {name}\n")
            f.write(f"# Descrição: {description}\n")
            f.write("address 0\n")
            for line in assembly_code:
                f.write(line + "\n")
        
        # Converte para binário
        with open(asm_path, 'r', encoding='utf-8') as fin, \
             open(bin_path, 'w', encoding='utf-8') as fout:
            for linha in fin:
                b = montar_instrucao(linha)
                if b:
                    fout.write(b + "\n")
        
        return bin_path
    
    def run_test(self, name: str, bin_path: str, expected_results: Dict, 
                 save_log: bool = True) -> Dict:
        """
        Executa um teste e verifica os resultados.
        
        Args:
            name: Nome do teste
            bin_path: Caminho do arquivo binário
            expected_results: Resultados esperados
            save_log: Se True, salva o log de execução
            
        Returns:
            Dicionário com resultado do teste (passed, errors, details)
        """
        print(f"\n{'='*80}")
        print(f"Executando Teste: {name}")
        print(f"{'='*80}")
        
        # Cria CPU e executa
        cpu = CPULogged(enable_logging=True, verbose=False)
        
        try:
            cpu.load_from_file(bin_path, verbose=False)
            cpu.run()
            
            # Salva log se solicitado
            if save_log:
                log_path = os.path.join(self.output_dir, f"{name}_log.txt")
                cpu.save_execution_log(log_path)
            
            # Verifica resultados
            errors = []
            
            # Verifica registradores
            if "registers" in expected_results:
                for reg_idx, expected_val in expected_results["registers"].items():
                    actual_val = cpu.read_reg(reg_idx)
                    if actual_val != expected_val:
                        errors.append(
                            f"R{reg_idx}: esperado {expected_val}, obtido {actual_val}"
                        )
            
            # Verifica flags
            if "flags" in expected_results:
                for flag_name, expected_val in expected_results["flags"].items():
                    actual_val = getattr(cpu.state.flags, flag_name)
                    if actual_val != expected_val:
                        errors.append(
                            f"Flag {flag_name}: esperado {expected_val}, obtido {actual_val}"
                        )
            
            # Verifica memória
            if "memory" in expected_results:
                for addr, expected_val in expected_results["memory"].items():
                    actual_val = cpu.read_mem(addr)
                    if actual_val != expected_val:
                        errors.append(
                            f"MEM[{addr}]: esperado {expected_val}, obtido {actual_val}"
                        )
            
            # Verifica PC final
            if "pc" in expected_results:
                if cpu.state.pc != expected_results["pc"]:
                    errors.append(
                        f"PC final: esperado {expected_results['pc']}, obtido {cpu.state.pc}"
                    )
            
            # Resultado do teste
            passed = len(errors) == 0
            
            result = {
                "name": name,
                "passed": passed,
                "errors": errors,
                "cycles": cpu.logger.cycle_count if cpu.logger else 0,
                "final_state": {
                    "pc": cpu.state.pc,
                    "flags": cpu.state.flags.as_dict(),
                    "registers": {i: cpu.read_reg(i) for i in range(32) if cpu.read_reg(i) != 0}
                }
            }
            
            # Imprime resultado
            if passed:
                print(f" TESTE PASSOU - {name}")
            else:
                print(f" TESTE FALHOU - {name}")
                for error in errors:
                    print(f"   - {error}")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f" ERRO DURANTE EXECUÇÃO: {e}")
            result = {
                "name": name,
                "passed": False,
                "errors": [f"Exceção: {str(e)}"],
                "cycles": 0,
                "final_state": None
            }
            self.test_results.append(result)
            return result
    
    def generate_report(self, filepath: str):
        """Gera relatório completo dos testes."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RELATÓRIO DE TESTES - SIMULADOR UFLA-RISC\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Total de Testes: {total}\n")
            f.write(f"Testes Aprovados: {passed}\n")
            f.write(f"Testes Falhados: {failed}\n")
            f.write(f"Taxa de Sucesso: {(passed/total*100) if total > 0 else 0:.2f}%\n\n")
            
            f.write("="*80 + "\n")
            f.write("DETALHES DOS TESTES\n")
            f.write("="*80 + "\n\n")
            
            for result in self.test_results:
                f.write(f"\nTeste: {result['name']}\n")
                f.write(f"Status: {' PASSOU' if result['passed'] else ' FALHOU'}\n")
                f.write(f"Ciclos Executados: {result['cycles']}\n")
                
                if not result['passed']:
                    f.write("Erros:\n")
                    for error in result['errors']:
                        f.write(f"  - {error}\n")
                
                if result['final_state']:
                    f.write(f"Estado Final:\n")
                    f.write(f"  PC: {result['final_state']['pc']}\n")
                    f.write(f"  Flags: {result['final_state']['flags']}\n")
                    if result['final_state']['registers']:
                        f.write(f"  Registradores não-zero: {result['final_state']['registers']}\n")
                
                f.write("-"*80 + "\n")
        
        print(f"\n Relatório de testes salvo em: {filepath}")
        print(f"Total: {total} | Passou: {passed} | Falhou: {failed}")


# -----------------------------------------------------------------------------
# Teste do Framework
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Framework de testes criado com sucesso!")
    print("Use este módulo para criar e executar testes automatizados.")
