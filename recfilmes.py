import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import MiniBatchKMeans
from networkx.algorithms.link_prediction import adamic_adar_index

caminho_csv = 'disney_plus_titles.csv'
df = pd.read_csv(caminho_csv)

print(df.head())
print(df.info())

filmes = df[['title', 'description', 'director', 'cast', 'country', 'release_year', 'rating', 'listed_in']].copy()

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(filmes['description'].fillna(''))

n_clusters = 100
kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42)
kmeans.fit(tfidf_matrix)

filmes['cluster'] = kmeans.labels_

grafo = nx.Graph()

for _, row in filmes.iterrows():
    grafo.add_node(row['title'], type='filme', cluster=row['cluster'])
    
    if row['director']:
        grafo.add_edge(row['title'], row['director'], type='diretor')
    
    if pd.notna(row['cast']):
        for ator in row['cast'].split(','):
            grafo.add_edge(row['title'], ator.strip(), type='ator')
    
    if pd.notna(row['country']):
        grafo.add_edge(row['title'], row['country'], type='pais')
    
    if pd.notna(row['listed_in']):
        for categoria in row['listed_in'].split(','):
            grafo.add_edge(row['title'], categoria.strip(), type='categoria')

def recomendar_filmes(titulo, filmes, grafo, tfidf_matrix, top_n=5):
    if titulo not in filmes['title'].values:
        print(f"Filme '{titulo}' não encontrado.")
        return []

    idx = filmes[filmes['title'] == titulo].index[0]
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix)
    similar_indices = cosine_sim.argsort()[0][-top_n-1:-1]
    filmes_recomendados_cosine = filmes['title'].iloc[similar_indices].tolist()

    recomendacoes_adamic_adar = []
    for neighbor in grafo.neighbors(titulo):
        score = 0
        for u, v, p in adamic_adar_index(grafo, [(titulo, neighbor)]):
            score += p
        recomendacoes_adamic_adar.append((neighbor, score))
    
    recomendacoes_adamic_adar.sort(key=lambda x: x[1], reverse=True)
    filmes_recomendados_adamic_adar = [filme for filme, _ in recomendacoes_adamic_adar[:top_n]]
    filmes_recomendados = list(set(filmes_recomendados_cosine) | set(filmes_recomendados_adamic_adar))
    filmes_recomendados = [filme for filme in filmes_recomendados if filme != titulo]
    
    return filmes_recomendados[:top_n]

titulo = input("Insira o título de um filme em inglês disponível no Disney Plus: ")
while titulo not in df['title'].values:
    print(f"Desculpe, o título '{titulo}' não foi encontrado no catálogo. Verifique a ortografia e tente novamente.")
    titulo = input("Insira o título de um filme em inglês disponível no Disney Plus: ")

rec = recomendar_filmes(titulo, filmes, grafo, tfidf_matrix)
print(f"Filmes recomendados baseados em '{titulo}': {rec}")

# ---------------------------------------------------------

dark = {
    'node_color': '#1c1c1c',
    'font_color': 'white',
    'edge_color': '#757575',
    'node_size': 1000,
    'font_size': 12,
    'width': 0.8
}

highlight = {
    'node_color': 'red',
    'node_size': 1200,
}

def visualizar_grafo(grafo, titulo):
    subgrafo = grafo.subgraph([titulo] + list(grafo.neighbors(titulo)))

    pos = nx.spring_layout(subgrafo, k=0.3, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(subgrafo, pos, with_labels=False, **dark)
    nx.draw_networkx_nodes(subgrafo, pos, nodelist=[titulo], **highlight)
    labels = {node: node for node in subgrafo.nodes()}
    nx.draw_networkx_labels(subgrafo, pos, labels=labels, font_size=10, font_color='white',
                            bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.3'))
    plt.title(f"Grafo das Conexões de '{titulo}'")
    plt.show()

    pos = nx.spring_layout(grafo, k=0.8, seed=42)
    plt.figure(figsize=(14, 8))
    nx.draw(grafo, pos, with_labels=False, **dark)
    nx.draw_networkx_nodes(grafo, pos, nodelist=[titulo], **highlight)
    labels = {node: node for node in grafo.nodes() if node == titulo}
    nx.draw_networkx_labels(grafo, pos, labels=labels, font_size=8, font_color='white',
                            bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.3'))
    plt.title("Grafo Completo com Destaque no Título Escolhido")
    plt.show()

visualizar_grafo(grafo, titulo)