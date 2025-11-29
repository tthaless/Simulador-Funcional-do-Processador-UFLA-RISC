# Simulador Funcional do Processador UFLA-RISC

Este projeto implementa um simulador funcional para o processador RISC de 32 bits UFLA-RISC, desenvolvido como trabalho prático da disciplina de Arquitetura de Computadores II.

## Integrantes do Grupo

- Alexandra Melo
- Brenda Moreira da Silva
- Samuel Henrique Morais Rufino
- Arienne Alves Navarro
- Thales Rodrigues Resende

## Características do Simulador

- 32 registradores de uso geral (R0-R31)
- Memória de 256 KB (64K palavras de 32 bits)
- 30 instruções (22 base + 8 extras)
- Sistema de logging completo
- Framework de testes automatizados
- 36 testes com 100% de aprovação

## Estrutura do Projeto

```
Simulador-Funcional-do-Processador-UFLA-RISC-main/
├── src/
│   ├── interpretador.py       # Assembler
│   ├── loader.py              # Memória e Estado
│   ├── cpu.py                 # CPU e Execução
│   ├── logger.py              # Sistema de Logging
│   ├── cpu_logged.py          # CPU com Logging
│   ├── test_framework.py      # Framework de Testes
│   ├── testes_isolados.py     # Testes por Instrução
│   └── testes_massivos.py     # Testes de Programas
├── testes/
│   ├── isolados/              # Resultados dos testes isolados
│   └── massivos/              # Resultados dos testes massivos
└── documentacao/
    └── documentacao_final.md  # Documentação completa
```

## Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/usuario/ufla-risc-simulador.git
cd ufla-risc-simulador
```

### 2. Escreva um programa em assembly

Crie um arquivo `teste.txt` com código assembly:

```assembly
address 0
lclh r1, 0
lcll r1, 10
lclh r2, 0
lcll r2, 20
add r3, r1, r2
halt
```

### 3. Monte o código (gere o binário)

```bash
cd src
python3.11 interpretador.py
```

Isso gera o arquivo `programa.bin`.

### 4. Execute o simulador

```bash
python3.11 cpu.py
```

Ou com logging detalhado:

```bash
python3.11 cpu_logged.py
```

### 5. Execute com um arquivo binário específico

```bash
python3.11 cpu.py programa.bin
```

## Testes

Execute os testes isolados (26 testes):

```bash
cd src
python3.11 testes_isolados.py
```

Execute os testes massivos (10 programas):

```bash
python3.11 testes_massivos.py
```

Ou execute todos os testes:

```bash
python3.11 -m unittest discover
```

## Conjunto de Instruções

### Instruções Base (22)

- **Aritméticas:** add, sub, zero
- **Lógicas:** xor, or, and, passnota
- **Shift:** asl, asr, lsl, lsr
- **Cópia:** passa
- **Constantes:** lclh, lcll
- **Memória:** load, store
- **Controle:** j, jal, jr, beq, bne
- **Sistema:** halt

### Instruções Extras (8)

- **mul:** Multiplicação de inteiros
- **div:** Divisão de inteiros
- **mod:** Resto da divisão (módulo)
- **inc:** Incremento (+1)
- **dec:** Decremento (-1)
- **movi:** Move immediate (carrega constante)
- **notbit:** NOT bit-a-bit com 3 operandos
- **nop:** No operation

## Requisitos

- Python 3.11 ou superior
- Bibliotecas padrão do Python (nenhuma dependência externa)

## Documentação

Para informações detalhadas sobre a arquitetura, decisões de implementação e especificações técnicas, consulte, **apos rodar os testes**:

- [Documentação Final](documentacao/documentacao_final.md)
- [Relatório de Testes Isolados](testes/isolados/relatorio_testes_isolados.txt)
- [Relatório de Testes Massivos](testes/massivos/relatorio_testes_massivos.txt)

## Licença

Projeto acadêmico sem licença comercial.

---

**Universidade Federal de Lavras (UFLA)**  
**Disciplina:** Arquitetura de Computadores II - GCC123/PCC507  
**Ano:** 2025
