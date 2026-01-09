"""
===========================================================
MÓDULO: experiments.py
Experimentação e Coleta de Resultados
===========================================================

Este módulo automatiza a execução de experimentos, coletando
métricas de desempenho para análise comparativa.

CONCEITO: Experimentacao Cientifica
--------------------------------------
Em Pesquisa Operacional, não basta implementar - precisamos
VALIDAR experimentalmente. Isso inclui:

1. Múltiplas execuções (para lidar com aleatoriedade)
2. Diferentes instâncias (pequenas, médias, grandes)
3. Métricas padronizadas (valor, tempo, gap)
4. Reprodutibilidade (usar seeds fixas)

Métricas coletadas:
- Valor da solução
- Tempo de execução
- Gap em relação ao ótimo (se conhecido)
- Número de iterações/chamadas
"""

import time
import random
import csv
import json
import os
from datetime import datetime

from instance import KnapsackInstance
from solution import Solution
from heuristics import (
    greedy_value, greedy_weight, greedy_ratio, greedy_random,
    local_search_1flip, local_search_2swap, get_all_heuristics_info
)
from metaheuristic import simulated_annealing, hill_climbing_restart, grasp
from hyperheuristic import (
    RouletteWheelHH, EpsilonGreedyHH, ReinforcementLearningHH,
    AdaptiveHyperHeuristic, get_default_heuristics
)


# =====================================================
# CLASSE PRINCIPAL DE EXPERIMENTAÇÃO
# =====================================================

