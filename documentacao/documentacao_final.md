# Simulador Funcional do Processador UFLA-RISC

**Integrantes:**
- Alexandra Melo
- Brenda Moreira da Silva
- Samuel Henrique Morais Rufino
- Arienne Alves Navarro
- Thales Rodrigues Resende

**Universidade Federal de Lavras**  
**Lavras - 2025**

---

## Sumário

1. [Resumo da Máquina Simulada](#resumo-da-máquina-simulada)
2. [Decisões de Implementação](#decisões-de-implementação)
3. [Instruções Extras Projetadas pelo Grupo](#instruções-extras-projetadas-pelo-grupo)
4. [Tutorial de Uso do Interpretador e Simulador](#tutorial-de-uso-do-interpretador-e-simulador)
5. [Estruturas de Representação do Hardware (Datapath)](#estruturas-de-representação-do-hardware-datapath)
6. [Código Fonte do Simulador](#código-fonte-do-simulador)
7. [Testes Realizados](#testes-realizados)

---

## Resumo da Máquina Simulada

O projeto implementa um simulador funcional para o processador **UFLA-RISC**, uma arquitetura RISC de 32 bits concebida para fins acadêmicos. O objetivo do simulador é replicar o comportamento de um processador real, dividindo a execução de cada instrução em quatro estágios principais: **IF (Busca), ID (Decodificação), EX/MEM (Execução/Memória) e WB (Escrita)**.

As principais características da arquitetura UFLA-RISC são:

| Característica | Descrição |
|:---------------|:----------|
| **Largura da Palavra** | 32 bits |
| **Barramento de Endereço** | 16 bits, permitindo endereçar 64K palavras. |
| **Memória Principal** | 256 KB (64K palavras de 4 bytes cada), endereçada por palavra. |
| **Registradores** | 32 registradores de uso geral (R0 a R31), cada um com 32 bits. R0 é fixo em zero. |
| **Conjunto de Instruções** | 22 instruções base e 8 instruções extras projetadas pelo grupo. |
| **Formato de Instrução** | Instruções de 3 operandos, codificadas em 32 bits. |
| **Flags de Condição** | O processador possui 4 flags: Negativo (N), Zero (Z), Carry (C) e Overflow (V). |
| **Condição de Parada** | A instrução `HALT` (todos os 32 bits em 1) finaliza a execução. |

---

## Decisões de Implementação

O simulador foi desenvolvido em **Python 3**, escolhido pela sua clareza, flexibilidade e vasto conjunto de bibliotecas padrão, facilitando a manipulação de dados e a prototipagem rápida.

A estrutura do projeto foi modularizada para refletir a divisão de tarefas e as responsabilidades de cada componente do processador:

- **interpretador.py**: Responsável por ler um arquivo de texto com código assembly UFLA-RISC e convertê-lo para um arquivo binário (`.bin`) que pode ser carregado pela CPU. Ele mapeia os mnemônicos das instruções para seus respectivos opcodes e organiza os operandos no formato de 32 bits.

- **loader.py**: Implementa a memória principal, os registradores e as estruturas de estado da CPU (`CPUState`). É responsável por carregar o arquivo binário na memória, inicializar o estado do processador e fornecer funções de acesso seguro à memória e aos registradores.

- **cpu.py**: Contém a lógica central do processador. Implementa o ciclo de execução principal (o loop que executa os estágios IF, ID, EX/MEM, WB) e a lógica de execução de cada uma das 22 instruções base e das 8 instruções extras.

- **logger.py** e **cpu_logged.py**: Para atender aos requisitos de depuração e análise, foi criado um sistema de logging. O `logger.py` captura o estado da CPU antes e depois de cada ciclo, registrando apenas as diferenças (delta) em registradores, flags e memória. O `cpu_logged.py` é uma subclasse da CPU que integra o logger, permitindo uma execução com rastreamento detalhado.

- **test_framework.py**, **testes_isolados.py** e **testes_massivos.py**: Foi desenvolvido um framework de testes automatizados para garantir a corretude do simulador. Ele permite criar programas de teste, executá-los e comparar o estado final da CPU com um conjunto de resultados esperados, gerando relatórios detalhados.

---

## Instruções Extras Projetadas pelo Grupo

Além das 22 instruções base, o grupo projetou e implementou 8 instruções extras para aumentar a capacidade e a eficiência do processador. A seguir, a descrição e a justificativa de cada uma:

| Instrução | Opcode | Formato | Justificativa |
|:----------|:-------|:--------|:--------------|
| `mul rc, ra, rb` | `00100000` | R_R_R | A multiplicação é uma operação aritmética fundamental, essencial para a maioria dos algoritmos complexos. |
| `div rc, ra, rb` | `00100001` | R_R_R | Assim como a multiplicação, a divisão é crucial para cálculos matemáticos. |
| `mod rc, ra, rb` | `00100010` | R_R_R | A operação de módulo (resto da divisão) é útil em algoritmos de hashing, cíclicos e de manipulação de dados. |
| `inc rc, ra` | `00100011` | R_R | Otimiza a implementação de contadores e loops, sendo mais eficiente que `add rc, ra, 1`. |
| `dec rc, ra` | `00100100` | R_R | Similar ao `inc`, otimiza o decremento em loops e contadores. |
| `movi rc, const16` | `00100101` | CONST | Carrega uma constante de 16 bits diretamente em um registrador, sendo mais simples que a combinação `lclh`/`lcll`. |
| `notbit rc, ra, rb` | `00100110` | R_R_R | Implementa a operação `~(ra & rb)`, útil em manipulações de bits e máscaras. |
| `nop` | `00100111` | NOP | *No Operation*. Útil para preenchimento de pipeline, alinhamento de código ou para criar atrasos de ciclo. |

---

## Tutorial de Uso do Interpretador e Simulador

O uso do simulador é dividido em três etapas principais: escrita do código, montagem (assembler) e execução.

### Escrevendo o Código Assembly

1. Crie um arquivo de texto (ex: `meu_programa.txt`).
2. Escreva as instruções em assembly UFLA-RISC, uma por linha.
3. Use a diretiva `address <numero>` para definir o endereço de memória onde o código será carregado.
4. Use `halt` para indicar o fim do programa.

**Exemplo (`teste.txt`):**

```assembly
address 0
add r1, r2, r3
sub r5, r5, r1
lclh r10, 15
load r4, r10
beq r1, r2, 10
j 50
halt
```

### Montando o Código (Gerando o Binário)

Execute o `interpretador.py` para converter seu arquivo de assembly para binário. O interpretador, por padrão, lê o arquivo `teste.txt` e gera o `programa.bin`.

```bash
cd /seu-pc/simulador/src
python3.11 interpretador.py
```

Isso criará o arquivo `programa.bin` no mesmo diretório, pronto para ser executado.

### Executando o Simulador

Execute o `cpu_logged.py` para rodar o programa binário. Ele carregará o `programa.bin`, executará as instruções e imprimirá um log detalhado de cada ciclo no console.

```bash
cd /seu-pc/simulador/src
python3.11 cpu_logged.py
```

Ao final da execução, um arquivo `execution_log.txt` será gerado com o registro completo de todas as mudanças de estado.

### Executando os Testes

Para validar a corretude de todo o sistema, execute as suítes de teste:

**Testes Isolados (por instrução):**

```bash
cd /seu-pc/simulador/src
python3.11 testes_isolados.py
```

**Testes Massivos (programas reais):**

```bash
cd /seu-pc/simulador/src
python3.11 testes_massivos.py
```

Os relatórios de teste e logs detalhados serão salvos nos diretórios `testes/isolados` e `testes/massivos`.

---

## Estruturas de Representação do Hardware (Datapath)

O hardware foi representado através de classes Python que encapsulam o estado e o comportamento de cada componente principal:

- **Flags (dataclass):** Armazena os quatro flags de condição (`neg`, `zero`, `carry`, `overflow`).

- **CPUState (dataclass):** Agrega todo o estado volátil da CPU em um único objeto, incluindo a lista de 32 registradores (`regs`), o Program Counter (`pc`), o Instruction Register (`ir`), os `flags` e o estado de parada (`halted`).

- **MemoryLoader:** Classe que gerencia a memória principal (um array de 65536 inteiros), o `CPUState` e as operações de I/O, como carregar um programa de um arquivo. Funções como `read_mem`, `write_mem`, `read_reg` e `write_reg` garantem o acesso seguro e correto aos componentes.

- **CPU:** Herda de `MemoryLoader` e implementa o ciclo de vida do processador. O método `run()` contém o loop principal, e o método `step()` executa um ciclo completo (IF, ID, EX/MEM, WB). O método `execute_instruction()` contém a lógica para cada opcode.

- **CPULogged:** Herda de `CPU` e adiciona a funcionalidade de logging, chamando o `StateLogger` a cada ciclo para registrar as mudanças.

---

## Código Fonte do Simulador

O código fonte completo está localizado no diretório `src/` e está organizado nos seguintes arquivos:

- `interpretador.py`: Assembler.
- `loader.py`: Gerenciador de memória e estado da CPU.
- `cpu.py`: Lógica da CPU e execução de instruções.
- `logger.py`: Sistema de logging de ciclos.
- `cpu_logged.py`: CPU com logging integrado.
- `test_framework.py`: Framework de testes automatizados.
- `testes_isolados.py`: Suíte de testes para cada instrução.
- `testes_massivos.py`: Suíte de testes para programas complexos.

---

## Testes Realizados

Para garantir a robustez e a corretude do simulador, uma bateria completa de testes automatizados foi desenvolvida e executada. Os testes foram divididos em duas categorias:

### Testes Isolados

Foram criados **26 testes isolados**, um para cada instrução base e extra. Cada teste executa a instrução com operandos conhecidos e verifica se o resultado no registrador de destino e os flags de condição correspondem ao valor esperado. Todos os 26 testes passaram com 100% de sucesso.

### Testes Massivos

Foram criados **10 testes massivos** que simulam programas reais, combinando múltiplas instruções para realizar tarefas complexas. Estes testes validam a interação entre as instruções, o controle de fluxo (loops e desvios) e o acesso à memória.

Os programas testados incluem:

1. Cálculo de Fatorial
2. Soma de elementos de um array
3. Cálculo da sequência de Fibonacci
4. Encontrar o valor máximo entre três números
5. Operações bit-a-bit complexas
6. Chamada de sub-rotina com `JAL` e `JR`
7. Cálculo de divisão e resto
8. Contador decrescente usando flags
9. Manipulação de memória (cópia invertida de array)
10. Execução sequencial de todas as 8 instruções extras

Após correções e simplificações na lógica dos programas de teste para se adequar às particularidades da arquitetura, **todos os 10 testes massivos passaram com 100% de sucesso**.

Os relatórios detalhados e os logs de execução de cada teste estão disponíveis nos diretórios `testes/isolados/` e `testes/massivos/`.

---

**Universidade Federal de Lavras (UFLA)**  
**Disciplina:** Arquitetura de Computadores II - GCC123
**Ano:** 2025
