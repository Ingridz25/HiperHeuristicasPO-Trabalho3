"""
Heurísticas construtivas e de melhoria para o problema da mochila.
"""

import random
from solution import Solution


def greedy_value(instance):

    sol = Solution(instance)
    
    # Ordena índices dos itens por valor DECRESCENTE
    # sorted() retorna nova lista, não modifica a original
    # key= define o critério de ordenação
    # reverse=True coloca os maiores primeiro
    order = sorted(
        range(instance.n),
        key=lambda i: instance.values[i],
        reverse=True
    )
    
    # Tenta adicionar cada item na ordem de prioridade
    for i in order:
        sol.items[i] = 1
        sol.evaluate()
        
        # Se ultrapassou capacidade, remove o item
        if not sol.is_feasible():
            sol.items[i] = 0
    
    sol.evaluate()
    return sol


def greedy_weight(instance):

    sol = Solution(instance)
    
    # Ordena por peso CRESCENTE (mais leves primeiro)
    order = sorted(
        range(instance.n),
        key=lambda i: instance.weights[i],
        reverse=False  # False = ordem crescente
    )
    
    for i in order:
        sol.items[i] = 1
        sol.evaluate()
        
        if not sol.is_feasible():
            sol.items[i] = 0
    
    sol.evaluate()
    return sol


def greedy_ratio(instance):

    sol = Solution(instance)
    
    # Ordena por razão valor/peso DECRESCENTE
    order = sorted(
        range(instance.n),
        key=lambda i: instance.get_ratio(i),
        reverse=True
    )
    
    for i in order:
        sol.items[i] = 1
        sol.evaluate()
        
        if not sol.is_feasible():
            sol.items[i] = 0
    
    sol.evaluate()
    return sol


def greedy_random(instance, alpha=0.3):

    sol = Solution(instance)
    
    # Lista de itens ainda não decididos
    candidates = list(range(instance.n))
    
    while candidates:
        # Filtra candidatos que cabem na mochila
        viable = []
        for i in candidates:
            if instance.weights[i] <= sol.remaining_capacity():
                viable.append(i)
        
        if not viable:
            break  # Nenhum item cabe mais
        
        # Calcula razão de cada candidato viável
        ratios = {i: instance.get_ratio(i) for i in viable}
        
        # Define limites da RCL (Lista Restrita de Candidatos)
        max_ratio = max(ratios.values())
        min_ratio = min(ratios.values())
        threshold = max_ratio - alpha * (max_ratio - min_ratio)
        
        # RCL contém candidatos com razão >= threshold
        rcl = [i for i in viable if ratios[i] >= threshold]
        
        # Escolhe aleatoriamente da RCL
        chosen = random.choice(rcl)
        
        # Adiciona o item escolhido (verificando viabilidade)
        sol.items[chosen] = 1
        sol.evaluate()
        
        # Se ultrapassou capacidade, remove o item
        if not sol.is_feasible():
            sol.items[chosen] = 0
            sol.evaluate()
        
        candidates.remove(chosen)
    
    sol.evaluate()
    return sol



def local_search_1flip(solution):

    best = solution.copy()
    
    for i in range(solution.instance.n):
        # Cria candidato invertendo item i
        candidate = solution.copy()
        candidate.flip_item(i)
        
        # Aceita se: é viável E é melhor que o atual
        if candidate.is_feasible() and candidate.value > best.value:
            best = candidate
            # First Improvement: retorna assim que acha melhoria
            # (Pode trocar por Best Improvement se quiser testar todos)
    
    return best


def local_search_1flip_best(solution):

    best = solution.copy()
    
    for i in range(solution.instance.n):
        candidate = solution.copy()
        candidate.flip_item(i)
        
        if candidate.is_feasible() and candidate.value > best.value:
            best = candidate
            # Não retorna aqui - continua testando todos
    
    return best


def local_search_2swap(solution):

    best = solution.copy()
    
    # Identifica itens dentro e fora da mochila
    inside = solution.get_selected_items()
    outside = solution.get_unselected_items()
    
    # Tenta cada combinação de (remover um, adicionar outro)
    for i_out in inside:  # Item a remover
        for i_in in outside:  # Item a adicionar
            candidate = solution.copy()
            
            # Remove item i_out, adiciona item i_in
            candidate.items[i_out] = 0
            candidate.items[i_in] = 1
            candidate.evaluate()
            
            # Verifica se é viável e melhor
            if candidate.is_feasible() and candidate.value > best.value:
                best = candidate
    
    return best


