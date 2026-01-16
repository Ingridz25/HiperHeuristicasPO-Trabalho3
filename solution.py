"""
Representação de soluções para o problema da mochila.
"""

from instance import KnapsackInstance
import random


class Solution:
    """
    Representa uma solução para o Problema da Mochila.
    
    Atributos:
    ----------
    instance : KnapsackInstance
        A instância do problema que esta solução resolve.
    items : list[int]
        Vetor binário indicando quais itens estão na mochila.
    value : int
        Valor total dos itens selecionados.
    weight : int
        Peso total dos itens selecionados.
    """

    def __init__(self, instance):
        """
        Cria uma solução vazia (nenhum item selecionado).
        
        Parâmetros:
        -----------
        instance : KnapsackInstance
            Instância do problema.
        """
        self.instance = instance
        # Inicialmente, nenhum item está na mochila
        self.items = [0] * instance.n
        self.value = 0
        self.weight = 0

    def evaluate(self):

        self.value = sum(
            self.items[i] * self.instance.values[i]
            for i in range(self.instance.n)
        )

        # Mesmo raciocínio para o peso
        self.weight = sum(
            self.items[i] * self.instance.weights[i]
            for i in range(self.instance.n)
        )

    def is_feasible(self):

        return self.weight <= self.instance.capacity

    def copy(self):

        # Cria uma cópia independente desta solução.

        nova = Solution(self.instance)
        nova.items = self.items[:]  # [:] cria cópia da lista
        nova.evaluate()
        return nova

    def add_item(self, index):

        if self.items[index] == 1:
            return True  # Já está na mochila

        self.items[index] = 1
        self.evaluate()

        if not self.is_feasible():
            # Não coube! Desfaz a operação
            self.items[index] = 0
            self.evaluate()
            return False

        return True

    def remove_item(self, index):

        self.items[index] = 0
        self.evaluate()

    def flip_item(self, index):

        self.items[index] = 1 - self.items[index]
        self.evaluate()

    def get_selected_items(self):

        return [i for i in range(self.instance.n) if self.items[i] == 1]

    def get_unselected_items(self):

        return [i for i in range(self.instance.n) if self.items[i] == 0]

    def remaining_capacity(self):

        return self.instance.capacity - self.weight

    def calculate_gap(self):

        if self.instance.optimal_value is None:
            return None

        if self.instance.optimal_value == 0:
            return 0.0

        gap = (self.instance.optimal_value - self.value) / self.instance.optimal_value
        return gap * 100

    def __str__(self):
        """Representação textual da solução."""
        selected = self.get_selected_items()
        return (
            f"Solution(value={self.value}, weight={self.weight}/{self.instance.capacity}, "
            f"items={selected})"
        )

    def __repr__(self):
        return self.__str__()


def create_random_solution(instance):
    sol = Solution(instance)

    # Embaralha a ordem dos itens
    order = list(range(instance.n))
    random.shuffle(order)

    # Tenta adicionar itens na ordem aleatória
    for i in order:
        sol.add_item(i)

    return sol


if __name__ == "__main__":
    # Cria instância de teste
    inst = KnapsackInstance(
        capacity=10,
        weights=[5, 3, 4, 6],
        values=[10, 7, 8, 9]
    )

    # Cria solução vazia
    sol = Solution(inst)
    print("Solução vazia:", sol)

    # Adiciona alguns itens
    sol.add_item(0)  # peso=5, valor=10
    print("Após adicionar item 0:", sol)

    sol.add_item(1)  # peso=3, valor=7
    print("Após adicionar item 1:", sol)

    # Tenta adicionar item que não cabe
    result = sol.add_item(2)  # peso=4, excederia
    print(f"Tentou adicionar item 2: sucesso={result}")
    print("Estado final:", sol)

    # Testa solução aleatória
    print("\nSolução aleatória:", create_random_solution(inst))
