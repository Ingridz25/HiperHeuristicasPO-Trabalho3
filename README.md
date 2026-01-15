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

## 📈 Análise de Resultados

### Arquivos Gerados

Após executar `--experiment`, verifique a pasta `results/`:

```
results/
├── experiment_20250114_143022.csv   # Dados tabulares
└── experiment_20250114_143022.json  # Dados estruturados
```

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

**Referência principal:**
Burke, E. K., et al. (2013). Hyper-heuristics: A survey of the state of the art. *Journal of the Operational Research Society*, 64(12), 1695-1724.
https://doi.org/10.1057/jors.2013.71

---

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

### Criar Instância Personalizada

```python
from instance import KnapsackInstance

# Manualmente
inst = KnapsackInstance(
    capacity=100,
    weights=[10, 20, 30, 40],
    values=[60, 100, 120, 150]
)

# De arquivo
inst = KnapsackInstance.from_file("caminho/arquivo.txt")
```

---

## 🧪 Reprodutibilidade

Todas as execuções utilizam **seeds fixas** para garantir reprodutibilidade:

```python
# Experimento usa base_seed + run_number
python main.py --experiment --runs 10
# Run 1: seed=42, Run 2: seed=43, ..., Run 10: seed=51
```

Para alterar a seed base, modifique em `experiments.py`:

```python
runner.run_multiple(..., base_seed=1234)
```

---

## 🎓 Conceitos-Chave Implementados

### ✅ Complexidade Computacional
- Greedy: O(n log n)
- 1-Flip: O(n)
- 2-Swap: O(n²)
- SA: O(iterações × n)

### ✅ Estruturas de Vizinhança
- Flip: inverter um bit
- Swap: trocar item dentro por fora
- Multi-swap: múltiplas trocas

### ✅ Critérios de Aceitação
- Hill Climbing: apenas melhorias
- SA: Metropolis (aceita pioras com probabilidade)
- GRASP: melhoria após construção

### ✅ Mecanismos de Aprendizado
- Roleta: scores proporcionais
- Epsilon-greedy: exploração decrescente
- Q-Learning: atualização baseada em recompensas

---

## 📚 Exemplos de Uso

### Exemplo 1: Comparar Heurísticas

```python
from instance import KnapsackInstance
from heuristics import greedy_value, greedy_ratio, greedy_weight

inst = KnapsackInstance.from_file("instances/knapPI_1_100_1000_1.txt")

sol1 = greedy_value(inst)
sol2 = greedy_ratio(inst)
sol3 = greedy_weight(inst)

print(f"Greedy Valor: {sol1.value}")
print(f"Greedy Razão: {sol2.value}")
print(f"Greedy Peso:  {sol3.value}")
```

### Exemplo 2: Executar Hiperheurística

```python
from hyperheuristic import AdaptiveHyperHeuristic, get_default_heuristics
from instance import KnapsackInstance

inst = KnapsackInstance.from_file("instances/knapPI_1_200_1000_1.txt")
hh = AdaptiveHyperHeuristic(get_default_heuristics())

solution = hh.solve(inst, iterations=200, verbose=True)

print(f"Valor encontrado: {solution.value}")
print(f"Gap: {solution.calculate_gap():.2f}%")

hh.print_statistics()  # Mostra uso de cada heurística
```

### Exemplo 3: Experimento Customizado

```python
from experiments import ExperimentRunner, generate_random_instance

runner = ExperimentRunner(output_dir="meus_resultados")

# Gera instâncias
instances = [
    generate_random_instance(50, seed=42),
    generate_random_instance(100, seed=43),
]

# Define algoritmos
algorithms = {
    'SA': (simulated_annealing, {'initial_temp': 1000}),
    'GRASP': (grasp, {'max_iterations': 100}),
}

# Executa
for inst in instances:
    runner.run_comparison(inst, algorithms, num_runs=10)

# Salva
runner.save_to_csv("resultados.csv")
runner.print_summary()
```

---

## ⚠️ Solução de Problemas

### Erro: "FileNotFoundError: instances/..."

**Solução:** Execute primeiro `python download_instances.py`

### Erro: "ModuleNotFoundError"

**Solução:** Certifique-se de estar no diretório do projeto:
```bash
cd HiperHeuristicasPO-Trabalho3-main
python main.py
```

### Experimento muito lento

**Solução:** Reduza número de execuções ou tamanho das instâncias:
```bash
python main.py --experiment --runs 5
```

Ou edite `experiments.py` para usar apenas instâncias pequenas.

### Gap retorna None

**Causa:** Instância sem valor ótimo conhecido.

**Solução:** O gap só é calculado quando `instance.optimal_value` está definido. Use instâncias da OR-Library que incluem valores ótimos.

---

## 📊 Checklist do Trabalho

### Implementação ✅
- [x] 4+ heurísticas construtivas
- [x] 3+ heurísticas de melhoria
- [x] 3 metaheurísticas (SA, HC, GRASP)
- [x] 4 hiperheurísticas com mecanismos distintos
- [x] Código modular e bem documentado
- [x] Referência a Burke et al. (2012)

### Experimentação ⏳
- [ ] **Baixar instâncias OR-Library** → `python download_instances.py`
- [ ] **Executar experimento completo** → `python main.py --experiment --runs 10`
- [ ] Múltiplas execuções (10+) ✅ (código pronto)
- [ ] Instâncias variadas (pequenas, médias, grandes)
- [ ] Métricas: valor, tempo, gap ✅ (código pronto)
- [ ] Exportação CSV/JSON ✅ (código pronto)

### Documentação ✅
- [x] README.md completo (este arquivo)
- [x] Código comentado (docstrings)
- [x] Links para datasets
- [ ] **Relatório técnico 8-12 páginas** (próximo passo)

---

## 📖 Referências

1. **Burke, E. K., Hyde, M., Kendall, G., Ochoa, G., Özcan, E., & Woodward, J. R.** (2012). Hyper-heuristics: A survey of the state of the art. *European Journal of Operational Research*, 64(12), 1695-1724. https://doi.org/10.1016/j.ejor.2012.10.039

2. **Pisinger, D.** (2005). Where are the hard knapsack problems? *Computers & Operations Research*, 32(9), 2271-2284.

3. **OR-Library - Knapsack Problem Instances**
   https://people.brunel.ac.uk/~mastjjb/jeb/orlib/knapsackinfo.html

4. **Jooken, J.** Knapsack Problem Instances (GitHub)
   https://github.com/JorikJooken/knapsackProblemInstances

---

## 👨‍💻 Autor

Trabalho de Pesquisa Operacional - Ciência da Computação  
Data de entrega: 09/01/2026

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos.

---

## 🆘 Suporte

Para dúvidas sobre o código:
1. Leia este README completamente
2. Execute os exemplos fornecidos
3. Consulte os comentários no código (docstrings)
4. Execute os testes individuais (`python heuristics.py`, etc.)

---

**Próximos Passos:**

1. ✅ Ler este README
2. ⏳ Executar `python download_instances.py`
3. ⏳ Executar `python main.py --experiment --runs 10`
4. ⏳ Analisar resultados em `results/`
5. ⏳ Escrever relatório técnico (8-12 páginas)
6. ✅ Apresentação em sala (23/01/2026)