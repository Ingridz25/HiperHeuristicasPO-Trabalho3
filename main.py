import argparse
import os
import sys

# Importações dos módulos do projeto
from instance import KnapsackInstance
from solution import Solution, create_random_solution
from heuristics import (
    greedy_value, greedy_weight, greedy_ratio, greedy_random,
    local_search_1flip, local_search_2swap, fill_remaining
)
from metaheuristic import (
    simulated_annealing, hill_climbing_restart, grasp
)
from hyperheuristic import (
    RouletteWheelHH, EpsilonGreedyHH, ReinforcementLearningHH,
    AdaptiveHyperHeuristic, get_default_heuristics
)
from experiments import (
    ExperimentRunner, generate_random_instance, run_full_experiment
)

# DEMONSTRACAO COMPLETA

def run_demo():
    print("=" * 70)
    print("   DEMONSTRACAO: HIPERHEURISTICA PARA O PROBLEMA DA MOCHILA")
    print("=" * 70)
    
    # ===== ETAPA 1: Criar/Carregar Instancia =====
    print("\n" + "=" * 70)
    print("ETAPA 1: CRIACAO DA INSTANCIA")
    print("=" * 70)
    
    # Verifica se existe instancia de exemplo
    instance_path = "instances/pequena_10.txt"
    if os.path.exists(instance_path):
        print(f"\n[ARQUIVO] Carregando instancia de: {instance_path}")
        instance = KnapsackInstance.from_file(instance_path)
    else:
        print("\n[GERANDO] Gerando instancia aleatoria (10 itens)...")
        instance = generate_random_instance(10, seed=42)
    
    print(f"\n[INFO] INSTANCIA CARREGADA:")
    print(f"   * Numero de itens: {instance.n}")
    print(f"   * Capacidade da mochila: {instance.capacity}")
    print(f"   * Peso total disponivel: {sum(instance.weights)}")
    print(f"   * Valor total disponivel: {sum(instance.values)}")
    
    print("\n   Detalhes dos itens:")
    print(f"   {'Item':<6} {'Peso':<8} {'Valor':<8} {'Razao':<8}")
    print("   " + "-" * 32)
    for i in range(min(instance.n, 10)):  # Mostra ate 10 itens
        ratio = instance.get_ratio(i)
        print(f"   {i:<6} {instance.weights[i]:<8} {instance.values[i]:<8} {ratio:<8.2f}")
    if instance.n > 10:
        print(f"   ... e mais {instance.n - 10} itens")
    
    # ===== ETAPA 2: Heuristicas Construtivas =====
    print("\n" + "=" * 70)
    print("ETAPA 2: HEURISTICAS CONSTRUTIVAS")
    print("=" * 70)
    
    print("\n[CONCEITO] Heuristicas construtivas criam solucoes 'do zero',")
    print("           adicionando itens um por um seguindo algum criterio.\n")
    
    heuristics = [
        ("Greedy por Valor", greedy_value, "Pega os itens mais valiosos primeiro"),
        ("Greedy por Peso", greedy_weight, "Pega os itens mais leves primeiro"),
        ("Greedy por Razao", greedy_ratio, "Pega os itens com melhor custo-beneficio"),
        ("Greedy Aleatorizada", greedy_random, "Escolhe semi-aleatoriamente entre os melhores"),
    ]
    
    best_heuristic = None
    best_solution = None
    
    for name, func, description in heuristics:
        solution = func(instance)
        print(f"   [RESULTADO] {name}:")
        print(f"      Descricao: {description}")
        print(f"      Valor: {solution.value}, Peso: {solution.weight}/{instance.capacity}")
        print(f"      Itens: {solution.get_selected_items()}\n")
        
        if best_solution is None or solution.value > best_solution.value:
            best_solution = solution
            best_heuristic = name
    
    print(f"   [MELHOR] Melhor heuristica construtiva: {best_heuristic} (valor={best_solution.value})")
    
    # ===== ETAPA 3: Heuristicas de Melhoria =====
    print("\n" + "=" * 70)
    print("ETAPA 3: HEURISTICAS DE MELHORIA (BUSCA LOCAL)")
    print("=" * 70)
    
    print("\n[CONCEITO] Heuristicas de melhoria recebem uma solucao e")
    print("           tentam melhora-la fazendo pequenas modificacoes.\n")
    
    initial = greedy_ratio(instance)
    print(f"   Solucao inicial (greedy_ratio): valor={initial.value}")
    
    improved = local_search_1flip(initial)
    print(f"   Apos 1-Flip: valor={improved.value}")
    
    improved = local_search_2swap(improved)
    print(f"   Apos 2-Swap: valor={improved.value}")
    
    improved = fill_remaining(improved)
    print(f"   Apos Fill Remaining: valor={improved.value}")
    
    # ===== ETAPA 4: Metaheuristicas =====
    print("\n" + "=" * 70)
    print("ETAPA 4: METAHEURISTICAS")
    print("=" * 70)
    
    print("\n[CONCEITO] Metaheuristicas sao estrategias de alto nivel que")
    print("           controlam heuristicas para explorar melhor o espaco de busca.\n")
    
    print("   [SA] Simulated Annealing:")
    print("        Aceita pioras temporarias para escapar de otimos locais.")
    sa_result = simulated_annealing(
        instance, 
        initial_temp=500, 
        cooling_rate=0.95,
        iterations_per_temp=20,
        verbose=False
    )
    print(f"        Resultado: valor={sa_result.value}")
    
    print("\n   [HC] Hill Climbing com Reinicio:")
    print("        Executa multiplas vezes de pontos diferentes.")
    hc_result = hill_climbing_restart(instance, num_restarts=5, max_iter_per_run=30)
    print(f"        Resultado: valor={hc_result.value}")
    
    print("\n   [GRASP] GRASP:")
    print("           Construcao aleatorizada + busca local, repetido varias vezes.")
    grasp_result = grasp(instance, max_iterations=30, alpha=0.3)
    print(f"           Resultado: valor={grasp_result.value}")
    
    # ===== ETAPA 5: Hiperheuristicas =====
    print("\n" + "=" * 70)
    print("ETAPA 5: HIPERHEURISTICAS")
    print("=" * 70)
    
    print("\n[CONCEITO] Hiperheuristicas sao 'algoritmos de selecao de algoritmos'.")
    print("           Elas aprendem quais heuristicas funcionam melhor e adaptam suas escolhas!")
    
    heuristics_list = get_default_heuristics()
    
    print("\n   [ROLETA] Roleta Ponderada:")
    print("            Seleciona heuristicas proporcionalmente ao seu desempenho.")
    hh_roulette = RouletteWheelHH(heuristics_list)
    roulette_result = hh_roulette.solve(instance, iterations=80, verbose=False)
    print(f"            Resultado: valor={roulette_result.value}")
    
    print("\n   [EPSILON] Epsilon-Greedy:")
    print("             Balanceia exploracao (tentar novas) vs exploitacao (usar as melhores).")
    hh_epsilon = EpsilonGreedyHH(heuristics_list, epsilon=0.3)
    epsilon_result = hh_epsilon.solve(instance, iterations=80, verbose=False)
    print(f"             Resultado: valor={epsilon_result.value}")
    
    print("\n   [RL] Aprendizado por Reforco:")
    print("        Aprende 'Q-values' baseado em recompensas de cada heuristica.")
    hh_rl = ReinforcementLearningHH(heuristics_list)
    rl_result = hh_rl.solve(instance, iterations=80, verbose=False)
    print(f"        Resultado: valor={rl_result.value}")
    
    print("\n   [ADAPTATIVA] Hiperheuristica Adaptativa (Completa):")
    print("                Combina epsilon-greedy, RL e reinicio automatico.")
    hh_adaptive = AdaptiveHyperHeuristic(heuristics_list)
    adaptive_result = hh_adaptive.solve(instance, iterations=100, verbose=False)
    print(f"                Resultado: valor={adaptive_result.value}")
    
    # ===== RESUMO FINAL =====
    print("\n" + "=" * 70)
    print("RESUMO COMPARATIVO")
    print("=" * 70)
    
    results = [
        ("Greedy Ratio", best_solution.value),
        ("Simulated Annealing", sa_result.value),
        ("Hill Climbing Restart", hc_result.value),
        ("GRASP", grasp_result.value),
        ("HH Roleta", roulette_result.value),
        ("HH Epsilon-Greedy", epsilon_result.value),
        ("HH RL", rl_result.value),
        ("HH Adaptativa", adaptive_result.value),
    ]
    
    print(f"\n   {'Algoritmo':<25} {'Valor':>10}")
    print("   " + "-" * 37)
    
    sorted_results = sorted(results, key=lambda x: -x[1])
    for name, value in sorted_results:
        marker = "[MELHOR]" if value == sorted_results[0][1] else "        "
        print(f"   {marker} {name:<23} {value:>10}")
    
    # Estatisticas da hiperheuristica adaptativa
    print("\n" + "=" * 70)
    print("ANALISE DO COMPORTAMENTO ADAPTATIVO")
    print("=" * 70)
    hh_adaptive.print_statistics()
    
    print("\n" + "=" * 70)
    print("[OK] DEMONSTRACAO CONCLUIDA!")
    print("=" * 70)


