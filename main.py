import networkx as nx
import pandas as pd 

caminho_csv = 'marvel.csv'
df = pd.read_csv(caminho_csv)

# Criar um grafo
grafo = nx.Graph()
filmes = {}

for _, row in df.iterrows():
    titulo = row["Título"]
    generos = row["Gênero"].split(", ")
    grafo.add_node(titulo, gênero=generos, descrição=row["Descrição"])
    filmes[titulo] = generos

# Calcular similaridade entre filmes e adicionar arestas ao grafo
for filme1, generos1 in filmes.items():
    for filme2, generos2 in filmes.items():
        if filme1 != filme2:
            # Calcular a similaridade como o número de gêneros em comum
            similaridade = len(set(generos1).intersection(generos2))
            if similaridade > 0:
                # Adicionar uma aresta com peso baseado na similaridade
                grafo.add_edge(filme1, filme2, weight=similaridade)

# Função para recomendar filmes com base em um filme de entrada
def recomendar_filmes(grafo, filme, limite_similaridade=1):
    if filme not in grafo:
        print(f"{filme} não está no grafo.")
        return []
    
    recomendacoes = [
        (vizinho, peso) 
        for vizinho, peso in grafo[filme].items()
        if peso['weight'] >= limite_similaridade
    ]
    recomendacoes.sort(key=lambda x: x[1]['weight'], reverse=True)
    
    return recomendacoes

name = input("Escolha um filme pra ver recomendações: ")
recomendacoes = recomendar_filmes(grafo, name, limite_similaridade=1)
print("Recomendações para " + name + ":", recomendacoes)