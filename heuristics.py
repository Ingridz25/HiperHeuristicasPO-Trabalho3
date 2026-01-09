"""
===========================================================
MÓDULO: heuristics.py
Heurísticas de Baixo Nível para o Problema da Mochila
===========================================================

Este módulo contém TODAS as heurísticas exigidas para o trabalho:

HEURISTICAS CONSTRUTIVAS (criam solucoes do zero):
  - greedy_value()     -> Prioriza itens com MAIOR VALOR
  - greedy_weight()    -> Prioriza itens com MENOR PESO
  - greedy_ratio()     -> Prioriza itens com MELHOR razao valor/peso
  - greedy_random()    -> Construcao semi-aleatoria (para GRASP)

HEURISTICAS DE MELHORIA (melhoram solucoes existentes):
  - local_search_1flip()  -> Testa inverter cada item
  - local_search_2swap()  -> Troca um item dentro por um fora
  - remove_worst()        -> Remove item com pior custo-beneficio

CONCEITO: Heuristicas Construtivas vs. de Melhoria
-----------------------------------------------------
Construtivas: Constroem uma solução "do zero", item por item.
De Melhoria: Recebem uma solução e tentam melhorá-la.

A ideia é usar construtivas para gerar uma solução inicial,
depois aplicar as de melhoria para refinar.
"""

import random
from solution import Solution


# =====================================================
# HEURÍSTICAS CONSTRUTIVAS
# =====================================================

def greedy_value(instance):
    """
    Heurística Gulosa por VALOR.
    
    ESTRATEGIA: "Quero os itens mais valiosos!"
    
    Ordena os itens do mais valioso ao menos valioso.
    Para cada item (em ordem), adiciona se couber na mochila.
    
    LIMITACAO: Pode pegar um item muito valioso mas pesado,
    deixando espaço insuficiente para vários itens menores que
    juntos teriam valor maior.
    
    Parâmetros:
    -----------
    instance : KnapsackInstance
        Instância do problema.
    
    Retorna:
    --------
    Solution
        Solução construída pela heurística.
    
    Complexidade: O(n log n) - dominado pela ordenação
    """
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
    """
    Heurística Gulosa por PESO (menor peso primeiro).
    
    ESTRATEGIA: "Quero caber o maximo de itens possivel!"
    
    Ordena os itens do mais leve ao mais pesado.
    Adiciona itens enquanto couberem.
    
    Esta estrategia tende a colocar MUITOS itens na mochila,
    o que pode ser bom se os valores são similares.
    
    LIMITACAO: Pode pegar muitos itens leves de baixo valor,
    ignorando um item pesado mas muito valioso.
    
    Parâmetros:
    -----------
    instance : KnapsackInstance
        Instância do problema.
    
    Retorna:
    --------
    Solution
        Solução construída pela heurística.
    
    Complexidade: O(n log n)
    """
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
    """
    Heurística Gulosa por RAZÃO VALOR/PESO.
    
    ESTRATEGIA: "Quero o melhor custo-beneficio!"
    
    Esta é geralmente a MELHOR heurística gulosa para a mochila.
    Prioriza itens que dão mais "valor por quilo".
    
    CONCEITO: A razao valor/peso representa a "eficiencia"
    de cada item. Um item com razão 2.0 dá 2 unidades de valor
    para cada unidade de peso que ocupa.
    
    Parâmetros:
    -----------
    instance : KnapsackInstance
        Instância do problema.
    
    Retorna:
    --------
    Solution
        Solução construída pela heurística.
    
    Complexidade: O(n log n)
    """
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
    """
    Heurística Gulosa Aleatorizada (Semi-Greedy / GRASP Construction).
    
    ESTRATEGIA: "Escolho entre os melhores, mas com aleatoriedade!"
    
    Em vez de sempre pegar o "melhor" item, escolhe aleatoriamente
    entre os melhores candidatos (Lista Restrita de Candidatos - RCL).
    
    CONCEITO: Esta aleatoriedade controlada permite gerar
    soluções DIFERENTES a cada execução, o que é essencial
    para metaheurísticas como GRASP.
    
    Parâmetros:
    -----------
    instance : KnapsackInstance
        Instância do problema.
    alpha : float
        Parâmetro de aleatoriedade (0 a 1):
        - alpha=0: Totalmente guloso (sem aleatoriedade)
        - alpha=1: Totalmente aleatório
        - Valor recomendado: 0.2 a 0.4
    
    Retorna:
    --------
    Solution
        Solução construída pela heurística.
    
    Complexidade: O(n²) - pois recalcula candidatos a cada inserção
    """
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


