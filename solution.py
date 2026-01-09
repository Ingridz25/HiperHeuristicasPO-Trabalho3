"""
===========================================================
MÓDULO: solution.py
Representação de Soluções para o Problema da Mochila
===========================================================

Este módulo contém a classe que representa uma solução
(quais itens foram escolhidos para a mochila).

CONCEITO: Representacao de Solucao
-------------------------------------
Usamos um vetor binário (lista de 0s e 1s) para representar
quais itens foram escolhidos:
- items[i] = 1 → Item i está na mochila
- items[i] = 0 → Item i NÃO está na mochila

Exemplo com 4 itens:
items = [1, 0, 1, 0]
Significa: escolhemos os itens 0 e 2, não pegamos 1 e 3.
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
        """
        Recalcula o valor e peso totais da solução.
        
        IMPORTANTE: Sempre chame este metodo apos modificar self.items!
        
        A função percorre todos os itens e soma os valores/pesos
        dos itens que estão na mochila (items[i] == 1).
        """
        # Calcula o valor total somando os valores dos itens selecionados
        # A expressão items[i] * values[i] resulta em:
        # - values[i] se items[i] == 1 (item selecionado)
        # - 0 se items[i] == 0 (item não selecionado)
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
        """
        Verifica se a solução é viável (respeita a capacidade).
        
        Uma solucao e INVIAVEL quando o peso total dos itens
        selecionados ultrapassa a capacidade da mochila.
        
        Retorna:
        --------
        bool
            True se o peso total ≤ capacidade, False caso contrário.
        """
        return self.weight <= self.instance.capacity
    
    def copy(self):
        """
        Cria uma cópia independente desta solução.
        
        Por que precisamos copiar?
        Quando fazemos busca local, queremos testar modificações
        sem perder a solução original. Se fizermos s2 = s1, ambas
        apontam para o mesmo objeto! Precisamos de uma cópia real.
        
        Retorna:
        --------
        Solution
            Nova solução com os mesmos itens.
        """
        nova = Solution(self.instance)
        nova.items = self.items[:]  # [:] cria cópia da lista
        nova.evaluate()
        return nova
    
    def add_item(self, index):
        """
        Adiciona um item à mochila (se possível).
        
        Parâmetros:
        -----------
        index : int
            Índice do item a adicionar.
        
        Retorna:
        --------
        bool
            True se conseguiu adicionar e permanece viável.
        """
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
        """
        Remove um item da mochila.
        
        Parâmetros:
        -----------
        index : int
            Índice do item a remover.
        """
        self.items[index] = 0
        self.evaluate()
    
    def flip_item(self, index):
        """
        Inverte o estado de um item (0→1 ou 1→0).
        
        Esta operacao e muito usada em buscas locais!
        """
        self.items[index] = 1 - self.items[index]
        self.evaluate()
    
    def get_selected_items(self):
        """
        Retorna lista dos índices dos itens selecionados.
        
        Retorna:
        --------
        list[int]
            Índices dos itens na mochila.
        """
        return [i for i in range(self.instance.n) if self.items[i] == 1]
    
    def get_unselected_items(self):
        """
        Retorna lista dos índices dos itens NÃO selecionados.
        
        Retorna:
        --------
        list[int]
            Índices dos itens fora da mochila.
        """
        return [i for i in range(self.instance.n) if self.items[i] == 0]
    
    def remaining_capacity(self):
        """
        Calcula quanto peso ainda cabe na mochila.
        
        Retorna:
        --------
        int
            Capacidade disponível.
        """
        return self.instance.capacity - self.weight
    
    def calculate_gap(self):
        """
        Calcula o gap em relação ao ótimo conhecido.
        
        O GAP nos diz quao longe estamos da solucao perfeita.
        Gap = 0% significa que encontramos o ótimo!
        
        Fórmula: gap = (ótimo - encontrado) / ótimo * 100
        
        Retorna:
        --------
        float ou None
            Percentual de gap, ou None se ótimo não conhecido.
        """
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


# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def create_random_solution(instance):
    """
    Cria uma solução aleatória viável.
    
    Util para inicializacao de metaheuristicas!
    
    Parâmetros:
    -----------
    instance : KnapsackInstance
        Instância do problema.
    
    Retorna:
    --------
    Solution
        Solução aleatória que respeita a capacidade.
    """
    sol = Solution(instance)
    
    # Embaralha a ordem dos itens
    order = list(range(instance.n))
    random.shuffle(order)
    
    # Tenta adicionar itens na ordem aleatória
    for i in order:
        sol.add_item(i)
    
    return sol


# =====================================================
# CÓDIGO DE TESTE
# =====================================================
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