def run_with_instance(instance_path, verbose=True):
    """Executa com uma instancia especifica."""
    print(f"\n[ARQUIVO] Carregando instancia: {instance_path}")
    instance = KnapsackInstance.from_file(instance_path)
    print(f"   {instance.n} itens, capacidade={instance.capacity}")
    
    # Executa algoritmos
    print("\n[EXECUTANDO] Executando algoritmos...")
    
    # Greedy baseline
    greedy = greedy_ratio(instance)
    print(f"   Greedy Ratio: {greedy.value}")
    
    # Simulated Annealing
    sa = simulated_annealing(instance, verbose=verbose)
    print(f"   SA: {sa.value}")
    
    # Hiperheuristica
    hh = AdaptiveHyperHeuristic(get_default_heuristics())
    hh_result = hh.solve(instance, iterations=200, verbose=verbose)
    print(f"   HH Adaptativa: {hh_result.value}")
    
    # Melhor
    best = max([greedy, sa, hh_result], key=lambda s: s.value)
    print(f"\n[MELHOR] Melhor: {best.value}")
    print(f"   Itens: {best.get_selected_items()}")
    
    return best


def run_experiment(num_runs=10, sizes=None):
    """Executa experimento completo."""
    if sizes is None:
        sizes = [10, 20, 50]
    
    print("\n[EXPERIMENTO] EXECUTANDO EXPERIMENTO COMPLETO")
    print(f"   Tamanhos: {sizes}")
    print(f"   Execucoes por algoritmo: {num_runs}")
    
    # Gera instancias
    instances = [generate_random_instance(n, seed=42+n) for n in sizes]
    
    # Executa
    runner = run_full_experiment(
        instances,
        output_prefix="knapsack_experiment",
        num_runs=num_runs,
        verbose=True
    )
    
    return runner

# PONTO DE ENTRADA

def main():
    """Funcao principal."""
    parser = argparse.ArgumentParser(
        description="Hiperheuristica para o Problema da Mochila Binaria"
    )
    parser.add_argument(
        '--instance', '-i',
        type=str,
        help='Caminho para arquivo de instancia'
    )
    parser.add_argument(
        '--experiment', '-e',
        action='store_true',
        help='Executa experimento completo'
    )
    parser.add_argument(
        '--runs', '-r',
        type=int,
        default=10,
        help='Numero de execucoes por algoritmo (padrao: 10)'
    )
    parser.add_argument(
        '--demo', '-d',
        action='store_true',
        help='Executa demonstracao didatica'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose'
    )
    
    args = parser.parse_args()
    
    if args.instance:
        run_with_instance(args.instance, verbose=args.verbose)
    elif args.experiment:
        run_experiment(num_runs=args.runs)
    else:
        # Padrao: executa demo
        run_demo()


if __name__ == "__main__":
    main()
