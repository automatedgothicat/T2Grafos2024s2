#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define infinito 1000000

// declaração structs
typedef struct {
    int vert; 
    int peso;
    struct aresta *proxVertice;
} aresta;

typedef struct {
    aresta *cab;
} cabLista;

typedef struct { 
    int vertices; 
    int arestas; 
    cabLista *adj; 	
} grafo;

// declaração funções
grafo *criaGrafo (int numvertices);
aresta *criaAresta(int vertice, int peso);
bool ligarAresta(grafo *g, int vertOrigem, int vertFim, int peso);
int mapeiaVertice(char vertice);
void printGrafo(grafo *gr);
void Dijkstra(grafo *g, int vertInicial, int vertFinal);
int contarLinhas(FILE *path);
void BFS(grafo *g, int verticeInicial);
void buscaProfundidade(grafo *g, int verticeInicial);
void DFS(grafo *g, int vertice, bool *visitado);

int main(){
    int menu = -1;
    FILE *fonte;
    grafo *mainGrafo;
    do {
        printf("--- x MENU x ---\n");
        printf("0 - fechar programa\n");
        printf("1 - selecionar arquivo\n");
        printf("2 - ler arquivo e criar grafo\n");
        printf("3 - visualizar grafo\n");
        printf("4 - calcular menor caminho\n");
        printf("5 - busca por largura\n");
        printf("6 - busca por profundidade\n");
        printf("Opcao: ");
        scanf("%d",&menu);

        switch (menu){
            case 0: {
                break;
            }
            case 1: {
                char path[256];
                printf("Insira o caminho do arquivo contendo sua extensao: ");
                scanf("%255s",path);

                fonte = fopen(path, "r");
                if(fonte == NULL){
                    printf("erro ao abrir arquivo...\n");
                    exit (1);
                }
                break;
            }
            case 2: {
                int nLinhas = contarLinhas(fonte);
                rewind(fonte);
                mainGrafo = criaGrafo(nLinhas);

                char linha[50];
                char vertOrigem, vertFinal;
                int OrigemId, FinalId, peso;
                while(fgets(linha,sizeof(linha),fonte)){
                    sscanf(linha,"%c;%c;%d",&vertOrigem,&vertFinal,&peso);
                    OrigemId = mapeiaVertice(vertOrigem);
                    FinalId = mapeiaVertice(vertFinal);
                    ligarAresta(mainGrafo, OrigemId, FinalId, peso);
                }
                puts("Grafo criado.");
                break;
            }
            case 3: {
                printGrafo(mainGrafo);
                break;
            }
            case 4: {
                char CaminhoIni,CaminhoFim;
                int IdVertIni, IdVertFinal;
                printf("\nSelecione dois vertices para calcular o menor caminho.\n");
                printf("Vertice inicial: ");
                scanf(" %c",&CaminhoIni);
                printf("\nVertice final: ");
                scanf(" %c",&CaminhoFim);

                IdVertIni = mapeiaVertice(CaminhoIni);
                IdVertFinal = mapeiaVertice(CaminhoFim);

                Dijkstra(mainGrafo,IdVertIni,IdVertFinal);
                break;
            }
            case 5: {
                char verticeInicial;
                printf("Digite o vertice inicial para a busca em largura: ");
                scanf(" %c", &verticeInicial);
                int verticeInicialId = mapeiaVertice(verticeInicial);
                BFS(mainGrafo,verticeInicialId);

                break;
            }
            case 6: {
                char verticeInicial;
                printf("Digite o vertice inicial para a busca em profundidade: ");
                scanf(" %c", &verticeInicial);
                int verticeInicialId = mapeiaVertice(verticeInicial);
                buscaProfundidade(mainGrafo,verticeInicialId);

                break;
            }
            default:{
                printf("Selecione uma opcao valida\n");
                break;
            }
        }
    } while (menu != 0);
    fclose(fonte);
    return 0;
}

// implementação das funções
grafo *criaGrafo (int numvertices) {
	int i;

	grafo *g = (grafo *)malloc(sizeof(grafo)); 
	g->vertices = numvertices;
	g->arestas = 0;
	g->adj = (cabLista *)malloc(numvertices*sizeof(cabLista)); 

	for (i = 0; i < numvertices; i++){
		g->adj[i].cab=NULL;
	}

	return(g);
}

aresta *criaAresta(int vertice, int peso){
    aresta *temp = (aresta *)malloc(sizeof(aresta));
    temp->vert = vertice;
    temp->peso = peso;
    temp->proxVertice = NULL;

    return(temp);
}

