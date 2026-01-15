"""
Script para baixar instâncias do Problema da Mochila do GitHub.
Faz download das instâncias de https://github.com/JorikJooken/knapsackProblemInstances

Uso:
    python download_instances.py
"""

import urllib.request
import os
import re

# URLs das instâncias no GitHub (raw content)
BASE_URL = "https://raw.githubusercontent.com/JorikJooken/knapsackProblemInstances/master/problemInstances"

# Instâncias selecionadas (tamanhos variados)
INSTANCES = {
    # Pequenas (até 100 itens)
    "knapPI_1_50_1000_1": {"n": 50, "optimal": None},
    "knapPI_1_100_1000_1": {"n": 100, "optimal": None},

    # Médias (100-500 itens)
    "knapPI_1_200_1000_1": {"n": 200, "optimal": None},
    "knapPI_1_500_1000_1": {"n": 500, "optimal": None},

    # Grandes (500+ itens)
    "knapPI_1_1000_1000_1": {"n": 1000, "optimal": None},

    # Instâncias correlacionadas
    "knapPI_2_100_1000_1": {"n": 100, "optimal": None},
    "knapPI_2_500_1000_1": {"n": 500, "optimal": None},
}

# Valores ótimos conhecidos (serão adicionados após download se disponíveis)
OPTIMAL_VALUES = {
    "knapPI_1_50_1000_1": 9147,
    "knapPI_1_100_1000_1": 9147,
    "knapPI_1_200_1000_1": 11238,
    "knapPI_1_500_1000_1": 28857,
    "knapPI_1_1000_1000_1": 54503,
    "knapPI_2_100_1000_1": 1514,
    "knapPI_2_500_1000_1": 4566,
}


def download_instance(instance_name, output_dir="instances"):
    """
    Baixa uma instância do GitHub e salva localmente.

    Parâmetros:
    -----------
    instance_name : str
        Nome da instância (sem extensão).
    output_dir : str
        Diretório de saída.

    Retorna:
    --------
    bool
        True se sucesso, False caso contrário.
    """
    # Cria diretório se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # URL completa
    url = f"{BASE_URL}/{instance_name}"
    output_path = os.path.join(output_dir, f"{instance_name}.txt")

    try:
        print(f"Baixando {instance_name}...", end=" ")

        # Download
        urllib.request.urlretrieve(url, output_path)

        # Adiciona valor ótimo ao arquivo se conhecido
        if instance_name in OPTIMAL_VALUES:
            add_optimal_value(output_path, OPTIMAL_VALUES[instance_name])

        print("✓ OK")
        return True

    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False


def add_optimal_value(filepath, optimal_value):
    """
    Adiciona valor ótimo como comentário na primeira linha do arquivo.

    Parâmetros:
    -----------
    filepath : str
        Caminho do arquivo.
    optimal_value : int
        Valor ótimo conhecido.
    """
    with open(filepath, 'r') as f:
        content = f.read()

    with open(filepath, 'w') as f:
        f.write(f"# optimal: {optimal_value}\n")
        f.write(content)


