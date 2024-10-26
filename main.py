import networkx as nx

# Dados de exemplo: uma lista de filmes com seus gêneros
filmes = {
    "Filme A": ["Ação", "Aventura"],
    "Filme B": ["Ação", "Comédia"],
    "Filme C": ["Drama"],
    "Filme D": ["Aventura", "Fantasia"],
    "Filme E": ["Comédia", "Romance"],
    "Filme F": ["Ação", "Fantasia"],
}

# Criar um grafo
grafo = nx.Graph()

# Adicionar nós ao grafo
for filme, generos in filmes.items():
    grafo.add_node(filme, generos=generos)

# Adicionar arestas com base na similaridade de gêneros
for filme1, generos1 in filmes.items():
    for filme2, generos2 in filmes.items():
        if filme1 != filme2:
            # Calcular a similaridade como o número de gêneros em comum
            similaridade = len(set(generos1).intersection(generos2))
            if similaridade > 0:
                # Adicionar uma aresta com peso baseado na similaridade
                grafo.add_edge(filme1, filme2, weight=similaridade)

# Função para recomendar filmes com base em um filme de entrada
def recomendar_filmes(grafo, filme_base, top_n=3):
    if filme_base not in grafo:
        print("O filme não está no grafo.")
        return []

    # Obter filmes conectados ao filme base, ordenados por peso da aresta (similaridade)
    conexoes = sorted(grafo[filme_base].items(), key=lambda x: x[1]['weight'], reverse=True)
    recomendacoes = [filme for filme, _ in conexoes[:top_n]]
    return recomendacoes

# Testar o sistema de recomendação
filme_base = "Filme A"
recomendacoes = recomendar_filmes(grafo, filme_base)
print(f"Recomendações para {filme_base}: {recomendacoes}")