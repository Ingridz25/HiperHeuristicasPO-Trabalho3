# Hiperheurística para o Problema da Mochila Binária

## 📋 Descrição do Projeto

Este projeto implementa uma solução completa e incremental para o **Problema da Mochila Binária (0/1 Knapsack Problem)** utilizando heurísticas, metaheurísticas e **hiperheurísticas** adaptativas.

**Trabalho de Pesquisa Operacional** - Ciência da Computação

---

## 🎯 Objetivos

- Implementar heurísticas construtivas e de melhoria
- Desenvolver metaheurísticas clássicas (SA, HC, GRASP)
- Criar hiperheurísticas de seleção com aprendizado adaptativo
- Realizar experimentação computacional rigorosa
- Analisar comparativamente o desempenho dos algoritmos

---

## 🏗️ Estrutura do Projeto

```
HiperHeuristicasPO-Trabalho3/
│
├── instance.py              # Representação de instâncias
├── solution.py              # Representação de soluções
├── heuristics.py            # Heurísticas de baixo nível (6+)
├── metaheuristic.py         # Metaheurísticas (SA, HC, GRASP)
├── hyperheuristic.py        # Hiperheurísticas (4 mecanismos)
├── experiments.py           # Framework experimental
├── main.py                  # Programa principal
├── download_instances.py    # Download de instâncias OR-Library
│
├── instances/               # Instâncias do problema
│   ├── INSTANCIAS_INFO.txt
│   ├── knapPI_1_50_1000_1.txt
│   ├── knapPI_1_100_1000_1.txt
│   └── ...
│
├── results/                 # Resultados experimentais (CSV/JSON)
│   ├── experiment_*.csv
│   └── experiment_*.json
│
├── requirements.txt         # Dependências (apenas Python padrão)
└── README.md               # Este arquivo
```

---

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Bibliotecas padrão do Python (nenhuma instalação adicional necessária)

### Instalação

1. **Clone ou baixe o projeto:**
```bash
cd HiperHeuristicasPO-Trabalho3-main
```

2. **Baixe as instâncias da OR-Library:**
```bash
python download_instances.py
```

Este script irá:
- Baixar 7 instâncias de tamanhos variados (50 a 1000 itens)
- Adicionar valores ótimos conhecidos aos arquivos
- Criar catálogo com informações das instâncias

---

## 🚀 Como Executar

### 1. Modo Demonstração (Recomendado para começar)

Executa uma demonstração completa com explicações didáticas:

```bash
python main.py
```

ou

```bash
python main.py --demo
```

**Saída esperada:**
- Execução de todas as heurísticas
- Comparação de metaheurísticas
- Teste de todas as 4 hiperheurísticas
- Análise do comportamento adaptativo

---

### 2. Executar com Instância Específica

```bash
python main.py --instance instances/knapPI_1_100_1000_1.txt
```

**Opções:**
- `-i, --instance PATH`: Caminho para arquivo de instância
- `-v, --verbose`: Modo detalhado (mostra progresso)

---

### 3. Experimento Completo (OBRIGATÓRIO para o trabalho)

```bash
python main.py --experiment --runs 10
```

**Parâmetros:**
- `--experiment, -e`: Ativa modo experimental
- `--runs N, -r N`: Número de execuções por algoritmo (padrão: 10)

**O que o experimento faz:**
1. Carrega todas as instâncias disponíveis
2. Executa 10 vezes cada algoritmo em cada instância
3. Coleta métricas: valor, tempo, gap, desvio padrão
4. Salva resultados em `results/experiment_TIMESTAMP.csv` e `.json`
5. Imprime resumo estatístico

**Tempo estimado:** 10-30 minutos (depende do número de instâncias)

---

### 4. Testar Módulos Individualmente

```bash
# Testar heurísticas
python heuristics.py

# Testar metaheurísticas
python metaheuristic.py

# Testar hiperheurísticas
python hyperheuristic.py

# Testar framework experimental
python experiments.py
```

---

## 📊 Algoritmos Implementados

### 🧩 Heurísticas Construtivas (4)

1. **Greedy por Valor** - Prioriza itens mais valiosos
2. **Greedy por Peso** - Prioriza itens mais leves
3. **Greedy por Razão** - Melhor custo-benefício (valor/peso)
4. **Greedy Aleatorizada** - Construção semi-aleatória (para GRASP)

### 🔄 Heurísticas de Melhoria (3+)

5. **Local Search 1-Flip** - Inverte um item por vez
6. **Local Search 2-Swap** - Troca item dentro por fora
7. **Fill Remaining** - Preenche capacidade restante
8. **Remove Worst** - Remove item com pior razão

### 🎯 Metaheurísticas (3)

1. **Simulated Annealing (SA)**
   - Aceita pioras temporárias para escapar de ótimos locais
   - Parâmetros: temperatura inicial, taxa de resfriamento
   
2. **Hill Climbing com Reinício**
   - Múltiplas execuções de pontos aleatórios
   - Parâmetros: número de reinícios, iterações por execução

3. **GRASP**
   - Construção aleatorizada + busca local
   - Parâmetros: alpha (aleatoriedade), iterações

### 🧠 Hiperheurísticas (4 mecanismos adaptativos)

1. **Roleta Ponderada (Roulette Wheel)**
   - Seleção proporcional ao desempenho histórico
   
2. **Epsilon-Greedy**
   - Balanceamento exploração vs exploitação
   - Epsilon decai ao longo do tempo
   
3. **Aprendizado por Reforço (RL)**
   - Q-Learning simplificado
   - Seleção softmax sobre Q-values
   
4. **Hiperheurística Adaptativa (COMPLETA)**
   - Combina epsilon-greedy + RL
   - Reinício automático ao detectar estagnação
   - **Recomendada para análise principal**

---

### Métricas Coletadas

Para cada execução:
- `algorithm`: Nome do algoritmo
- `instance_size`: Número de itens
- `instance_capacity`: Capacidade da mochila
- `value`: Valor da solução encontrada
- `weight`: Peso total
- `execution_time`: Tempo em segundos
- `gap_percent`: Gap em relação ao ótimo (se conhecido)
- `seed`: Seed para reprodutibilidade

### Estatísticas Calculadas

- Valor médio ± desvio padrão
- Melhor e pior valor
- Tempo médio de execução
- Gap médio (quando ótimo conhecido)

---

## 🔬 Fundamentação Teórica

### Problema da Mochila Binária

Dado:
- Conjunto de `n` itens
- Cada item `i` tem valor `vᵢ` e peso `wᵢ`
- Mochila com capacidade `C`

Objetivo:
- Maximizar ∑ vᵢxᵢ
- Sujeito a: ∑ wᵢxᵢ ≤ C
- Onde xᵢ ∈ {0, 1}

### Hiperheurísticas

**Definição (Burke et al., 2012):**
> "Hiperheurísticas são métodos de busca que operam no espaço de heurísticas (ou componentes de heurísticas) ao invés de operar diretamente no espaço de soluções."

**Características:**
- Seleção adaptativa baseada em desempenho
- Atualização online de scores/pesos
- Balanço entre exploração e exploitação

## 📝 Formato das Instâncias

### Formato OR-Library

```
# optimal: 9147
50 995
92 8
4 59
43 27
...
```

**Estrutura:**
- Linha 1 (opcional): `# optimal: <valor_ótimo>`
- Linha 2: `<n> <capacidade>`
- Linhas 3+: `<valor> <peso>` (um item por linha)