# =====================================================
# HEURÍSTICAS DE MELHORIA (Busca Local)
# =====================================================

def local_search_1flip(solution):
    """
    Busca Local com movimento 1-Flip.
    
    ESTRATEGIA: "E se eu inverter UM item?"
    
    Testa inverter cada item:
    - Se item está na mochila → remove
    - Se item está fora → adiciona (se couber)
    
    Retorna a PRIMEIRA melhoria encontrada (First Improvement).
    
    CONCEITO: Vizinhanca
    -----------------------
    A "vizinhanca" de uma solucao sao todas as solucoes que
    podemos alcançar com UM movimento. Aqui, o movimento é
    inverter um bit (0→1 ou 1→0).
    
    Parâmetros:
    -----------
    solution : Solution
        Solução atual a ser melhorada.
    
    Retorna:
    --------
    Solution
        Melhor vizinho encontrado (ou a própria solução se não melhorou).
    
    Complexidade: O(n)
    """
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
    """
    Busca Local 1-Flip com Best Improvement.
    
    Diferença para a anterior: testa TODOS os vizinhos
    e retorna o MELHOR de todos.
    
    Parâmetros:
    -----------
    solution : Solution
        Solução atual a ser melhorada.
    
    Retorna:
    --------
    Solution
        Melhor vizinho encontrado.
    
    Complexidade: O(n)
    """
    best = solution.copy()
    
    for i in range(solution.instance.n):
        candidate = solution.copy()
        candidate.flip_item(i)
        
        if candidate.is_feasible() and candidate.value > best.value:
            best = candidate
            # Não retorna aqui - continua testando todos
    
    return best


def local_search_2swap(solution):
    """
    Busca Local com movimento 2-Swap (troca).
    
    ESTRATEGIA: "E se eu trocar um item dentro por um fora?"
    
    Remove um item que está na mochila e adiciona outro
    que estava fora. Isso permite escapar de situações onde
    1-flip não consegue melhorar.
    
    CONCEITO: Vizinhanca mais ampla
    ----------------------------------
    A vizinhança do 2-swap é MAIOR que a do 1-flip.
    Isso significa mais chances de encontrar melhorias,
    mas também mais tempo de computação.
    
    Parâmetros:
    -----------
    solution : Solution
        Solução atual a ser melhorada.
    
    Retorna:
    --------
    Solution
        Melhor vizinho encontrado.
    
    Complexidade: O(n²) - testa todos os pares
    """
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
    """
    Remove o item com PIOR razão valor/peso.
    
    ESTRATEGIA: "Quem esta ocupando espaco sem merecer?"
    
    Identifica o item na mochila que tem a pior razão valor/peso
    e o remove. Isso libera capacidade para potencialmente
    adicionar itens melhores depois.
    
    ATENCAO: Esta heuristica sempre PIORA o valor imediato!
    Ela deve ser usada como parte de uma estratégia maior
    (como no Simulated Annealing) que permite pioras temporárias.
    
    Parâmetros:
    -----------
    solution : Solution
        Solução atual.
    
    Retorna:
    --------
    Solution
        Solução com um item a menos.
    """
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
    """
    Tenta preencher a capacidade restante com itens viáveis.
    
    ESTRATEGIA: "Sobrou espaco? Vamos aproveitar!"
    
    Ordena itens não selecionados por razão valor/peso
    e adiciona enquanto couber.
    
    Parâmetros:
    -----------
    solution : Solution
        Solução atual.
    
    Retorna:
    --------
    Solution
        Solução com capacidade melhor utilizada.
    """
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


# =====================================================
# CONJUNTO DE HEURÍSTICAS PARA HIPERHEURÍSTICA
# =====================================================

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


# =====================================================
# CÓDIGO DE TESTE
# =====================================================
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

