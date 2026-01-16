

import os
import sys
import argparse
from datetime import datetime

# Importa módulos do projeto
try:
    from instance import KnapsackInstance, load_all_instances_from_dir
    from experiments import run_full_experiment, generate_random_instance
except ImportError as e:
    print(f"[ERRO] Não foi possível importar módulos: {e}")
    print("Certifique-se de estar no diretório correto do projeto.")
    sys.exit(1)


def check_instances_available(min_instances=3):

    instances = load_all_instances_from_dir("instances")

    if len(instances) < min_instances:
        print(f"\n[AVISO] Encontradas apenas {len(instances)} instâncias.")
        print(f"         Recomendado: pelo menos {min_instances} instâncias.")
        return False

    return True


def download_instances_if_needed():

    if check_instances_available():
        print("[OK] Instâncias já disponíveis.")
        return True

    print("\n[AÇÃO] Baixando instâncias da OR-Library...")

    try:
        import download_instances
        stats = download_instances.download_all_instances()

        if stats['success'] > 0:
            print(f"[OK] {stats['success']} instâncias baixadas com sucesso!")
            return True
        else:
            print("[ERRO] Falha ao baixar instâncias.")
            return False

    except ImportError:
        print("[ERRO] Arquivo download_instances.py não encontrado.")
        print("       Baixe as instâncias manualmente ou crie instâncias locais.")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao baixar instâncias: {e}")
        return False


def create_local_instances_fallback():

    print("\n[FALLBACK] Gerando instâncias locais aleatórias...")

    sizes = [20, 50, 100, 200, 500]
    instances = []

    for i, n in enumerate(sizes):
        inst = generate_random_instance(n, capacity_ratio=0.5, seed=1000 + i)
        inst.name = f"random_{n}_items"
        instances.append(inst)

        # Salva em arquivo
        os.makedirs("instances", exist_ok=True)
        filepath = f"instances/{inst.name}.txt"
        inst.save_to_file(filepath, include_optimal=False)
        print(f"  ✓ Criado: {inst.name} ({n} itens)")

    print(f"\n[OK] {len(instances)} instâncias locais criadas.")
    return instances


def run_experiment_with_validation(num_runs=10, quick_mode=False):

    print("\n" + "=" * 70)
    print("EXPERIMENTO COMPLETO - HIPERHEURÍSTICA PARA PROBLEMA DA MOCHILA")
    print("=" * 70)

    # 1. Verifica/baixa instâncias
    print("\n[PASSO 1/3] Verificando instâncias...")

    if not download_instances_if_needed():
        print("\n[ALTERNATIVA] Usando instâncias locais geradas...")
        instances = create_local_instances_fallback()
    else:
        instances = load_all_instances_from_dir("instances")

    if not instances:
        print("[ERRO] Nenhuma instância disponível. Abortando.")
        return False

    # Modo rápido: apenas instâncias pequenas
    if quick_mode:
        instances = [inst for inst in instances if inst.n <= 100]
        print(f"\n[MODO RÁPIDO] Usando apenas {len(instances)} instâncias pequenas (≤100 itens)")

    print(f"\n[INFO] Total de instâncias a processar: {len(instances)}")
    for inst in instances:
        opt_str = f", ótimo={inst.optimal_value}" if inst.optimal_value else ""
        print(f"  • {inst.name}: {inst.n} itens{opt_str}")

    # 2. Executa experimento
    print("\n[PASSO 2/3] Executando experimento...")
    print(f"  Execuções por algoritmo: {num_runs}")
    print(f"  Isso pode levar alguns minutos...\n")

    try:
        runner = run_full_experiment(
            instances=instances,
            output_prefix="experiment",
            num_runs=num_runs,
            verbose=True
        )

        print("\n[OK] Experimento concluído com sucesso!")

    except Exception as e:
        print(f"\n[ERRO] Falha durante experimento: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Validação dos resultados
    print("\n[PASSO 3/3] Validando resultados...")

    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"[ERRO] Diretório {results_dir}/ não encontrado.")
        return False

    files = os.listdir(results_dir)
    csv_files = [f for f in files if f.endswith('.csv')]
    json_files = [f for f in files if f.endswith('.json')]

    print(f"\n[RESULTADOS] Arquivos gerados:")
    print(f"  CSV:  {len(csv_files)} arquivo(s)")
    print(f"  JSON: {len(json_files)} arquivo(s)")

    if csv_files:
        latest_csv = sorted(csv_files)[-1]
        print(f"\n  Arquivo mais recente: {latest_csv}")

        # Conta linhas do CSV
        csv_path = os.path.join(results_dir, latest_csv)
        with open(csv_path, 'r') as f:
            num_lines = sum(1 for _ in f) - 1  # -1 para header

        print(f"  Total de execuções: {num_lines}")

    return True


