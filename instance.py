"""
===========================================================
MÓDULO: instance.py
Representação e Leitura de Instâncias do Problema da Mochila
===========================================================

Este módulo contém a classe que representa uma instância do
Problema da Mochila Binária (0/1 Knapsack Problem).

ATUALIZAÇÃO: Agora suporta valores ótimos conhecidos para cálculo de GAP.
"""

import re


class KnapsackInstance:
    """
    Representa uma instância do Problema da Mochila Binária.

    Atributos:
    ----------
    capacity : int
        Capacidade máxima de peso que a mochila suporta.
    weights : list[int]
        Lista com o peso de cada item.
    values : list[int]
        Lista com o valor de cada item.
    n : int
        Número total de itens disponíveis.
    optimal_value : int ou None
        Valor ótimo conhecido (se disponível).
    name : str
        Nome da instância (extraído do arquivo).
    """

    def __init__(self, capacity, weights, values, optimal_value=None, name="unnamed"):
        """
        Inicializa uma instância do problema.

        Parâmetros:
        -----------
        capacity : int
            Capacidade máxima da mochila em unidades de peso.
        weights : list[int]
            Lista de pesos dos itens.
        values : list[int]
            Lista de valores dos itens.
        optimal_value : int, opcional
            Valor ótimo conhecido (para comparação).
        name : str, opcional
            Nome da instância.
        """
        self.capacity = capacity
        self.weights = weights
        self.values = values
        self.n = len(weights)
        self.optimal_value = optimal_value
        self.name = name

        # Validação básica dos dados
        if len(weights) != len(values):
            raise ValueError(
                "A lista de pesos e valores deve ter o mesmo tamanho!"
            )

        if any(w <= 0 for w in weights):
            raise ValueError("Todos os pesos devem ser positivos!")

        if any(v < 0 for v in values):
            raise ValueError("Valores não podem ser negativos!")

        if capacity <= 0:
            raise ValueError("Capacidade deve ser positiva!")

    @staticmethod
    def from_file(path):
        """
        Lê uma instância a partir de um arquivo.

        Suporta dois formatos:

        1. Formato OR-Library padrão:
        ----------------------
        n capacidade
        valor peso
        valor peso
        ...

        2. Formato com valor ótimo (comentário):
        ----------------------
        # optimal: 9147
        n capacidade
        valor peso
        valor peso
        ...

        Parâmetros:
        -----------
        path : str
            Caminho para o arquivo da instância.

        Retorna:
        --------
        KnapsackInstance
            Objeto representando a instância lida.
        """
        import os

        # Extrai nome do arquivo
        name = os.path.splitext(os.path.basename(path))[0]

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Remove linhas vazias e espaços
        lines = [line.strip() for line in lines if line.strip()]

        optimal_value = None
        start_line = 0

        # Procura por valor ótimo em comentários
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Tenta extrair valor ótimo
                match = re.search(r'optimal[:\s]+(\d+)', line, re.IGNORECASE)
                if match:
                    optimal_value = int(match.group(1))
                start_line = i + 1
            else:
                # Primeira linha sem # é onde começa a instância
                start_line = i
                break

        # Lê primeira linha: n e capacidade
        first_line = lines[start_line].split()
        n = int(first_line[0])
        capacity = int(first_line[1])

        # Lê cada item (valor e peso)
        values = []
        weights = []

        for i in range(start_line + 1, start_line + 1 + n):
            if i >= len(lines):
                raise ValueError(
                    f"Arquivo mal formatado: esperava {n} itens, "
                    f"encontrou apenas {len(values)}"
                )

            parts = lines[i].split()
            if len(parts) < 2:
                raise ValueError(f"Linha {i+1} mal formatada: {lines[i]}")

            v = int(parts[0])  # Valor do item
            w = int(parts[1])  # Peso do item
            values.append(v)
            weights.append(w)

        return KnapsackInstance(capacity, weights, values, optimal_value, name)

    def get_ratio(self, item_index):
        """
        Calcula a razão valor/peso de um item.

        A razão valor/peso nos diz o "custo-benefício" de cada item.
        Um item com razão alta nos dá muito valor por unidade de peso.

        Parâmetros:
        -----------
        item_index : int
            Índice do item (0 a n-1).

        Retorna:
        --------
        float
            Razão valor/peso do item.
        """
        # Evita divisão por zero
        if self.weights[item_index] == 0:
            return float('inf')
        return self.values[item_index] / self.weights[item_index]

    def save_to_file(self, path, include_optimal=True):
        """
        Salva a instância em um arquivo.

        Parâmetros:
        -----------
        path : str
            Caminho do arquivo de saída.
        include_optimal : bool
            Se True, inclui valor ótimo como comentário.
        """
        with open(path, 'w', encoding='utf-8') as f:
            # Comentário com valor ótimo (se conhecido)
            if include_optimal and self.optimal_value is not None:
                f.write(f"# optimal: {self.optimal_value}\n")

            # Nome da instância
            if self.name != "unnamed":
                f.write(f"# instance: {self.name}\n")

            # Primeira linha: n capacidade
            f.write(f"{self.n} {self.capacity}\n")

            # Itens: valor peso
            for i in range(self.n):
                f.write(f"{self.values[i]} {self.weights[i]}\n")

    def get_statistics(self):
        """
        Retorna estatísticas da instância.

        Retorna:
        --------
        dict
            Dicionário com estatísticas.
        """
        total_value = sum(self.values)
        total_weight = sum(self.weights)

        ratios = [self.get_ratio(i) for i in range(self.n)]

        return {
            'name': self.name,
            'n': self.n,
            'capacity': self.capacity,
            'optimal_value': self.optimal_value,
            'total_value': total_value,
            'total_weight': total_weight,
            'avg_value': total_value / self.n,
            'avg_weight': total_weight / self.n,
            'avg_ratio': sum(ratios) / self.n,
            'max_ratio': max(ratios),
            'min_ratio': min(ratios),
            'capacity_ratio': self.capacity / total_weight if total_weight > 0 else 0,
        }

    def print_statistics(self):
        """Imprime estatísticas formatadas."""
        stats = self.get_statistics()

        print(f"\n{'='*60}")
        print(f"ESTATÍSTICAS DA INSTÂNCIA: {stats['name']}")
        print(f"{'='*60}")
        print(f"  Número de itens:        {stats['n']}")
        print(f"  Capacidade:             {stats['capacity']}")

        if stats['optimal_value'] is not None:
            print(f"  Valor ótimo:            {stats['optimal_value']}")
        else:
            print(f"  Valor ótimo:            Desconhecido")

        print(f"\n  Valor total disponível: {stats['total_value']}")
        print(f"  Peso total disponível:  {stats['total_weight']}")
        print(f"  Razão de capacidade:    {stats['capacity_ratio']:.2%}")

        print(f"\n  Valor médio:            {stats['avg_value']:.2f}")
        print(f"  Peso médio:             {stats['avg_weight']:.2f}")
        print(f"  Razão média:            {stats['avg_ratio']:.4f}")
        print(f"  Razão máxima:           {stats['max_ratio']:.4f}")
        print(f"  Razão mínima:           {stats['min_ratio']:.4f}")
        print(f"{'='*60}\n")

    def __str__(self):
        """Representação textual da instância (para debug)."""
        opt_str = f", optimal={self.optimal_value}" if self.optimal_value else ""
        return (
            f"KnapsackInstance(name='{self.name}', n={self.n}, "
            f"capacity={self.capacity}{opt_str})"
        )

    def __repr__(self):
        return self.__str__()


# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def load_all_instances_from_dir(directory="instances"):
    """
    Carrega todas as instâncias de um diretório.

    Parâmetros:
    -----------
    directory : str
        Caminho do diretório.

    Retorna:
    --------
    list[KnapsackInstance]
        Lista de instâncias carregadas.
    """
    import os

    instances = []

    if not os.path.exists(directory):
        print(f"[AVISO] Diretório não encontrado: {directory}")
        return instances

    # Lista arquivos .txt
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]

    # Ignora arquivos de documentação
    ignore = ['README', 'INSTANCIAS_INFO', 'readme']
    files = [f for f in files if not any(ign in f for ign in ignore)]

    print(f"[INFO] Encontrados {len(files)} arquivos em {directory}/")

    for filename in sorted(files):
        filepath = os.path.join(directory, filename)
        try:
            inst = KnapsackInstance.from_file(filepath)
            instances.append(inst)
            print(f"  ✓ {filename}: {inst.n} itens, cap={inst.capacity}")
        except Exception as e:
            print(f"  ✗ {filename}: ERRO - {e}")

    return instances


# =====================================================
# CÓDIGO DE TESTE
# =====================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DO MÓDULO instance.py")
    print("=" * 60)

    # Teste 1: Criar instância manualmente
    print("\n[TESTE 1] Criação manual")
    inst = KnapsackInstance(
        capacity=10,
        weights=[5, 3, 4, 6],
        values=[10, 7, 8, 9],
        optimal_value=17,
        name="teste_manual"
    )

    print(inst)
    print(f"  Razão item 0: {inst.get_ratio(0):.2f}")
    print(f"  Razão item 1: {inst.get_ratio(1):.2f}")

    # Teste 2: Salvar e carregar
    print("\n[TESTE 2] Salvar e carregar")
    inst.save_to_file("test_instance.txt")
    inst_loaded = KnapsackInstance.from_file("test_instance.txt")
    print(f"  Original:  {inst}")
    print(f"  Carregado: {inst_loaded}")

    # Teste 3: Estatísticas
    print("\n[TESTE 3] Estatísticas")
    inst.print_statistics()

    # Teste 4: Carregar múltiplas instâncias
    print("\n[TESTE 4] Carregar do diretório 'instances/'")
    instances = load_all_instances_from_dir("instances")
    print(f"\n[OK] Total carregado: {len(instances)} instâncias")

    # Cleanup
    import os
    if os.path.exists("test_instance.txt"):
        os.remove("test_instance.txt")

    print("\n[OK] Todos os testes concluídos!")