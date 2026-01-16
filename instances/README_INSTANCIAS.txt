======================================================================
CATÁLOGO DE INSTÂNCIAS - PROBLEMA DA MOCHILA
======================================================================

FONTE: Geradas localmente
BASEADO EM: Literatura científica (Pisinger, Jooken et al.)

TIPOS DE INSTÂNCIAS:
----------------------------------------------------------------------
1. UNCORRELATED (Não-correlacionadas)
   - Valores e pesos independentes
   - Mais fáceis de resolver

2. WEAKLY_CORRELATED (Fracamente correlacionadas)
   - Valores próximos aos pesos: v ≈ w ± 100
   - Dificuldade média

3. STRONGLY_CORRELATED (Fortemente correlacionadas)
   - Valores muito próximos aos pesos: v = w + 10
   - Mais difíceis

4. SUBSET_SUM (Soma de subconjuntos)
   - Valores iguais aos pesos: v = w
   - As mais difíceis

======================================================================
TAMANHOS DISPONÍVEIS:
======================================================================
- Pequenas: 50, 100 itens
- Médias: 200, 500 itens
- Grandes: 1000 itens

======================================================================
FORMATO DOS ARQUIVOS:
======================================================================
Linha 1: # optimal: <valor_ótimo_estimado>
Linha 2: # type: <tipo_instância>
Linha 3: <n> <capacidade>
Linhas 4+: <valor> <peso> (um item por linha)

======================================================================
REFERÊNCIAS:
======================================================================
Pisinger, D. (2005). Where are the hard knapsack problems?
  Computers & Operations Research, 32(9), 2271-2284.

Jooken, J., et al. (2022). A new class of hard problem instances
  for the 0-1 knapsack problem. European Journal of OR, 301(3).
======================================================================