bool ligarAresta(grafo *g, int vertOrigem, int vertFim, int peso){
    if(!g) return false;
    
    aresta *nova = criaAresta(vertFim,peso);
    nova->proxVertice = g->adj[vertOrigem].cab;
    g->adj[vertOrigem].cab = nova;
    g->arestas++;

    return true;
}

int mapeiaVertice(char vertice) {
    return vertice - 'A';  // Supondo que os vértices sejam 'A', 'B', 'C', etc.
}

void printGrafo(grafo *gr){
	printf("Vertices: %d. Arestas: %d. \n",gr->vertices,gr->arestas);
	int i;
	
	for(i = 0; i < gr->vertices; i++){
        printf("Vertice %c: ", i + 'A');
		aresta *ad = gr->adj[i].cab;
			while(ad){ 
				printf("v%c(%d) ",ad->vert + 'A',ad->peso);
				ad = ad->proxVertice;
			}
		printf("\n");	
	}
}

void Dijkstra(grafo *g, int vertInicial, int vertFinal){
    const int totalVert = g->vertices;
    int i;
    int distancia[totalVert];
    int anterior[totalVert];
    bool visitado[totalVert];

    for(i = 0; i < totalVert; i++){
        distancia[i] = infinito;
        visitado[i] = false;
        anterior[i] = -1;
    }
    distancia[vertInicial] = 0;

    int visita, ultimo;
    for(i = 0; i < totalVert; i++){
        int menorDist = infinito;
        int ultimo = -1;

        for(visita = 0; visita < totalVert; visita++){
            if(!visitado[visita] && distancia[visita] < menorDist){
                menorDist = distancia[visita];
                ultimo = visita;
            }
        }
        
        if(ultimo == -1)
            break;

        visitado[ultimo] = true;

        aresta *vizinho = g->adj[ultimo].cab;
        int vertId, pesoCaminho;

        while (vizinho) {
            vertId = vizinho->vert;
            pesoCaminho = vizinho->peso;

            if (!visitado[vertId] && distancia[ultimo] + pesoCaminho < distancia[vertId]) {
                distancia[vertId] = distancia[ultimo] + pesoCaminho;
                anterior[vertId] = ultimo;
            }

            vizinho = vizinho->proxVertice;
        }
    }

    if(distancia[vertFinal] == infinito){
        printf("Caminho inexistente.\n");
    } else{
        printf("Custo do caminho: %d\n",distancia[vertFinal]);
    }

    int caminho[totalVert];
    int contador = 0;
    for (i = vertFinal; i != -1; i = anterior[i]) {
            caminho[contador++] = i;
        }

    printf("Caminho:");
        for (i = contador - 1; i >= 0; i--) {
            printf(" %c", caminho[i] + 'A');  // Convertendo o índice de volta para caractere
            if (i > 0) printf(" ->");
        }
        printf("\n");
}

int contarLinhas(FILE *path){
    int linhas = 0;
    char caractere;

    while ((caractere = fgetc(path)) != EOF){
        if(caractere == '\n') linhas++;
    }
    
    if(caractere != '\n') linhas++;
    return linhas;
}

void BFS(grafo *g, int verticeInicial) {
    bool *visitado = (bool *)calloc(g->vertices, sizeof(bool));
    int *fila = (int *)malloc(g->vertices * sizeof(int));
    int inicio = 0, fim = 0;

    visitado[verticeInicial] = true;
    fila[fim++] = verticeInicial;

    printf("Busca em Largura (BFS) a partir do vértice %c:\n", verticeInicial + 'A');

    while (inicio < fim) {
        int vertice = fila[inicio++];  
        printf("%c ", vertice + 'A');

        aresta *vizinho = g->adj[vertice].cab;
        while (vizinho != NULL) {
            if (!visitado[vizinho->vert]) {
                visitado[vizinho->vert] = true;
                fila[fim++] = vizinho->vert;
            }
            vizinho = vizinho->proxVertice;
        }
    }
    printf("\n");

    free(visitado);
    free(fila);
}

void DFS(grafo *g, int vertice, bool *visitado) {
    visitado[vertice] = true;
    printf("%c ", vertice + 'A');

    aresta *vizinho = g->adj[vertice].cab;
    while (vizinho != NULL) {
        if (!visitado[vizinho->vert]) {
            DFS(g, vizinho->vert, visitado);
        }
        vizinho = vizinho->proxVertice;
    }
}

void buscaProfundidade(grafo *g, int verticeInicial) {
    bool *visitado = (bool *)calloc(g->vertices, sizeof(bool));
    printf("Busca em Profundidade (DFS) a partir do vértice %c:\n", verticeInicial + 'A');
    DFS(g, verticeInicial, visitado);
    printf("\n");
    free(visitado);
}