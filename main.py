import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# check: https://github.com/dedeco/dijkstra-bellman-ford/tree/master
# livro: https://computerscience360.wordpress.com/wp-content/uploads/2018/02/algoritmos-teoria-e-prc3a1tica-3ed-thomas-cormen.pdf

# Carregar dados do CSV
caminho_csv = 'disney_plus_titles.csv'
df = pd.read_csv(caminho_csv)

# Criar um grafo
grafo = nx.Graph()
filmes = {}
descricoes = {}

for _, row in df.iterrows():
    titulo = row["Título"]
    generos = row["Gênero"].split(", ")
    descricao = row["Descrição"]
    grafo.add_node(titulo, gênero=generos, descrição=descricao)
    filmes[titulo] = generos
    descricoes[titulo] = descricao

# Calcular a similaridade entre descrições usando TF-IDF e cosseno da similaridade
titulos = list(descricoes.keys() )
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(descricoes.values())
similaridade_descricoes = cosine_similarity(tfidf_matrix)

# Adicionar arestas ao grafo com base na similaridade das descrições
for i, titulo1 in enumerate(titulos):
    for j, titulo2 in enumerate(titulos):
        if i != j:
            similaridade = similaridade_descricoes[i, j]
            if similaridade > 0.1:  # Define um limite mínimo de similaridade para adicionar uma aresta
                grafo.add_edge(titulo1, titulo2, weight=similaridade)

# Calcular a similaridade entre títulos usando TF-IDF e cosseno da similaridade
titulos = list(filmes.keys())
tfidf_titulos = TfidfVectorizer().fit_transform(titulos)
similaridade_titulos = cosine_similarity(tfidf_titulos)

# Adicionar ao grafo um peso composto (gêneros e títulos)
for i, titulo1 in enumerate(titulos):
    for j, titulo2 in enumerate(titulos):
        if i != j:
            similaridade_generos = similaridade_descricoes[i, j]  # Similaridade de descrições (gêneros)
            similaridade_titulo = similaridade_titulos[i, j]     # Similaridade de títulos
            
            # Peso final como uma média ponderada de ambas as similaridades
            peso_total = 0.7 * similaridade_generos + 0.3 * similaridade_titulo
            if peso_total > 0.1:  # Limite mínimo para criar uma aresta
                grafo.add_edge(titulo1, titulo2, weight=peso_total)

# Função para recomendar filmes com base em uma descrição similar
def recomendar_filmes(grafo, filme, limite_similaridade=0.1):
    if filme not in grafo:
        print(f"{filme} não está no grafo.")
        return []
    
    recomendacoes = [
        (vizinho, float(round(peso['weight'], 2))) 
        for vizinho, peso in grafo[filme].items()
        if peso['weight'] >= limite_similaridade
    ]
    recomendacoes.sort(key=lambda x: x[1], reverse=True)
    
    return recomendacoes

def obter_titulo_valido(grafo):
    # Converte os títulos do grafo para minúsculas para uma comparação insensível a case
    titulos_disponiveis = [titulo.lower() for titulo in grafo.nodes]
    mapa_titulos_originais = {titulo.lower(): titulo for titulo in grafo.nodes}

    while True:
        # Solicita ao usuário um título e converte para minúsculas
        titulo_usuario = input("Escolha um filme para ver recomendações: ").lower()
        
        # Verifica se o título digitado existe no grafo
        if titulo_usuario in mapa_titulos_originais:
            return mapa_titulos_originais[titulo_usuario]
        
        # Se não encontrar, sugere um título semelhante
        tfidf_titulos = TfidfVectorizer().fit_transform(titulos_disponiveis + [titulo_usuario])
        similaridades = cosine_similarity(tfidf_titulos[-1], tfidf_titulos[:-1]).flatten()
        indice_mais_proximo = similaridades.argmax()
        
        sugestao = mapa_titulos_originais[titulos_disponiveis[indice_mais_proximo]]
        print(f"Filme não encontrado. Você quis dizer '{sugestao}'?")

# Entrada do usuário e recomendações
titulo_valido = obter_titulo_valido(grafo)
recomendacoes = recomendar_filmes(grafo, titulo_valido, limite_similaridade=0.1)
print(f"Recomendações para {titulo_valido}:", recomendacoes)

# ------------------------------------------

# Parâmetros de estilo para a visualização
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

# Gerar layout para o grafo
pos = nx.spring_layout(grafo, k=0.3, seed=42)  # k controla a distância entre os nós

# Visualizar o grafo com todos os nós em preto
plt.figure(figsize=(14, 8))
nx.draw(grafo, pos, with_labels=False, **dark)

# Destacar o nó do filme escolhido pelo usuário em vermelho
nx.draw_networkx_nodes(grafo, pos, nodelist=[titulo_valido], **highlight)

# Adicionar rótulos com um fundo para melhorar a legibilidade
labels = {node: node for node in grafo.nodes()}
nx.draw_networkx_labels(grafo, pos, labels=labels, font_size=10, font_color='white',
                        bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.3'))

plt.title("Grafo de Filmes com Similaridade nas Descrições")
plt.show()