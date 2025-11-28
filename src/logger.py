"""
Módulo de Logging para o Simulador UFLA-RISC
Cria logs detalhados de cada ciclo de execução
Mostra as diferenças de estado (registradores, memória, PC, IR, flags) após cada instrução
"""

from typing import Dict, List, Tuple, Optional
from loader import MemoryLoader, Flags
import copy

class StateLogger:
    """
    Classe responsável por rastrear e registrar mudanças de estado durante a execução.
    Compara o estado anterior com o estado atual e gera logs detalhados.
    """
    
    def __init__(self, cpu_ref):
        """
        Inicializa o logger com referência à CPU.
        
        Args:
            cpu_ref: Referência ao objeto CPU para acessar o estado
        """
        self.cpu = cpu_ref
        self.cycle_count = 0
        self.logs = []  # Lista de logs de cada ciclo
        
        # Estado anterior (para comparação)
        self.prev_state = {
            "pc": 0,
            "ir": 0,
            "regs": [0] * 32,
            "flags": {"neg": 0, "zero": 0, "carry": 0, "overflow": 0},
            "memory": {}  # Apenas posições modificadas
        }
        
        # Mapeamento de opcodes para nomes (para logs legíveis)
        self.OPCODE_NAMES = {
            1: "ADD", 2: "SUB", 3: "ZEROS", 4: "XOR", 5: "OR", 6: "NOT",
            7: "AND", 8: "ASL", 9: "ASR", 10: "LSL", 11: "LSR", 12: "COPY",
            14: "LCLH", 15: "LCLL", 16: "LOAD", 17: "STORE",
            18: "JAL", 19: "JR", 20: "BEQ", 21: "BNE", 22: "J",
            32: "MUL", 33: "DIV", 34: "MOD", 35: "INC", 
            36: "DEC", 37: "MOVI", 38: "NOTBIT", 39: "NOP",
            255: "HALT"
        }
    
    def capture_initial_state(self):
        """Captura o estado inicial antes da primeira instrução."""
        self.prev_state["pc"] = self.cpu.state.pc
        self.prev_state["ir"] = self.cpu.state.ir
        self.prev_state["regs"] = copy.deepcopy(self.cpu.state.regs)
        self.prev_state["flags"] = copy.deepcopy(self.cpu.state.flags.as_dict())
        self.prev_state["memory"] = {}
        self.cycle_count = 0
    
    def log_cycle(self, stage: str = "COMPLETE"):
        """
        Registra as mudanças de estado após um ciclo completo de instrução.
        
        Args:
            stage: Estágio atual (IF, ID, EX/MEM, WB, COMPLETE)
        """
        self.cycle_count += 1
        
        # Estado atual
        current_pc = self.cpu.state.pc
        current_ir = self.cpu.state.ir
        current_regs = self.cpu.state.regs
        current_flags = self.cpu.state.flags.as_dict()
        
        # Decodifica a instrução para log legível
        opcode = self.cpu.extract_field(current_ir, 24, 31)
        instr_name = self.OPCODE_NAMES.get(opcode, f"UNKNOWN({opcode})")
        
        # Extrai campos da instrução
        ra_idx = self.cpu.extract_field(current_ir, 16, 23)
        rb_idx = self.cpu.extract_field(current_ir, 8, 15)
        rc_idx = self.cpu.extract_field(current_ir, 0, 7)
        const16 = self.cpu.extract_field(current_ir, 8, 23)
        addr24 = self.cpu.extract_field(current_ir, 0, 23)
        
        # Monta representação legível da instrução
        instr_repr = self._format_instruction(instr_name, ra_idx, rb_idx, rc_idx, const16, addr24)
        
        # Detecta mudanças
        changes = {
            "cycle": self.cycle_count,
            "stage": stage,
            "pc_before": self.prev_state["pc"],
            "pc_after": current_pc,
            "ir_binary": f"{current_ir:032b}",
            "ir_hex": f"0x{current_ir:08X}",
            "instruction": instr_repr,
            "registers_changed": [],
            "flags_changed": [],
            "memory_changed": []
        }
        
        # Detecta mudanças em registradores
        for i in range(32):
            if current_regs[i] != self.prev_state["regs"][i]:
                changes["registers_changed"].append({
                    "reg": f"R{i}",
                    "before": self.prev_state["regs"][i],
                    "after": current_regs[i],
                    "before_signed": self.cpu.uint32_to_signed(self.prev_state["regs"][i]),
                    "after_signed": self.cpu.uint32_to_signed(current_regs[i])
                })
        
        # Detecta mudanças em flags
        for flag_name in ["neg", "zero", "carry", "overflow"]:
            if current_flags[flag_name] != self.prev_state["flags"][flag_name]:
                changes["flags_changed"].append({
                    "flag": flag_name,
                    "before": self.prev_state["flags"][flag_name],
                    "after": current_flags[flag_name]
                })
        
        # Detecta mudanças na memória
        for addr in self.cpu._modified_addresses:
            if addr not in self.prev_state["memory"] or \
               self.cpu.memory[addr] != self.prev_state["memory"].get(addr, 0):
                changes["memory_changed"].append({
                    "address": addr,
                    "before": self.prev_state["memory"].get(addr, 0),
                    "after": self.cpu.memory[addr]
                })
                self.prev_state["memory"][addr] = self.cpu.memory[addr]
        
        # Atualiza estado anterior
        self.prev_state["pc"] = current_pc
        self.prev_state["ir"] = current_ir
        self.prev_state["regs"] = copy.deepcopy(current_regs)
        self.prev_state["flags"] = copy.deepcopy(current_flags)
        
        # Adiciona log à lista
        self.logs.append(changes)
        
        return changes
    
    def _format_instruction(self, name: str, ra: int, rb: int, rc: int, const16: int, addr24: int) -> str:
        """Formata a instrução de forma legível."""
        if name == "HALT":
            return "HALT"
        elif name == "NOP":
            return "NOP"
        elif name in ["ADD", "SUB", "XOR", "OR", "AND", "ASL", "ASR", "LSL", "LSR", "MUL", "DIV", "MOD", "NOTBIT"]:
            return f"{name} R{rc}, R{ra}, R{rb}"
        elif name in ["NOT", "COPY", "INC", "DEC"]:
            return f"{name} R{rc}, R{ra}"
        elif name in ["ZEROS", "JR"]:
            return f"{name} R{rc}"
        elif name in ["LCLH", "LCLL", "MOVI"]:
            return f"{name} R{rc}, {const16}"
        elif name in ["LOAD", "STORE"]:
            return f"{name} R{rc}, R{ra}"
        elif name in ["BEQ", "BNE"]:
            return f"{name} R{ra}, R{rb}, {rc}"
        elif name in ["J", "JAL"]:
            return f"{name} {addr24}"
        else:
            return f"{name} (opcode desconhecido)"
    
    def print_cycle_log(self, cycle_data: Dict):
        """Imprime o log de um ciclo de forma formatada."""
        print(f"\n{'='*80}")
        print(f"CICLO {cycle_data['cycle']} - Estágio: {cycle_data['stage']}")
        print(f"{'='*80}")
        print(f"PC: {cycle_data['pc_before']} → {cycle_data['pc_after']}")
        print(f"IR: {cycle_data['ir_hex']} ({cycle_data['ir_binary']})")
        print(f"Instrução: {cycle_data['instruction']}")
        
        if cycle_data['registers_changed']:
            print(f"\n--- Registradores Modificados ---")
            for reg_change in cycle_data['registers_changed']:
                print(f"  {reg_change['reg']}: {reg_change['before']} → {reg_change['after']} "
                      f"(signed: {reg_change['before_signed']} → {reg_change['after_signed']})")
        
        if cycle_data['flags_changed']:
            print(f"\n--- Flags Modificados ---")
            for flag_change in cycle_data['flags_changed']:
                print(f"  {flag_change['flag']}: {flag_change['before']} → {flag_change['after']}")
        
        if cycle_data['memory_changed']:
            print(f"\n--- Memória Modificada ---")
            for mem_change in cycle_data['memory_changed']:
                print(f"  MEM[{mem_change['address']}]: {mem_change['before']} → {mem_change['after']}")
        
        if not cycle_data['registers_changed'] and not cycle_data['flags_changed'] and not cycle_data['memory_changed']:
            print("\n(Nenhuma mudança de estado detectada)")
    
    def save_logs_to_file(self, filepath: str):
        """Salva todos os logs em um arquivo texto."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("LOG DE EXECUÇÃO DO SIMULADOR UFLA-RISC\n")
            f.write("="*80 + "\n\n")
            
            for log_entry in self.logs:
                f.write(f"\n{'='*80}\n")
                f.write(f"CICLO {log_entry['cycle']} - Estágio: {log_entry['stage']}\n")
                f.write(f"{'='*80}\n")
                f.write(f"PC: {log_entry['pc_before']} → {log_entry['pc_after']}\n")
                f.write(f"IR: {log_entry['ir_hex']} ({log_entry['ir_binary']})\n")
                f.write(f"Instrução: {log_entry['instruction']}\n")
                
                if log_entry['registers_changed']:
                    f.write(f"\n--- Registradores Modificados ---\n")
                    for reg_change in log_entry['registers_changed']:
                        f.write(f"  {reg_change['reg']}: {reg_change['before']} → {reg_change['after']} "
                              f"(signed: {reg_change['before_signed']} → {reg_change['after_signed']})\n")
                
                if log_entry['flags_changed']:
                    f.write(f"\n--- Flags Modificados ---\n")
                    for flag_change in log_entry['flags_changed']:
                        f.write(f"  {flag_change['flag']}: {flag_change['before']} → {flag_change['after']}\n")
                
                if log_entry['memory_changed']:
                    f.write(f"\n--- Memória Modificada ---\n")
                    for mem_change in log_entry['memory_changed']:
                        f.write(f"  MEM[{mem_change['address']}]: {mem_change['before']} → {mem_change['after']}\n")
                
                if not log_entry['registers_changed'] and not log_entry['flags_changed'] and not log_entry['memory_changed']:
                    f.write("\n(Nenhuma mudança de estado detectada)\n")
            
            f.write(f"\n{'='*80}\n")
            f.write(f"TOTAL DE CICLOS: {self.cycle_count}\n")
            f.write(f"{'='*80}\n")
    
    def get_summary(self) -> Dict:
        """Retorna um resumo da execução."""
        return {
            "total_cycles": self.cycle_count,
            "total_logs": len(self.logs),
            "final_pc": self.cpu.state.pc,
            "final_flags": self.cpu.state.flags.as_dict()
        }


# -----------------------------------------------------------------------------
# Teste do Logger
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Módulo logger.py criado com sucesso!")
    print("Este módulo será integrado à CPU para gerar logs detalhados.")
