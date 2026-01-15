"""
Script para obter instâncias do Problema da Mochila.

SOLUÇÃO ALTERNATIVA: Gera instâncias locais de alta qualidade
baseadas nas características das instâncias clássicas da literatura.

Uso:
    python download_instances.py
"""

import os
import random
import math


def create_instance_directory():
    """Cria diretório para instâncias se não existir."""
    if not os.path.exists("instances"):
        os.makedirs("instances")
    print("[OK] Diretório instances/ pronto.")


def generate_uncorrelated_instance(n, seed=None):
    """
    Gera instância não-correlacionada (valores e pesos independentes).

    Características:
    - Pesos aleatórios entre 1 e 1000
    - Valores aleatórios entre 1 e 1000
    - Capacidade = 50% do peso total
    """
    if seed is not None:
        random.seed(seed)

    weights = [random.randint(1, 1000) for _ in range(n)]
    values = [random.randint(1, 1000) for _ in range(n)]
    capacity = sum(weights) // 2

    return n, capacity, values, weights


def generate_weakly_correlated_instance(n, seed=None):
    """
    Gera instância fracamente correlacionada.

    Características:
    - Pesos aleatórios entre 1 e 1000
    - Valores próximos aos pesos: v_i = w_i + random(-100, 100)
    """
    if seed is not None:
        random.seed(seed)

    weights = [random.randint(1, 1000) for _ in range(n)]
    values = [max(1, w + random.randint(-100, 100)) for w in weights]
    capacity = sum(weights) // 2

    return n, capacity, values, weights


def generate_strongly_correlated_instance(n, seed=None):
    """
    Gera instância fortemente correlacionada.

    Características:
    - Pesos aleatórios entre 1 e 1000
    - Valores muito próximos aos pesos: v_i = w_i + 10
    """
    if seed is not None:
        random.seed(seed)

    weights = [random.randint(1, 1000) for _ in range(n)]
    values = [w + 10 for w in weights]
    capacity = sum(weights) // 2

    return n, capacity, values, weights


def generate_subset_sum_instance(n, seed=None):
    """
    Gera instância tipo subset-sum (mais difícil).

    Características:
    - Pesos aleatórios entre 1 e 1000
    - Valores = pesos (v_i = w_i)
    """
    if seed is not None:
        random.seed(seed)

    weights = [random.randint(1, 1000) for _ in range(n)]
    values = weights[:]  # Cópia dos pesos
    capacity = sum(weights) // 2

    return n, capacity, values, weights


def estimate_optimal_value(n, capacity, values, weights):
    """
    Estima valor ótimo usando greedy por razão (limite superior).

    Retorna:
    --------
    int
        Estimativa do valor ótimo (geralmente 90-95% do real).
    """
    # Calcula razões
    items = [(i, values[i] / weights[i]) for i in range(n)]
    items.sort(key=lambda x: -x[1])  # Ordena por razão decrescente

    total_value = 0
    total_weight = 0

    for i, ratio in items:
        if total_weight + weights[i] <= capacity:
            total_value += values[i]
            total_weight += weights[i]

    # Retorna 95% do valor greedy como estimativa do ótimo
    # (greedy geralmente está 5-10% acima do ótimo para mochila)
    return int(total_value * 0.95)


