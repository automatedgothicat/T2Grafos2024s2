import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import MiniBatchKMeans


caminho_csv = 'disney_plus_titles.csv'
df = pd.read_csv(caminho_csv)

print(df.head())
print(df.info())

filmes = df[['title', 'description', 'director', 'cast', 'country', 'release_year', 'rating', 'listed_in']].copy()
print(filmes.head())

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(filmes['description'].fillna(''))

print("Matriz TF-IDF criada com dimensões:", tfidf_matrix.shape)

n_clusters = 10
kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42)
kmeans.fit(tfidf_matrix)

filmes['cluster'] = kmeans.labels_
print(filmes[['title', 'cluster']].head())

grafo = nx.Graph()

for _, row in filmes.iterrows():
    grafo.add_node(row['title'], cluster=row['cluster'])
    if row['director']:
        grafo.add_edge(row['title'], row['director'])

print("Número de nós no grafo:", grafo.number_of_nodes())

def recomendar_filmes(titulo, df, grafo, top_n=5):
    cluster = df.loc[df['title'] == titulo, 'cluster'].values[0]
    
    semelhantes = df[df['cluster'] == cluster]['title'].tolist()
    semelhantes.remove(titulo)
    
    return semelhantes[:top_n]

titulo = input("Insira o titulo de um filme em inglês disponível no disney plus: ")
rec = recomendar_filmes(titulo,filmes,grafo)
print(rec)

# ---------------------------------------------------------

dark = {
    'node_color': 'black',
    'font_color': 'white',
    'edge_color': 'gray',
    'node_size': 1000,
    'font_size': 10,
    'width': 0.5
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