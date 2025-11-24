from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import sys

# --- CONSTANTES GLOBAIS ---
MEMORY_SIZE = 65536         # 64K palavras (word-addressed)
WORD_MASK = 0xFFFFFFFF      # 32-bit mask (garante 32 bits unsigned)
REG_COUNT = 32              # 32 registradores de uso geral

@dataclass
class Flags:
    """Representa os flags de condição (neg, zero, carry, overflow)."""
    neg: int = 0
    zero: int = 0
    carry: int = 0
    overflow: int = 0

    def as_dict(self):
        """Retorna os flags como um dicionário para logs."""
        return {"neg": self.neg, "zero": self.zero, "carry": self.carry, "overflow": self.overflow}

@dataclass
class CPUState:
    """Representa o estado interno da CPU (registradores, PC, IR, flags, estado de parada)."""
    regs: List[int] = field(default_factory=lambda: [0]*REG_COUNT)  # 32 registradores de 32 bits
    pc: int = 0         # Program Counter (endereço de palavra, 16 bits)
    ir: int = 0         # Instruction Register (palavra de 32 bits)
    flags: Flags = field(default_factory=Flags)
    halted: bool = False

class MemoryLoader:
    """
    Gerencia a memória principal (64K palavras), o estado da CPU e as 
    funções de I/O (carregador, leitura/escrita).
    """

    def __init__(self):
        # Memória: cada entrada é uma palavra de 32 bits (unsigned)
        self.memory: List[int] = [0] * MEMORY_SIZE
        self.state = CPUState()
        # Endereços modificados (útil para logs da Pessoa 5)
        self._modified_addresses: set = set()

    # ---------- utilitários de conversão e bits ----------
    @staticmethod
    def _binstr_to_uint32(binstr: str) -> int:
        """Converte uma string binária de 32 bits para um inteiro unsigned (uint32)."""
        b = binstr.strip()
        if len(b) != 32:
            raise ValueError(f"Each instruction line must be 32 bits long. Got length {len(b)}: '{b}'")
        if not all(ch in '01' for ch in b):
            raise ValueError(f"Binary instruction contains invalid characters: '{b}'")
        return int(b, 2) & WORD_MASK

    @staticmethod
    def uint32_to_signed(x: int) -> int:
        """Converte um inteiro unsigned de 32 bits para um inteiro assinado (complemento de dois)."""
        x &= WORD_MASK
        if x & (1 << 31):
            return x - (1 << 32)
        return x

    @staticmethod
    def signed_to_uint32(x: int) -> int:
        """Converte um inteiro assinado para um unsigned de 32 bits."""
        return x & WORD_MASK

    @staticmethod
    def extract_field(word_32bits: int, bit_inicio: int, bit_fim: int) -> int:
        """
        Extrai um campo de bits da palavra (Instrução Register - IR).
        Ex: OPCODE (31-24): bit_inicio=24, bit_fim=31.
        """
        tamanho_campo = bit_fim - bit_inicio + 1
        mascara = (1 << tamanho_campo) - 1
        return (word_32bits >> bit_inicio) & mascara

    # ---------- memória ----------
    def read_mem(self, address: int) -> int:
        """Lê uma palavra (32-bit) em endereço (word address)."""
        self._check_address(address)
        return self.memory[address]

    def write_mem(self, address: int, value: int):
        """Escreve uma palavra (32-bit) em endereço (word address)."""
        self._check_address(address)
        # Garante que o valor se encaixe em 32 bits
        self.memory[address] = value & WORD_MASK
        self._modified_addresses.add(address)

    def _check_address(self, address: int):
        """Verifica se o endereço está dentro dos limites da memória."""
        if not (0 <= address < MEMORY_SIZE):
            raise IndexError(f"Memory address out of range: {address}. Valid: 0..{MEMORY_SIZE-1}")

    # ---------- registradores e estado ----------
    def read_reg(self, reg_index: int) -> int:
        """Lê o valor de um registrador (R0-R31). R0 sempre retorna 0."""
        if reg_index < 0 or reg_index >= REG_COUNT:
            raise IndexError(f"Register index out of range: {reg_index}")
        # R0 é sempre 0 por convenção RISC
        if reg_index == 0:
            return 0
        return self.state.regs[reg_index]

    def write_reg(self, reg_index: int, value: int):
        """Escreve um valor em um registrador (R1-R31). Ignora escrita em R0."""
        if reg_index < 0 or reg_index >= REG_COUNT:
            raise IndexError(f"Register index out of range: {reg_index}")
        # R0 é sempre 0 e a escrita é ignorada (Write Back - WB)
        if reg_index != 0:
            self.state.regs[reg_index] = value & WORD_MASK
    
    # ---------- estado da CPU ----------
    def init_registers(self):
        """Zera registradores, PC, IR, flags e limpa histórico de mudanças."""
        self.state.regs = [0] * REG_COUNT
        self.state.pc = 0
        self.state.ir = 0
        self.state.flags = Flags()
        self.state.halted = False
        self._modified_addresses.clear()

    def fetch_instruction(self) -> int:
        """
        (Estágio IF) Lê a instrução apontada por PC e carrega em IR.
        Não incrementa PC aqui, a lógica de incremento fica na CPU (Pessoa 3).
        """
        instr = self.read_mem(self.state.pc)
        self.state.ir = instr
        return instr

    def set_pc(self, value:int):
        """Define o valor do Program Counter (PC). Usado para Jumps."""
        if not (0 <= value < MEMORY_SIZE):
            raise IndexError("PC out of range.")
        self.state.pc = value

    def incr_pc(self, step:int=1):
        """Incrementa o Program Counter (PC). Usado no IF (Instrução Fetch)."""
        new_pc = self.state.pc + step
        if not (0 <= new_pc < MEMORY_SIZE):
            raise IndexError("PC out of range after increment.")
        self.state.pc = new_pc


    # ---------- carregador de arquivo (Input) ----------
    def load_from_file(self, filepath: str, verbose: bool = False) -> Tuple[int,int]:
        """
        Carrega as instruções de um arquivo binário (gerado pela Pessoa 1) na memória.
        Retorna (first_address_loaded, last_address_loaded).
        """
        self.init_registers() # Limpa o estado antes de carregar
        
        current_address = 0
        first_loaded: Optional[int] = None
        last_loaded: Optional[int] = None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for lineno, raw in enumerate(f, start=1):
                    line = raw.strip()
                    if not line or line.startswith('#') or line.startswith('//'):
                        continue
                        
                    # 1. Diretiva address
                    if line.lower().startswith('address'):
                        parts = line.split()
                        if len(parts) != 2:
                             raise ValueError(f"Invalid address directive at line {lineno}: '{line}'")
                        bin_addr = parts[1].strip()
                        current_address = int(bin_addr, 2)
                        if verbose:
                            print(f"[Loader] linha {lineno}: set current_address = {current_address}")
                        continue
                        
                    # 2. Instrução em binário (32 bits)
                    bits = ''.join(line.split())
                    
                    if len(bits) != 32:
                        raise ValueError(f"Invalid instruction length at line {lineno}. Expected 32 bits, got {len(bits)}: '{bits}'")
                        
                    word = self._binstr_to_uint32(bits)
                    
                    if not (0 <= current_address < MEMORY_SIZE):
                        raise IndexError(f"Memory address {current_address} out of range while loading (line {lineno}).")
                        
                    self.write_mem(current_address, word)
                    if first_loaded is None:
                        first_loaded = current_address
                    last_loaded = current_address
                    
                    if verbose:
                        print(f"[Loader] linha {lineno}: mem[{current_address}] = {bits}")
                    
                    current_address += 1

        except FileNotFoundError:
            print(f"ERRO FATAL: Arquivo de instruções '{filepath}' não encontrado.")
            sys.exit(1)
        except Exception as e:
            print(f"ERRO durante o carregamento do arquivo na linha {lineno}: {e}")
            sys.exit(1)

        if first_loaded is None:
            return (-1, -1)

        # Convenção: se o address inicial não foi definido, PC é 0. Caso contrário,
        # PC deve apontar para o primeiro endereço carregado.
        self.state.pc = first_loaded
        return (first_loaded, last_loaded)

    # ---------- dumps / logs ----------
    def dump_memory_region(self, start: int, end: int) -> List[Tuple[int, str]]:
        """Retorna lista (addr, binstr) para intervalo [start, end] (inclusive)."""
        if start < 0 or end >= MEMORY_SIZE or start > end:
            raise IndexError("Invalid memory dump range.")
        out = []
        for addr in range(start, end+1):
            word = self.memory[addr]
            out.append((addr, f"{word:032b}"))
        return out

    def dump_registers(self) -> List[Tuple[int, int, int]]:
        """Retorna uma lista de (reg_index, value_unsigned, value_signed)."""
        out = []
        for i, v in enumerate(self.state.regs):
            # Lendo com read_reg garante que R0 seja 0
            unsigned_val = self.read_reg(i) 
            out.append((i, unsigned_val & WORD_MASK, self.uint32_to_signed(unsigned_val)))
        return out

    def state_summary(self) -> dict:
        """Resumo do estado atual (pc, ir, flags, registradores modificados)."""
        return {
            "pc": self.state.pc,
            "ir": f"{self.state.ir & WORD_MASK:032b}",
            "flags": self.state.flags.as_dict(),
            "modified_mem_addresses": sorted(self._modified_addresses)
        }