def generate_quick_report(results_dir="results"):

    import csv

    files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]

    if not files:
        print("[AVISO] Nenhum arquivo CSV encontrado para gerar relatório.")
        return

    latest = sorted(files)[-1]
    filepath = os.path.join(results_dir, latest)

    print("\n" + "=" * 70)
    print(f"RELATÓRIO RESUMIDO: {latest}")
    print("=" * 70)

    # Lê CSV
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    if not data:
        print("[AVISO] Arquivo CSV vazio.")
        return

    # Agrupa por algoritmo
    by_algorithm = {}
    for row in data:
        alg = row['algorithm']
        if alg not in by_algorithm:
            by_algorithm[alg] = []
        by_algorithm[alg].append(float(row['value']))

    # Estatísticas
    print(f"\n{'Algoritmo':<25} {'Execuções':>10} {'Média':>12} {'Desvio':>12} {'Melhor':>12}")
    print("-" * 70)

    for alg in sorted(by_algorithm.keys()):
        values = by_algorithm[alg]
        mean = sum(values) / len(values)

        if len(values) > 1:
            variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
            std = variance ** 0.5
        else:
            std = 0

        best = max(values)

        print(f"{alg:<25} {len(values):>10} {mean:>12.2f} {std:>12.2f} {best:>12.2f}")

    print("=" * 70)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Executa experimento completo para o trabalho de PO"
    )
    parser.add_argument(
        '--runs', '-r',
        type=int,
        default=10,
        help='Número de execuções por algoritmo (padrão: 10)'
    )
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Modo rápido (apenas instâncias pequenas)'
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Pula download de instâncias (usa apenas existentes)'
    )

    args = parser.parse_args()

    # Banner
    print("\n" + "=" * 70)
    print(" " * 15 + "EXPERIMENTO COMPLETO - TRABALHO DE PO")
    print("=" * 70)
    print(f"\nData/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Configuração:")
    print(f"  • Execuções por algoritmo: {args.runs}")
    print(f"  • Modo rápido: {'Sim' if args.quick else 'Não'}")
    print(f"  • Download automático: {'Não' if args.skip_download else 'Sim'}")

    # Executa
    success = run_experiment_with_validation(
        num_runs=args.runs,
        quick_mode=args.quick
    )

    if success:
        # Gera relatório resumido
        generate_quick_report()

        print("\n" + "=" * 70)
        print("EXPERIMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 70)
        print("\nPróximos passos:")
        print("  1. Analise os resultados em: results/")
        print("  2. Use os dados para escrever o relatório técnico")
        print("  3. Gere gráficos comparativos (opcional)")
        print("\nArquivos importantes:")
        print("  • results/experiment_*.csv  → Dados tabulares")
        print("  • results/experiment_*.json → Dados estruturados")
        print("=" * 70 + "\n")

        return 0
    else:
        print("\n" + "=" * 70)
        print("EXPERIMENTO FALHOU")
        print("=" * 70)
        print("\nVerifique os erros acima e tente novamente.")
        print("=" * 70 + "\n")

        return 1


if __name__ == "__main__":
    sys.exit(main())