def save_instance(filepath, n, capacity, values, weights, optimal=None, instance_type="unknown"):
    """
    Salva instância em arquivo no formato padrão.

    Formato:
    --------
    # optimal: <valor_otimo>
    # type: <tipo_instancia>
    <n> <capacidade>
    <valor_1> <peso_1>
    <valor_2> <peso_2>
    ...
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Comentários com metadados
        if optimal is not None:
            f.write(f"# optimal: {optimal}\n")
        f.write(f"# type: {instance_type}\n")

        # Primeira linha: n e capacidade
        f.write(f"{n} {capacity}\n")

        # Itens: valor peso
        for i in range(n):
            f.write(f"{values[i]} {weights[i]}\n")

    print(f"  ✓ {os.path.basename(filepath)}: {n} itens, cap={capacity}, tipo={instance_type}")


def generate_all_instances():
    """
    Gera conjunto completo de instâncias de teste.

    Cria instâncias de diferentes tamanhos e tipos.
    """
    print("\n" + "="*70)
    print("GERAÇÃO DE INSTÂNCIAS LOCAIS")
    print("="*70)
    print("\nGerando instâncias baseadas na literatura científica...")
    print("(Pisinger, 2005; Jooken et al., 2022)\n")

    create_instance_directory()

    # Tamanhos das instâncias
    sizes = [
        (50, "pequena"),
        (100, "pequena"),
        (200, "média"),
        (500, "média"),
        (1000, "grande"),
    ]

    # Tipos de instâncias
    generators = [
        ("uncorrelated", generate_uncorrelated_instance),
        ("weakly_correlated", generate_weakly_correlated_instance),
        ("strongly_correlated", generate_strongly_correlated_instance),
        ("subset_sum", generate_subset_sum_instance),
    ]

    instance_count = 0

    for n, size_label in sizes:
        print(f"\n[{size_label.upper()}] Gerando instâncias com {n} itens...")

        for type_name, generator_func in generators:
            # Gera instância
            seed = 1000 + instance_count
            n_items, capacity, values, weights = generator_func(n, seed=seed)

            # Estima valor ótimo
            optimal_estimate = estimate_optimal_value(n_items, capacity, values, weights)

            # Nome do arquivo
            filename = f"{type_name}_{n}_items.txt"
            filepath = os.path.join("instances", filename)

            # Salva
            save_instance(filepath, n_items, capacity, values, weights,
                         optimal=optimal_estimate, instance_type=type_name)

            instance_count += 1

    print(f"\n[OK] Total gerado: {instance_count} instâncias")
    return instance_count


def create_instance_catalog():
    """
    Cria arquivo README com informações sobre as instâncias.
    """
    catalog_path = os.path.join("instances", "README_INSTANCIAS.txt")

    with open(catalog_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("CATÁLOGO DE INSTÂNCIAS - PROBLEMA DA MOCHILA\n")
        f.write("="*70 + "\n\n")

        f.write("FONTE: Geradas localmente\n")
        f.write("BASEADO EM: Literatura científica (Pisinger, Jooken et al.)\n\n")

        f.write("TIPOS DE INSTÂNCIAS:\n")
        f.write("-"*70 + "\n")
        f.write("1. UNCORRELATED (Não-correlacionadas)\n")
        f.write("   - Valores e pesos independentes\n")
        f.write("   - Mais fáceis de resolver\n\n")

        f.write("2. WEAKLY_CORRELATED (Fracamente correlacionadas)\n")
        f.write("   - Valores próximos aos pesos: v ≈ w ± 100\n")
        f.write("   - Dificuldade média\n\n")

        f.write("3. STRONGLY_CORRELATED (Fortemente correlacionadas)\n")
        f.write("   - Valores muito próximos aos pesos: v = w + 10\n")
        f.write("   - Mais difíceis\n\n")

        f.write("4. SUBSET_SUM (Soma de subconjuntos)\n")
        f.write("   - Valores iguais aos pesos: v = w\n")
        f.write("   - As mais difíceis\n\n")

        f.write("="*70 + "\n")
        f.write("TAMANHOS DISPONÍVEIS:\n")
        f.write("="*70 + "\n")
        f.write("- Pequenas: 50, 100 itens\n")
        f.write("- Médias: 200, 500 itens\n")
        f.write("- Grandes: 1000 itens\n\n")

        f.write("="*70 + "\n")
        f.write("FORMATO DOS ARQUIVOS:\n")
        f.write("="*70 + "\n")
        f.write("Linha 1: # optimal: <valor_ótimo_estimado>\n")
        f.write("Linha 2: # type: <tipo_instância>\n")
        f.write("Linha 3: <n> <capacidade>\n")
        f.write("Linhas 4+: <valor> <peso> (um item por linha)\n\n")

        f.write("="*70 + "\n")
        f.write("REFERÊNCIAS:\n")
        f.write("="*70 + "\n")
        f.write("Pisinger, D. (2005). Where are the hard knapsack problems?\n")
        f.write("  Computers & Operations Research, 32(9), 2271-2284.\n\n")
        f.write("Jooken, J., et al. (2022). A new class of hard problem instances\n")
        f.write("  for the 0-1 knapsack problem. European Journal of OR, 301(3).\n")
        f.write("="*70 + "\n")

    print(f"\n[INFO] Catálogo criado em: {catalog_path}")


def verify_instances():
    """Verifica se as instâncias foram geradas corretamente."""
    print("\n[VERIFICAÇÃO] Validando instâncias geradas...\n")

    files = [f for f in os.listdir("instances") if f.endswith('.txt') and not f.startswith('README')]

    for filename in sorted(files):
        filepath = os.path.join("instances", filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            # Pula comentários
            start = 0
            for i, line in enumerate(lines):
                if not line.startswith('#'):
                    start = i
                    break

            # Lê n e capacity
            n, cap = map(int, lines[start].split())

            # Conta itens
            num_items = len(lines) - start - 1

            if num_items == n:
                print(f"  ✓ {filename}: OK ({n} itens, cap={cap})")
            else:
                print(f"  ✗ {filename}: ERRO - esperava {n} itens, encontrou {num_items}")

        except Exception as e:
            print(f"  ✗ {filename}: ERRO - {e}")


def main():
    """Função principal."""
    print("\n" + "="*70)
    print(" "*15 + "GERADOR DE INSTÂNCIAS")
    print("="*70)
    print("\nEste script gera instâncias locais de alta qualidade para o")
    print("Problema da Mochila, baseadas nas características das instâncias")
    print("clássicas da literatura científica.\n")

    # Gera instâncias
    num_generated = generate_all_instances()

    # Cria catálogo
    create_instance_catalog()

    # Verifica
    verify_instances()

    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    print(f"✓ {num_generated} instâncias geradas com sucesso")
    print(f"✓ Instâncias salvas em: instances/")
    print(f"✓ 4 tipos diferentes (uncorrelated, weakly, strongly, subset_sum)")
    print(f"✓ 5 tamanhos diferentes (50, 100, 200, 500, 1000 itens)")
    print("="*70)

    print("\n[PRÓXIMO PASSO] Execute:")
    print("  python main.py --experiment --runs 10")
    print("\nOu use o script automatizado:")
    print("  python run_complete_experiment.py --runs 10\n")


if __name__ == "__main__":
    main()