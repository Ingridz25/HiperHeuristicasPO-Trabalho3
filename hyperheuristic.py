"""
Hiperheurística de seleção automática de heurísticas para o problema da mochila.
"""

import random
import math
from solution import Solution, create_random_solution
from heuristics import (
    greedy_value, greedy_weight, greedy_ratio, greedy_random,
    local_search_1flip, local_search_2swap, fill_remaining
)


class HyperHeuristic:

    def __init__(self, heuristics):

        self.heuristics = heuristics

        # Inicializa scores: todas começam iguais
        self.scores = {h.__name__: 1.0 for h in heuristics}

        # Histórico para análise posterior
        self.history = []

        # Contadores de uso
        self.usage_count = {h.__name__: 0 for h in heuristics}

    def select_heuristic(self):
        """
        Seleciona uma heurística. Deve ser sobrescrito nas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar select_heuristic()")

    def update_scores(self, heuristic, old_value, new_value):

        name = heuristic.__name__

        # Calcula recompensa baseada na melhoria
        improvement = new_value - old_value

        if improvement > 0:
            # Melhorou! Aumenta o score proporcional à melhoria
            reward = 1 + (improvement / max(old_value, 1)) * 10
        elif improvement == 0:
            # Não mudou nada - pequena penalidade
            reward = 0.5
        else:
            # Piorou - penalidade maior
            reward = 0.1

        # Aplica a recompensa
        self.scores[name] = max(0.1, self.scores[name] * reward)

        # Registra no histórico
        self.history.append({
            'heuristic': name,
            'old_value': old_value,
            'new_value': new_value,
            'improvement': improvement,
            'reward': reward,
            'new_score': self.scores[name]
        })

        # Incrementa contador de uso
        self.usage_count[name] += 1

    def get_statistics(self):

        stats = {}
        for h in self.heuristics:
            name = h.__name__
            # Filtra histórico desta heurística
            h_history = [e for e in self.history if e['heuristic'] == name]

            if h_history:
                improvements = [e['improvement'] for e in h_history]
                stats[name] = {
                    'uses': len(h_history),
                    'avg_improvement': sum(improvements) / len(improvements),
                    'total_improvement': sum(improvements),
                    'best_improvement': max(improvements),
                    'current_score': self.scores[name]
                }
            else:
                stats[name] = {
                    'uses': 0,
                    'avg_improvement': 0,
                    'total_improvement': 0,
                    'best_improvement': 0,
                    'current_score': self.scores[name]
                }

        return stats

    def print_statistics(self):
        """Imprime estatísticas formatadas."""
        stats = self.get_statistics()

        print("\n[ESTATISTICAS] ESTATISTICAS DA HIPERHEURISTICA")
        print("=" * 60)
        print(f"{'Heuristica':<25} {'Usos':>6} {'Melhoria Media':>15} {'Score':>10}")
        print("-" * 60)

        for name, data in sorted(stats.items(), key=lambda x: -x[1]['uses']):
            print(f"{name:<25} {data['uses']:>6} {data['avg_improvement']:>15.2f} {data['current_score']:>10.2f}")


class RouletteWheelHH(HyperHeuristic):

    def select_heuristic(self):
        """
        Seleciona uma heurística usando roleta ponderada.
        """
        # Calcula total dos scores
        total = sum(self.scores.values())

        # "Gira" a roleta: número aleatório entre 0 e total
        r = random.uniform(0, total)

        # Percorre as heurísticas somando scores
        # Para quando a soma ultrapassa r
        accumulated = 0
        for h in self.heuristics:
            accumulated += self.scores[h.__name__]
            if accumulated >= r:
                return h

        # Fallback (não deveria chegar aqui)
        return self.heuristics[-1]

    def solve(self, instance, iterations=100, verbose=False):

        # Começa com solução gulosa
        current = greedy_ratio(instance)
        best = current.copy()

        if verbose:
            print(f"HH Roleta - Início: valor={best.value}")

        for i in range(iterations):
            # Seleciona heurística
            h = self.select_heuristic()
            old_value = current.value

            # Aplica a heurística
            # Verifica se é construtiva (recebe instance) ou de melhoria (recebe solution)
            try:
                new_solution = h(current)  # Tenta como melhoria
            except TypeError:
                new_solution = h(instance)  # É construtiva

            # Aceita se for viável
            if new_solution.is_feasible():
                self.update_scores(h, old_value, new_solution.value)
                current = new_solution

                if current.value > best.value:
                    best = current.copy()
                    if verbose:
                        print(f"  Iter {i}: {h.__name__} → novo melhor = {best.value}")

        return best


class EpsilonGreedyHH(HyperHeuristic):

    def __init__(self, heuristics, epsilon=0.3, epsilon_decay=0.99, min_epsilon=0.05):

        super().__init__(heuristics)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

    def select_heuristic(self):
        """
        Seleciona heurística usando estratégia epsilon-greedy.
        """
        if random.random() < self.epsilon:
            # EXPLORAÇÃO: escolhe aleatoriamente
            return random.choice(self.heuristics)
        else:
            # EXPLOITAÇÃO: escolhe a melhor
            best_name = max(self.scores.keys(), key=lambda k: self.scores[k])
            return next(h for h in self.heuristics if h.__name__ == best_name)

    def decay_epsilon(self):
        """Diminui o epsilon (menos exploração ao longo do tempo)."""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def solve(self, instance, iterations=100, verbose=False):
        """
        Resolve o problema usando epsilon-greedy.
        """
        current = greedy_ratio(instance)
        best = current.copy()

        if verbose:
            print(f"HH Epsilon-Greedy - Início: valor={best.value}, ε={self.epsilon:.3f}")

        for i in range(iterations):
            h = self.select_heuristic()
            old_value = current.value

            try:
                new_solution = h(current)
            except TypeError:
                new_solution = h(instance)

            if new_solution.is_feasible():
                self.update_scores(h, old_value, new_solution.value)
                current = new_solution

                if current.value > best.value:
                    best = current.copy()
                    if verbose:
                        print(f"  Iter {i}: {h.__name__} → melhor = {best.value} (ε={self.epsilon:.3f})")

            # Diminui epsilon
            self.decay_epsilon()

        return best


class ReinforcementLearningHH(HyperHeuristic):


    def __init__(self, heuristics, learning_rate=0.1, discount_factor=0.9):

        super().__init__(heuristics)
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        # Q-values (estimativas de qualidade)
        self.q_values = {h.__name__: 0.0 for h in heuristics}

        # Temperaturas para seleção softmax
        self.temperature = 1.0

    def select_heuristic(self):

        # Calcula exponenciais
        exp_values = {}
        for h in self.heuristics:
            name = h.__name__
            # Limita para evitar overflow
            exp_values[name] = math.exp(min(self.q_values[name] / self.temperature, 50))

        total = sum(exp_values.values())

        # Seleciona com probabilidade proporcional
        r = random.uniform(0, total)
        accumulated = 0
        for h in self.heuristics:
            accumulated += exp_values[h.__name__]
            if accumulated >= r:
                return h

        return self.heuristics[-1]

    def update_q_value(self, heuristic, reward):
        """
        Atualiza o Q-value de uma heurística.
        
        Fórmula: Q(h) = Q(h) + α * (recompensa - Q(h))
        """
        name = heuristic.__name__
        old_q = self.q_values[name]

        # Atualização Q-learning simplificada
        self.q_values[name] = old_q + self.learning_rate * (reward - old_q)

    def solve(self, instance, iterations=100, verbose=False):
        """
        Resolve o problema usando aprendizado por reforço.
        """
        current = greedy_ratio(instance)
        best = current.copy()

        if verbose:
            print(f"HH Reinforcement Learning - Início: valor={best.value}")

        for i in range(iterations):
            h = self.select_heuristic()
            old_value = current.value

            try:
                new_solution = h(current)
            except TypeError:
                new_solution = h(instance)

            if new_solution.is_feasible():
                # Calcula recompensa
                improvement = new_solution.value - old_value

                # Normaliza a recompensa para escala razoável
                if improvement > 0:
                    reward = 1.0 + improvement / max(old_value, 1)
                elif improvement == 0:
                    reward = 0.0
                else:
                    reward = -0.5

                # Atualiza Q-value
                self.update_q_value(h, reward)

                # Atualiza scores para manter compatibilidade
                self.update_scores(h, old_value, new_solution.value)

                current = new_solution

                if current.value > best.value:
                    best = current.copy()
                    if verbose:
                        print(f"  Iter {i}: {h.__name__} → melhor = {best.value}")

            # Diminui temperatura (fica mais greedy)
            self.temperature = max(0.1, self.temperature * 0.99)

        return best

    def print_q_values(self):
        """Imprime os Q-values aprendidos."""
        print("\n[Q-VALUES] Q-VALUES APRENDIDOS")
        print("-" * 40)
        for name, q in sorted(self.q_values.items(), key=lambda x: -x[1]):
            print(f"  {name:<25}: {q:.4f}")



class AdaptiveHyperHeuristic(HyperHeuristic):


    def __init__(self, heuristics,
                 epsilon=0.4,
                 epsilon_decay=0.995,
                 learning_rate=0.15,
                 stagnation_limit=20):

        super().__init__(heuristics)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.stagnation_limit = stagnation_limit

        # Q-values para cada heurística
        self.q_values = {h.__name__: 1.0 for h in heuristics}

    def select_heuristic(self):
        """Seleção epsilon-greedy baseada em Q-values."""
        if random.random() < self.epsilon:
            return random.choice(self.heuristics)
        else:
            best_name = max(self.q_values.keys(), key=lambda k: self.q_values[k])
            return next(h for h in self.heuristics if h.__name__ == best_name)

    def update_learning(self, heuristic, improvement, solution_value):
        """Atualiza Q-values com recompensa."""
        name = heuristic.__name__

        # Recompensa normalizada
        if improvement > 0:
            reward = 1.0 + (improvement / max(solution_value, 1)) * 5
        elif improvement == 0:
            reward = 0.1
        else:
            reward = -0.3

        # Atualização do Q-value
        old_q = self.q_values[name]
        self.q_values[name] = old_q + self.learning_rate * (reward - old_q)

    def solve(self, instance, iterations=200, verbose=False):
        """
        Resolve o problema com a hiperheurística adaptativa.
        """
        # Inicialização: tenta todas as heurísticas construtivas
        constructive = [greedy_value, greedy_weight, greedy_ratio]
        best = None
        for h in constructive:
            sol = h(instance)
            if best is None or sol.value > best.value:
                best = sol.copy()

        current = best.copy()
        stagnation = 0

        if verbose:
            print(f"HH Adaptativa - Início: valor={best.value}")
            print(f"  Parâmetros: ε={self.epsilon:.2f}, lr={self.learning_rate}")

        for i in range(iterations):
            h = self.select_heuristic()
            old_value = current.value

            # Aplica heurística
            try:
                new_solution = h(current)
            except TypeError:
                new_solution = h(instance)

            if new_solution.is_feasible():
                improvement = new_solution.value - old_value

                # Atualiza aprendizado
                self.update_learning(h, improvement, old_value)
                self.update_scores(h, old_value, new_solution.value)

                # Aceita se melhorou
                if improvement >= 0:
                    current = new_solution
                    stagnation = 0 if improvement > 0 else stagnation + 1

                    if current.value > best.value:
                        best = current.copy()
                        if verbose:
                            print(f"  Iter {i}: {h.__name__} → NOVO MELHOR = {best.value}")
                else:
                    stagnation += 1

                # Reinício se estagnou
                if stagnation >= self.stagnation_limit:
                    current = create_random_solution(instance)
                    current = fill_remaining(current)
                    stagnation = 0
                    if verbose:
                        print(f"  Iter {i}: REINÍCIO (estagnação)")

            # Decai epsilon
            self.epsilon = max(0.05, self.epsilon * self.epsilon_decay)

        return best



def get_default_heuristics():
    """Retorna conjunto padrão de heurísticas para a hiperheurística."""
    return [
        local_search_1flip,
        local_search_2swap,
        fill_remaining,
    ]


def create_hyperheuristic(method='adaptive', heuristics=None):

    if heuristics is None:
        heuristics = get_default_heuristics()

    if method == 'roulette':
        return RouletteWheelHH(heuristics)
    elif method == 'epsilon_greedy':
        return EpsilonGreedyHH(heuristics)
    elif method == 'rl':
        return ReinforcementLearningHH(heuristics)
    elif method == 'adaptive':
        return AdaptiveHyperHeuristic(heuristics)
    else:
        raise ValueError(f"Método desconhecido: {method}")


if __name__ == "__main__":
    from instance import KnapsackInstance

    # Cria instância de teste
    inst = KnapsackInstance(
        capacity=50,
        weights=[10, 20, 30, 40, 25, 15, 35, 45, 5, 12],
        values=[60, 100, 120, 150, 90, 50, 130, 180, 30, 70]
    )

    print("=" * 70)
    print("TESTE DAS HIPERHEURÍSTICAS")
    print("=" * 70)
    print(f"\nInstância: {inst.n} itens, capacidade={inst.capacity}")

    # Baseline
    baseline = greedy_ratio(inst)
    print(f"\n[BASELINE] Baseline (Greedy Ratio): valor={baseline.value}")

    # Testa cada tipo de hiperheurística
    heuristics = get_default_heuristics()

    print("\n--- Roleta Ponderada ---")
    hh1 = RouletteWheelHH(heuristics)
    result1 = hh1.solve(inst, iterations=100, verbose=False)
    print(f"Resultado: valor={result1.value}")
    hh1.print_statistics()

    print("\n--- Epsilon-Greedy ---")
    hh2 = EpsilonGreedyHH(heuristics, epsilon=0.4)
    result2 = hh2.solve(inst, iterations=100, verbose=False)
    print(f"Resultado: valor={result2.value}")
    hh2.print_statistics()

    print("\n--- Aprendizado por Reforço ---")
    hh3 = ReinforcementLearningHH(heuristics)
    result3 = hh3.solve(inst, iterations=100, verbose=False)
    print(f"Resultado: valor={result3.value}")
    hh3.print_q_values()

    print("\n--- Hiperheurística Adaptativa ---")
    hh4 = AdaptiveHyperHeuristic(heuristics)
    result4 = hh4.solve(inst, iterations=150, verbose=True)
    print(f"Resultado: valor={result4.value}")
    hh4.print_statistics()

    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO COMPARATIVO")
    print("=" * 70)
    print(f"Baseline:         {baseline.value}")
    print(f"Roleta:           {result1.value}")
    print(f"Epsilon-Greedy:   {result2.value}")
    print(f"RL:               {result3.value}")
    print(f"Adaptativa:       {result4.value}")
