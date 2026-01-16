"""
Metaheurísticas para o problema da mochila.
"""

import random
import math
from solution import Solution, create_random_solution
from heuristics import (
    greedy_ratio, greedy_random,
    local_search_1flip, local_search_1flip_best,
    local_search_2swap, fill_remaining
)


def hill_climbing(initial_solution, max_iterations=100, verbose=False):

    current = initial_solution.copy()
    
    for iteration in range(max_iterations):
        # Aplica busca local
        neighbor = local_search_1flip_best(current)
        
        if neighbor.value > current.value:
            current = neighbor
            if verbose:
                print(f"  Iteração {iteration}: valor={current.value}")
        else:
            # Não encontrou vizinho melhor - ótimo local atingido
            break
    
    return current


def hill_climbing_restart(instance, num_restarts=10, max_iter_per_run=100, verbose=False):

    best_overall = None
    
    for restart in range(num_restarts):
        # Gera solução inicial aleatória
        initial = create_random_solution(instance)
        
        if verbose:
            print(f"Reinício {restart + 1}/{num_restarts}: inicial={initial.value}")
        
        # Aplica Hill Climbing
        result = hill_climbing(initial, max_iter_per_run, verbose=False)
        
        if verbose:
            print(f"  → Final: {result.value}")
        
        # Atualiza melhor global
        if best_overall is None or result.value > best_overall.value:
            best_overall = result
    
    return best_overall


def simulated_annealing(instance, 
                        initial_temp=1000, 
                        cooling_rate=0.95,
                        min_temp=1,
                        iterations_per_temp=50,
                        verbose=False):

    # Solução inicial: usa heurística gulosa para ter bom ponto de partida
    current = greedy_ratio(instance)
    
    # Melhor solução encontrada até agora
    best = current.copy()
    
    # Temperatura atual
    temperature = initial_temp
    
    # Contadores para análise
    total_iterations = 0
    accepted_worse = 0  # Quantas vezes aceitou piora
    
    if verbose:
        print(f"SA Iniciado: temp_inicial={initial_temp}, cooling={cooling_rate}")
        print(f"Solução inicial: valor={current.value}")
    
    # Loop principal: enquanto não esfriar demais
    while temperature > min_temp:
        
        for _ in range(iterations_per_temp):
            total_iterations += 1
            
            # Gera vizinho: escolhe aleatoriamente entre movimentos
            neighbor = generate_neighbor(current)
            
            # IMPORTANTE: So aceita vizinhos VIAVEIS!
            if not neighbor.is_feasible():
                continue  # Ignora vizinhos inviaveis
            
            # Calcula diferenca de qualidade (delta)
            # Delta > 0 significa que vizinho e MELHOR
            delta = neighbor.value - current.value
            
            # Decide se aceita o movimento
            if delta > 0:
                # Vizinho e melhor -> aceita sempre!
                current = neighbor
            else:
                # Vizinho e pior -> aceita com probabilidade
                # Formula: P(aceitar) = e^(delta/temperatura)
                # Quanto maior a temperatura, maior a probabilidade
                probability = math.exp(delta / temperature)
                
                if random.random() < probability:
                    current = neighbor
                    accepted_worse += 1
            
            # Atualiza melhor global (so se viavel - dupla verificacao)
            if current.is_feasible() and current.value > best.value:
                best = current.copy()
        
        # Resfriamento: diminui a temperatura
        temperature *= cooling_rate
        
        if verbose and total_iterations % 500 == 0:
            print(f"  Temp={temperature:.2f}, atual={current.value}, melhor={best.value}")
    
    if verbose:
        print(f"SA Finalizado: {total_iterations} iterações")
        print(f"  Aceitou {accepted_worse} pioras")
        print(f"  Melhor valor: {best.value}")
    
    return best


def generate_neighbor(solution):

    neighbor = solution.copy()
    
    # Escolhe tipo de movimento
    move_type = random.choice(['flip', 'swap', 'swap'])  # Swap é mais provável
    
    if move_type == 'flip':
        # Inverte um item aleatório
        i = random.randint(0, solution.instance.n - 1)
        neighbor.flip_item(i)
    
    else:  # swap
        inside = neighbor.get_selected_items()
        outside = neighbor.get_unselected_items()
        
        if inside and outside:
            # Troca um de dentro por um de fora
            i_out = random.choice(inside)
            i_in = random.choice(outside)
            neighbor.items[i_out] = 0
            neighbor.items[i_in] = 1
            neighbor.evaluate()
        else:
            # Fallback: flip
            i = random.randint(0, solution.instance.n - 1)
            neighbor.flip_item(i)
    
    return neighbor



def grasp(instance, max_iterations=100, alpha=0.3, verbose=False):

    best = None
    
    for iteration in range(max_iterations):
        # FASE 1: Construção aleatorizada
        solution = greedy_random(instance, alpha=alpha)
        
        # FASE 2: Busca local
        solution = local_search_1flip_best(solution)
        solution = local_search_2swap(solution)
        solution = fill_remaining(solution)
        
        # Atualiza melhor
        if best is None or solution.value > best.value:
            best = solution.copy()
            if verbose:
                print(f"GRASP Iter {iteration}: novo melhor = {best.value}")
    
    return best


def run_metaheuristic(name, instance, **kwargs):

    if name == 'sa' or name == 'simulated_annealing':
        return simulated_annealing(instance, **kwargs)
    
    elif name == 'hc_restart' or name == 'hill_climbing_restart':
        return hill_climbing_restart(instance, **kwargs)
    
    elif name == 'grasp':
        return grasp(instance, **kwargs)
    
    else:
        raise ValueError(f"Metaheurística desconhecida: {name}")


if __name__ == "__main__":
    from instance import KnapsackInstance
    
    # Cria instância de teste
    inst = KnapsackInstance(
        capacity=50,
        weights=[10, 20, 30, 40, 25, 15, 35, 45, 5, 12],
        values=[60, 100, 120, 150, 90, 50, 130, 180, 30, 70]
    )
    
    print("=" * 60)
    print("TESTE DAS METAHEURÍSTICAS")
    print("=" * 60)
    print(f"\nInstância: {inst.n} itens, capacidade={inst.capacity}")
    
    # Baseline: heurística simples
    baseline = greedy_ratio(inst)
    print(f"\n[BASELINE] Baseline (Greedy Ratio): valor={baseline.value}")
    
    # Teste Hill Climbing com Reinício
    print("\n--- Hill Climbing com Reinício ---")
    result_hc = hill_climbing_restart(inst, num_restarts=5, verbose=True)
    print(f"Resultado HC: valor={result_hc.value}")
    
    # Teste Simulated Annealing
    print("\n--- Simulated Annealing ---")
    result_sa = simulated_annealing(
        inst,
        initial_temp=500,
        cooling_rate=0.95,
        iterations_per_temp=30,
        verbose=True
    )
    print(f"Resultado SA: valor={result_sa.value}")
    
    # Teste GRASP
    print("\n--- GRASP ---")
    result_grasp = grasp(inst, max_iterations=50, alpha=0.3, verbose=False)
    print(f"Resultado GRASP: valor={result_grasp.value}")
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Greedy Ratio:  {baseline.value}")
    print(f"HC Restart:    {result_hc.value}")
    print(f"SA:            {result_sa.value}")
    print(f"GRASP:         {result_grasp.value}")
    
    winner = max([baseline, result_hc, result_sa, result_grasp], key=lambda s: s.value)
    print(f"\n[MELHOR] Melhor: {winner.value}")

