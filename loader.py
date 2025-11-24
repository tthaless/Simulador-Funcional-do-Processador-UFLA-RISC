from dataclasses import dataclass, field
from typing import List, Tuple, Optional

MEMORY_SIZE = 65536          # 64K palavras (word-addressed)
WORD_MASK = 0xFFFFFFFF       # 32-bit mask
REG_COUNT = 32

@dataclass
class Flags:
    neg: int = 0
    zero: int = 0
    carry: int = 0
    overflow: int = 0

    def as_dict(self):
        return {"neg": self.neg, "zero": self.zero, "carry": self.carry, "overflow": self.overflow}

@dataclass
class CPUState:
    regs: List[int] = field(default_factory=lambda: [0]*REG_COUNT)  # 32 registers, 32-bit each
    pc: int = 0        # Program counter (word address)
    ir: int = 0        # Instruction register (32-bit word)
    flags: Flags = field(default_factory=Flags)
    halted: bool = False

class MemoryLoader:
    """
    MemoryLoader fornece:
    - memória word-addressed de 64K palavras (32 bits cada)
    - inicialização de registradores, PC, IR e flags
    - parsing de arquivos no formato: diretiva "address <binary>" e linhas de 32 bits
    - funções de leitura/escrita de memória e utilitários para integração com a CPU
    """

    def __init__(self):
        self.memory: List[int] = [0] * MEMORY_SIZE  # each entry is a 32-bit word (unsigned)
        self.state = CPUState()
        self._modified_addresses: set = set()  # for logs

    # ---------- utilitários ----------
    @staticmethod
    def _binstr_to_uint32(binstr: str) -> int:
        b = binstr.strip()
        if len(b) != 32:
            raise ValueError(f"Each instruction line must be 32 bits long. Got length {len(b)}: '{b}'")
        if not all(ch in '01' for ch in b):
            raise ValueError(f"Binary instruction contains invalid characters: '{b}'")
        return int(b, 2) & WORD_MASK

    @staticmethod
    def uint32_to_signed(x: int) -> int:
        x &= WORD_MASK
        if x & (1 << 31):
            return x - (1 << 32)
        return x

    @staticmethod
    def signed_to_uint32(x: int) -> int:
        return x & WORD_MASK

    # ---------- memória ----------
    def read_mem(self, address: int) -> int:
        """Lê uma palavra (32-bit) em endereço (word address)."""
        self._check_address(address)
        return self.memory[address]

    def write_mem(self, address: int, value: int):
        """Escreve uma palavra (32-bit) em endereço (word address)."""
        self._check_address(address)
        self.memory[address] = value & WORD_MASK
        self._modified_addresses.add(address)

    def _check_address(self, address: int):
        if not (0 <= address < MEMORY_SIZE):
            raise IndexError(f"Memory address out of range: {address}. Valid: 0..{MEMORY_SIZE-1}")

    # ---------- registradores e estado ----------
    def init_registers(self):
        """Zera registradores, PC, IR, flags e limpa histórico de mudanças."""
        self.state.regs = [0] * REG_COUNT
        self.state.pc = 0
        self.state.ir = 0
        self.state.flags = Flags()
        self.state.halted = False
        self._modified_addresses.clear()

    # ---------- carregador de arquivo ----------
    def load_from_file(self, filepath: str, verbose: bool = False) -> Tuple[int,int]:
        """
        Carrega as instruções de um arquivo texto no formato especificado:
        - Diretiva: `address <binary>` (binary = bits representando endereço word-addressed)
        - Seguido de linhas de 32 bits (ex.: 00001111000011110000111100001111)
        Retorna (first_address_loaded, last_address_loaded).
        Se nenhum dado for carregado, retorna (-1, -1).
        """
        current_address = 0
        first_loaded: Optional[int] = None
        last_loaded: Optional[int] = None

        with open(filepath, 'r', encoding='utf-8') as f:
            for lineno, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                # ignore comments that start with '#' or '//' (flexível)
                if line.startswith('#') or line.startswith('//'):
                    continue
                # diretiva address
                if line.lower().startswith('address'):
                    parts = line.split()
                    if len(parts) != 2:
                        raise ValueError(f"Invalid address directive at line {lineno}: '{line}'")
                    bin_addr = parts[1].strip()
                    if not all(ch in '01' for ch in bin_addr):
                        raise ValueError(f"Address must be binary string at line {lineno}: '{bin_addr}'")
                    current_address = int(bin_addr, 2)
                    if verbose:
                        print(f"[Loader] linha {lineno}: set current_address = {current_address}")
                    continue
                # instrução em binário (32 bits)
                bits = ''.join(line.split())  # remove espaços caso existam
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

        if first_loaded is None:
            return (-1, -1)
        # inicializa PC para endereço inicial por convenção
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
            out.append((i, v & WORD_MASK, self.uint32_to_signed(v)))
        return out

    def state_summary(self) -> dict:
        """Resumo do estado atual (pc, ir, flags, registradores modificados)."""
        return {
            "pc": self.state.pc,
            "ir": f"{self.state.ir & WORD_MASK:032b}",
            "flags": self.state.flags.as_dict(),
            "modified_mem_addresses": sorted(self._modified_addresses)
        }

    # ---------- auxiliares para integração com CPU ----------
    def fetch_instruction(self) -> int:
        """Lê a instrução apontada por PC e carrega em IR (não incrementa PC aqui; deixar convenção com CPU)."""
        instr = self.read_mem(self.state.pc)
        self.state.ir = instr
        return instr

    def set_pc(self, value:int):
        if not (0 <= value < MEMORY_SIZE):
            raise IndexError("PC out of range.")
        self.state.pc = value

    def incr_pc(self, step:int=1):
        new_pc = self.state.pc + step
        if not (0 <= new_pc < MEMORY_SIZE):
            raise IndexError("PC out of range after increment.")
        self.state.pc = new_pc


# ------------- Exemplo de uso / teste rápido -------------
if __name__ == "__main__":
    # Roda um teste rápido se executado diretamente (não é executado quando importado)
    import tempfile, os
    sample = """address 0
00000001000000100000001100000100
00000010000001000000010100000110
address 10
00000011000000010000001000000011
"""
    tmp = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
    try:
        tmp.write(sample)
        tmp.close()

        loader = MemoryLoader()
        loader.init_registers()
        first, last = loader.load_from_file(tmp.name, verbose=True)
        print("first,last:", first, last)
        print("PC inicial:", loader.state.pc)
        print("Dump 0..12:")
        for addr, bits in loader.dump_memory_region(0,12):
            print(addr, bits)
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
