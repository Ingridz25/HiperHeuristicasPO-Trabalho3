"""
===========================================================
MÓDULO: instance.py
Representação e Leitura de Instâncias do Problema da Mochila
===========================================================

Este módulo contém a classe que representa uma instância do
Problema da Mochila Binária (0/1 Knapsack Problem).

CONCEITO: O Problema da Mochila Binaria
------------------------------------------
Imagine que você tem uma mochila com capacidade limitada de peso.
Você tem vários itens, cada um com um peso e um valor.
O objetivo é escolher quais itens levar para MAXIMIZAR o valor total,
sem ultrapassar a capacidade da mochila.

A restrição "binária" significa que você só pode escolher levar
ou não levar cada item (não dá pra levar "meio" item).
"""


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
    
    Exemplo:
    --------
    Se temos 3 itens:
        - Item 0: peso=5, valor=10
        - Item 1: peso=3, valor=7
        - Item 2: peso=4, valor=8
    E a mochila suporta no máximo 10kg.
    
    instance.weights = [5, 3, 4]
    instance.values = [10, 7, 8]
    instance.capacity = 10
    """
    
    def __init__(self, capacity, weights, values, optimal_value=None):
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
        """
        self.capacity = capacity
        self.weights = weights
        self.values = values
        self.n = len(weights)  # Número de itens
        self.optimal_value = optimal_value
        
        # Validação básica dos dados
        if len(weights) != len(values):
            raise ValueError(
                "A lista de pesos e valores deve ter o mesmo tamanho!"
            )
    
    @staticmethod
    def from_file(path):
        """
        Lê uma instância a partir de um arquivo no formato OR-Library.
        
        Formato OR-Library:
        ----------------------
        Linha 1: n capacidade
        Linha 2 em diante: valor peso (um item por linha)
        
        Exemplo de arquivo:
        -------------------
        4 10
        10 5
        7 3
        8 4
        9 6
        
        Isso significa:
        - 4 itens disponíveis
        - Mochila suporta peso 10
        - Item 0: valor=10, peso=5
        - Item 1: valor=7, peso=3
        - Item 2: valor=8, peso=4
        - Item 3: valor=9, peso=6
        
        Parâmetros:
        -----------
        path : str
            Caminho para o arquivo da instância.
        
        Retorna:
        --------
        KnapsackInstance
            Objeto representando a instância lida.
        """
        with open(path, 'r') as f:
            # Primeira linha: número de itens e capacidade
            first_line = f.readline().split()
            n = int(first_line[0])
            capacity = int(first_line[1])
            
            # Lê cada item (valor e peso)
            values = []
            weights = []
            for _ in range(n):
                line = f.readline().split()
                v = int(line[0])  # Valor do item
                w = int(line[1])  # Peso do item
                values.append(v)
                weights.append(w)
        
        return KnapsackInstance(capacity, weights, values)
    
    def get_ratio(self, item_index):
        """
        Calcula a razão valor/peso de um item.
        
        Por que isso e util?
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
    
    def __str__(self):
        """Representação textual da instância (para debug)."""
        return (
            f"KnapsackInstance(n={self.n}, capacity={self.capacity}, "
            f"total_value={sum(self.values)}, total_weight={sum(self.weights)})"
        )
    
    def __repr__(self):
        return self.__str__()


# =====================================================
# CÓDIGO DE TESTE
# =====================================================
if __name__ == "__main__":
    # Teste rápido: criar instância manualmente
    inst = KnapsackInstance(
        capacity=10,
        weights=[5, 3, 4, 6],
        values=[10, 7, 8, 9]
    )
    
    print("[OK] Instancia criada com sucesso!")
    print(inst)
    print(f"   Razão item 0: {inst.get_ratio(0):.2f}")
    print(f"   Razão item 1: {inst.get_ratio(1):.2f}")