class ExperimentRunner:
    """
    Gerenciador de experimentos.
    
    Automatiza a execução de algoritmos em múltiplas instâncias,
    coleta métricas e gera relatórios.
    """
    
    def __init__(self, output_dir="results"):
        """
        Inicializa o gerenciador de experimentos.
        
        Parâmetros:
        -----------
        output_dir : str
            Diretório para salvar resultados.
        """
        self.output_dir = output_dir
        self.results = []
        
        # Cria diretório de saída se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def run_single(self, algorithm_func, instance, algorithm_name, 
                   seed=None, **kwargs):
        """
        Executa um único experimento.
        
        Parâmetros:
        -----------
        algorithm_func : callable
            Função do algoritmo a executar.
        instance : KnapsackInstance
            Instância do problema.
        algorithm_name : str
            Nome do algoritmo (para identificação).
        seed : int
            Seed para reprodutibilidade.
        **kwargs : dict
            Parâmetros adicionais para o algoritmo.
        
        Retorna:
        --------
        dict
            Dicionário com métricas coletadas.
        """
        # Define seed para reprodutibilidade
        if seed is not None:
            random.seed(seed)
        
        # Mede tempo de execução
        start_time = time.time()
        solution = algorithm_func(instance, **kwargs)
        end_time = time.time()
        
        # Calcula métricas
        execution_time = end_time - start_time
        
        result = {
            'algorithm': algorithm_name,
            'instance_size': instance.n,
            'instance_capacity': instance.capacity,
            'seed': seed,
            'value': solution.value,
            'weight': solution.weight,
            'execution_time': execution_time,
            'feasible': solution.is_feasible(),
            'items_selected': len(solution.get_selected_items()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Adiciona gap se ótimo conhecido
        if instance.optimal_value is not None:
            gap = (instance.optimal_value - solution.value) / instance.optimal_value * 100
            result['optimal_value'] = instance.optimal_value
            result['gap_percent'] = gap
        
        return result
    
    def run_multiple(self, algorithm_func, instance, algorithm_name,
                     num_runs=10, base_seed=42, **kwargs):
        """
        Executa múltiplas vezes um algoritmo na mesma instância.
        
        Por que multiplas execucoes?
        Algoritmos com componente aleatório podem dar resultados
        diferentes a cada execução. Executando várias vezes,
        podemos calcular média, desvio padrão, etc.
        
        Parâmetros:
        -----------
        algorithm_func : callable
            Função do algoritmo.
        instance : KnapsackInstance
            Instância do problema.
        algorithm_name : str
            Nome do algoritmo.
        num_runs : int
            Número de execuções.
        base_seed : int
            Seed base (incrementada a cada execução).
        
        Retorna:
        --------
        list[dict]
            Lista de resultados.
        """
        results = []
        
        for run in range(num_runs):
            seed = base_seed + run
            result = self.run_single(
                algorithm_func, instance, algorithm_name,
                seed=seed, **kwargs
            )
            result['run_number'] = run + 1
            results.append(result)
        
        return results
    
    def run_comparison(self, instance, algorithms, num_runs=10, verbose=True):
        """
        Compara múltiplos algoritmos na mesma instância.
        
        Parâmetros:
        -----------
        instance : KnapsackInstance
            Instância do problema.
        algorithms : dict
            Dicionário {nome: (função, kwargs)}.
        num_runs : int
            Execuções por algoritmo.
        verbose : bool
            Se True, imprime progresso.
        
        Retorna:
        --------
        list[dict]
            Todos os resultados.
        """
        all_results = []
        
        for name, (func, kwargs) in algorithms.items():
            if verbose:
                print(f"Executando {name}...")
            
            results = self.run_multiple(
                func, instance, name,
                num_runs=num_runs, **kwargs
            )
            all_results.extend(results)
            
            # Resumo rápido
            values = [r['value'] for r in results]
            times = [r['execution_time'] for r in results]
            
            if verbose:
                print(f"  → Valor: {sum(values)/len(values):.1f} ± {self._std(values):.1f}")
                print(f"  → Tempo: {sum(times)/len(times)*1000:.2f} ± {self._std(times)*1000:.2f} ms")
        
        self.results.extend(all_results)
        return all_results
    
    def _std(self, values):
        """Calcula desvio padrão."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def save_to_csv(self, filename="results.csv", results=None):
        """
        Salva resultados em arquivo CSV.
        
        Parâmetros:
        -----------
        filename : str
            Nome do arquivo.
        results : list
            Lista de resultados (usa self.results se None).
        """
        if results is None:
            results = self.results
        
        if not results:
            print("Nenhum resultado para salvar!")
            return
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        print(f"[OK] Resultados salvos em: {filepath}")
    
    def save_to_json(self, filename="results.json", results=None):
        """Salva resultados em arquivo JSON."""
        if results is None:
            results = self.results
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Resultados salvos em: {filepath}")
    
    def generate_summary(self, results=None):
        """
        Gera resumo estatístico dos resultados.
        
        Retorna:
        --------
        dict
            Estatísticas por algoritmo.
        """
        if results is None:
            results = self.results
        
        # Agrupa por algoritmo
        by_algorithm = {}
        for r in results:
            alg = r['algorithm']
            if alg not in by_algorithm:
                by_algorithm[alg] = []
            by_algorithm[alg].append(r)
        
        # Calcula estatísticas
        summary = {}
        for alg, runs in by_algorithm.items():
            values = [r['value'] for r in runs]
            times = [r['execution_time'] for r in runs]
            
            summary[alg] = {
                'num_runs': len(runs),
                'value_mean': sum(values) / len(values),
                'value_std': self._std(values),
                'value_min': min(values),
                'value_max': max(values),
                'time_mean': sum(times) / len(times),
                'time_std': self._std(times),
            }
            
            # Gap se disponível
            gaps = [r.get('gap_percent') for r in runs if 'gap_percent' in r]
            if gaps:
                summary[alg]['gap_mean'] = sum(gaps) / len(gaps)
        
        return summary
    
    def print_summary(self, results=None):
        """Imprime resumo formatado."""
        summary = self.generate_summary(results)
        
        print("\n" + "=" * 80)
        print("RESUMO DOS EXPERIMENTOS")
        print("=" * 80)
        print(f"{'Algoritmo':<25} {'Valor Médio':>12} {'± Std':>8} "
              f"{'Tempo (ms)':>12} {'Gap %':>8}")
        print("-" * 80)
        
        # Ordena por valor médio (maior primeiro)
        for alg in sorted(summary.keys(), 
                         key=lambda x: -summary[x]['value_mean']):
            s = summary[alg]
            gap = f"{s.get('gap_mean', 0):.2f}" if 'gap_mean' in s else "N/A"
            print(f"{alg:<25} {s['value_mean']:>12.1f} {s['value_std']:>8.1f} "
                  f"{s['time_mean']*1000:>12.2f} {gap:>8}")
        
        print("=" * 80)


# =====================================================
# FUNÇÕES DE CONVENIÊNCIA
# =====================================================

def create_test_algorithms():
    """
    Cria dicionário com todos os algoritmos para teste.
    
    Retorna:
    --------
    dict
        Dicionário {nome: (função, parâmetros)}.
    """
    heuristics = get_default_heuristics()
    
    return {
        # Heurísticas puras
        'Greedy_Value': (greedy_value, {}),
        'Greedy_Weight': (greedy_weight, {}),
        'Greedy_Ratio': (greedy_ratio, {}),
        
        # Metaheurísticas
        'SA': (simulated_annealing, {
            'initial_temp': 500,
            'cooling_rate': 0.95,
            'iterations_per_temp': 30
        }),
        'HC_Restart': (hill_climbing_restart, {
            'num_restarts': 10,
            'max_iter_per_run': 50
        }),
        'GRASP': (grasp, {
            'max_iterations': 50,
            'alpha': 0.3
        }),
        
        # Hiperheurísticas
        'HH_Roulette': (
            lambda inst, **kw: RouletteWheelHH(heuristics).solve(inst, iterations=100),
            {}
        ),
        'HH_EpsilonGreedy': (
            lambda inst, **kw: EpsilonGreedyHH(heuristics, epsilon=0.4).solve(inst, iterations=100),
            {}
        ),
        'HH_RL': (
            lambda inst, **kw: ReinforcementLearningHH(heuristics).solve(inst, iterations=100),
            {}
        ),
        'HH_Adaptive': (
            lambda inst, **kw: AdaptiveHyperHeuristic(heuristics).solve(inst, iterations=150),
            {}
        ),
    }


def run_full_experiment(instances, output_prefix="experiment", 
                        num_runs=10, verbose=True):
    """
    Executa experimento completo em múltiplas instâncias.
    
    Parâmetros:
    -----------
    instances : list[KnapsackInstance]
        Lista de instâncias.
    output_prefix : str
        Prefixo para arquivos de saída.
    num_runs : int
        Execuções por algoritmo por instância.
    verbose : bool
        Se True, imprime progresso.
    
    Retorna:
    --------
    ExperimentRunner
        Objeto com todos os resultados.
    """
    runner = ExperimentRunner()
    algorithms = create_test_algorithms()
    
    for i, instance in enumerate(instances):
        if verbose:
            print(f"\n{'='*60}")
            print(f"INSTÂNCIA {i+1}/{len(instances)}: {instance.n} itens")
            print(f"{'='*60}")
        
        runner.run_comparison(instance, algorithms, num_runs=num_runs, verbose=verbose)
    
    # Salva resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    runner.save_to_csv(f"{output_prefix}_{timestamp}.csv")
    runner.save_to_json(f"{output_prefix}_{timestamp}.json")
    
    # Imprime resumo
    runner.print_summary()
    
    return runner


# =====================================================
# GERADOR DE INSTÂNCIAS
# =====================================================

def generate_random_instance(n, capacity_ratio=0.5, seed=None):
    """
    Gera uma instância aleatória do problema da mochila.
    
    Parâmetros:
    -----------
    n : int
        Número de itens.
    capacity_ratio : float
        Capacidade como fração do peso total.
    seed : int
        Seed para reprodutibilidade.
    
    Retorna:
    --------
    KnapsackInstance
        Instância gerada.
    """
    if seed is not None:
        random.seed(seed)
    
    # Gera pesos e valores aleatórios
    weights = [random.randint(1, 100) for _ in range(n)]
    values = [random.randint(1, 100) for _ in range(n)]
    
    # Capacidade como fração do peso total
    capacity = int(sum(weights) * capacity_ratio)
    
    return KnapsackInstance(capacity, weights, values)


def generate_correlated_instance(n, capacity_ratio=0.5, seed=None):
    """
    Gera instância com valores correlacionados aos pesos.
    
    Instancias correlacionadas sao mais dificeis!
    Quando valor ≈ peso, é difícil decidir o que levar.
    """
    if seed is not None:
        random.seed(seed)
    
    weights = [random.randint(1, 100) for _ in range(n)]
    # Valores correlacionados: valor ≈ peso + ruído
    values = [w + random.randint(-10, 10) for w in weights]
    values = [max(1, v) for v in values]  # Garante positivo
    
    capacity = int(sum(weights) * capacity_ratio)
    
    return KnapsackInstance(capacity, weights, values)


# =====================================================
# CÓDIGO DE TESTE
# =====================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DO MÓDULO DE EXPERIMENTAÇÃO")
    print("=" * 60)
    
    # Gera instâncias de teste
    print("\n[INFO] Gerando instancias de teste...")
    instances = [
        generate_random_instance(20, seed=42),   # Pequena
        generate_random_instance(50, seed=43),   # Média
        generate_random_instance(100, seed=44),  # Grande
    ]
    
    for i, inst in enumerate(instances):
        print(f"  Instância {i+1}: {inst.n} itens, capacidade={inst.capacity}")
    
    # Executa experimento rápido (poucas execuções para teste)
    print("\n[TESTE] Executando experimento de teste...")
    runner = run_full_experiment(
        instances[:1],  # Só primeira instância para teste rápido
        output_prefix="test_experiment",
        num_runs=3,
        verbose=True
    )
    
    print("\n[OK] Teste concluido!")
    print(f"   Resultados salvos em: {runner.output_dir}/")