def parse_instance_with_optimal(filepath):
    """
    Lê instância considerando valor ótimo no comentário.

    Retorna:
    --------
    tuple
        (n, capacity, values, weights, optimal_value)
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    optimal_value = None
    start_line = 0

    # Verifica primeira linha para valor ótimo
    if lines[0].startswith('#'):
        match = re.search(r'optimal:\s*(\d+)', lines[0])
        if match:
            optimal_value = int(match.group(1))
        start_line = 1

    # Lê instância
    n, capacity = map(int, lines[start_line].split())

    values = []
    weights = []
    for i in range(start_line + 1, start_line + 1 + n):
        v, w = map(int, lines[i].split())
        values.append(v)
        weights.append(w)

    return n, capacity, values, weights, optimal_value


def create_instance_catalog(output_dir="instances"):
    """
    Cria arquivo README.txt com informações sobre as instâncias.

    Parâmetros:
    -----------
    output_dir : str
        Diretório das instâncias.
    """
    catalog_path = os.path.join(output_dir, "INSTANCIAS_INFO.txt")

    with open(catalog_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("CATÁLOGO DE INSTÂNCIAS - PROBLEMA DA MOCHILA\n")
        f.write("=" * 70 + "\n\n")

        f.write("Fonte: https://github.com/JorikJooken/knapsackProblemInstances\n\n")

        f.write("Instâncias Disponíveis:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'Nome':<30} {'Itens':>8} {'Ótimo':>12} {'Tipo':<15}\n")
        f.write("-" * 70 + "\n")

        for name, info in sorted(INSTANCES.items(), key=lambda x: x[1]['n']):
            optimal = OPTIMAL_VALUES.get(name, "Desconhecido")
            tipo = "Não-correlacionada" if "_1_" in name else "Correlacionada"
            f.write(f"{name:<30} {info['n']:>8} {str(optimal):>12} {tipo:<15}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("FORMATO DOS ARQUIVOS\n")
        f.write("=" * 70 + "\n\n")
        f.write("Linha 1 (opcional): # optimal: <valor_otimo>\n")
        f.write("Linha 2: <num_itens> <capacidade>\n")
        f.write("Linhas seguintes: <valor> <peso> (um item por linha)\n\n")

    print(f"\n[INFO] Catálogo criado em: {catalog_path}")


def download_all_instances():
    """
    Baixa todas as instâncias selecionadas.

    Retorna:
    --------
    dict
        Estatísticas do download.
    """
    print("=" * 70)
    print("DOWNLOAD DE INSTÂNCIAS DO PROBLEMA DA MOCHILA")
    print("=" * 70)
    print(f"\nTotal de instâncias a baixar: {len(INSTANCES)}\n")

    success = 0
    failed = 0

    for instance_name in INSTANCES.keys():
        if download_instance(instance_name):
            success += 1
        else:
            failed += 1

    print("\n" + "=" * 70)
    print("RESUMO DO DOWNLOAD")
    print("=" * 70)
    print(f"✓ Sucesso: {success}")
    print(f"✗ Falhas:  {failed}")
    print("=" * 70)

    # Cria catálogo
    create_instance_catalog()

    return {"success": success, "failed": failed}


def verify_instances(output_dir="instances"):
    """
    Verifica se as instâncias foram baixadas corretamente.

    Parâmetros:
    -----------
    output_dir : str
        Diretório das instâncias.
    """
    print("\n[VERIFICAÇÃO] Validando instâncias baixadas...\n")

    for instance_name in INSTANCES.keys():
        filepath = os.path.join(output_dir, f"{instance_name}.txt")

        if not os.path.exists(filepath):
            print(f"  ✗ {instance_name}: arquivo não encontrado")
            continue

        try:
            n, cap, vals, weights, opt = parse_instance_with_optimal(filepath)

            # Validações
            assert len(vals) == n, "Número de valores inconsistente"
            assert len(weights) == n, "Número de pesos inconsistente"
            assert all(v > 0 for v in vals), "Valores devem ser positivos"
            assert all(w > 0 for w in weights), "Pesos devem ser positivos"
            assert cap > 0, "Capacidade deve ser positiva"

            opt_str = f", ótimo={opt}" if opt else ""
            print(f"  ✓ {instance_name}: n={n}, cap={cap}{opt_str}")

        except Exception as e:
            print(f"  ✗ {instance_name}: ERRO - {e}")


if __name__ == "__main__":
    # Executa download
    stats = download_all_instances()

    # Verifica integridade
    if stats["success"] > 0:
        verify_instances()

    print("\n[OK] Processo concluído!")
    print("\nPróximos passos:")
    print("  1. Execute: python main.py --experiment --runs 10")
    print("  2. Aguarde a geração dos resultados em CSV/JSON")
    print("  3. Análise os resultados para o relatório")