def remove_worst(solution):

    inside = solution.get_selected_items()
    
    if not inside:
        return solution.copy()  # Nada a remover
    
    # Encontra item com pior razão
    worst = min(inside, key=lambda i: solution.instance.get_ratio(i))
    
    # Remove o pior item
    result = solution.copy()
    result.items[worst] = 0
    result.evaluate()
    
    return result


def fill_remaining(solution):

    result = solution.copy()
    outside = result.get_unselected_items()
    
    # Ordena candidatos por razão (melhores primeiro)
    outside.sort(
        key=lambda i: result.instance.get_ratio(i),
        reverse=True
    )
    
    # Tenta adicionar cada candidato
    for i in outside:
        result.add_item(i)  # add_item já verifica viabilidade
    
    return result

def get_constructive_heuristics():
    """
    Retorna lista de todas as heurísticas construtivas.
    
    Cada heurística é uma função que recebe instance e retorna Solution.
    """
    return [
        greedy_value,
        greedy_weight,
        greedy_ratio,
        greedy_random,
    ]


def get_improvement_heuristics():
    """
    Retorna lista de todas as heurísticas de melhoria.
    
    Cada heurística é uma função que recebe Solution e retorna Solution.
    """
    return [
        local_search_1flip,
        local_search_1flip_best,
        local_search_2swap,
        remove_worst,
        fill_remaining,
    ]


def get_all_heuristics_info():
    """
    Retorna informações sobre todas as heurísticas.
    
    Útil para logging e análise do comportamento da hiperheurística.
    """
    return {
        'greedy_value': 'Gulosa por Valor',
        'greedy_weight': 'Gulosa por Peso',
        'greedy_ratio': 'Gulosa por Razão',
        'greedy_random': 'Gulosa Aleatorizada',
        'local_search_1flip': 'Busca Local 1-Flip',
        'local_search_1flip_best': 'Busca Local 1-Flip (Best)',
        'local_search_2swap': 'Busca Local 2-Swap',
        'remove_worst': 'Remove Pior',
        'fill_remaining': 'Preenche Capacidade',
    }

if __name__ == "__main__":
    from instance import KnapsackInstance
    
    # Cria instância de teste
    inst = KnapsackInstance(
        capacity=15,
        weights=[5, 3, 4, 6, 2, 7, 1],
        values=[10, 7, 8, 9, 3, 12, 2]
    )
    
    print("=" * 60)
    print("TESTE DAS HEURÍSTICAS CONSTRUTIVAS")
    print("=" * 60)
    
    print(f"\n[INFO] Instancia: capacidade={inst.capacity}, {inst.n} itens")
    print(f"   Pesos: {inst.weights}")
    print(f"   Valores: {inst.values}")
    
    print("\n--- Resultados ---")
    
    sol_value = greedy_value(inst)
    print(f"Greedy Valor:  valor={sol_value.value:3d}, peso={sol_value.weight:2d}, itens={sol_value.get_selected_items()}")
    
    sol_weight = greedy_weight(inst)
    print(f"Greedy Peso:   valor={sol_weight.value:3d}, peso={sol_weight.weight:2d}, itens={sol_weight.get_selected_items()}")
    
    sol_ratio = greedy_ratio(inst)
    print(f"Greedy Razão:  valor={sol_ratio.value:3d}, peso={sol_ratio.weight:2d}, itens={sol_ratio.get_selected_items()}")
    
    sol_random = greedy_random(inst)
    print(f"Greedy Random: valor={sol_random.value:3d}, peso={sol_random.weight:2d}, itens={sol_random.get_selected_items()}")
    
    print("\n" + "=" * 60)
    print("TESTE DAS HEURÍSTICAS DE MELHORIA")
    print("=" * 60)
    
    print(f"\nSolução inicial (greedy_ratio): {sol_ratio}")
    
    improved_1flip = local_search_1flip(sol_ratio)
    print(f"Após 1-Flip:    {improved_1flip}")
    
    improved_2swap = local_search_2swap(sol_ratio)
    print(f"Após 2-Swap:    {improved_2swap}")
    
    print("\n[OK] Todos os testes executados!")