# ------------- Exemplo de uso / teste rápido -------------
if __name__ == "__main__":
    # Importar temporário para simular a criação do arquivo binário 
    import tempfile, os

    # Simulação do arquivo que a Pessoa 1 geraria
    # Note que aqui as strings binárias não têm citações
    sample_bin = """address 0000000000000000
00000001000000100000001100000001
00000010000001010000000100000101
00001110000000000000111100001010
00010000000010100000000000000100
00010100000000010000001000001010
00010110000000000000000000110010
11111111111111111111111111111111
"""
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
    try:
        tmp.write(sample_bin)
        tmp.close()
        filepath = tmp.name

        print("--- Testando (Loader/Memória/Estruturas) ---")

        loader = MemoryLoader()
        
        # Carregamento do arquivo
        first, last = loader.load_from_file(filepath, verbose=True)
        print(f"\n✅ Carregamento Concluído.")
        print(f"Endereços carregados: {first} até {last}")
        print(f"PC inicial após load: {loader.state.pc}")

        # Teste de leitura da memória
        print("\n--- Verificação da Memória e IR ---")
        halt_address = 6
        inst_halt = loader.read_mem(halt_address)
        print(f"Memória[{halt_address}] (HALT): {inst_halt} (Esperado 4294967295)")
        assert inst_halt == 4294967295

        # Teste de acesso ao PC e IR (simulação do IF)
        loader.set_pc(0)
        inst_fetch = loader.fetch_instruction()
        print(f"IR após fetch (PC=0): {loader.state.ir}")
        print(f"Opcode (31-24) da instrução (ADD): {loader.extract_field(inst_fetch, 24, 31)}")

        # Teste de acesso e escrita em registradores
        print("\n--- Teste de Registradores ---")
        loader.write_reg(2, 500)
        loader.write_reg(0, 999) # Tentativa de escrita em R0 (deve ser ignorada)
        r2_val = loader.read_reg(2)
        r0_val = loader.read_reg(0)
        print(f"R2 (escrito 500): {r2_val}")
        print(f"R0 (tentado escrever 999): {r0_val}")
        assert r2_val == 500
        assert r0_val == 0
        
        print("\nSUCESSO! `loader.py` está completo e pronto para a Etapa 3.")
        
    finally:
        # Limpa o arquivo temporário
        try:
            os.unlink(filepath)
        except Exception:
            pass