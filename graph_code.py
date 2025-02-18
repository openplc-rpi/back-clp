import json
import numpy as np
from random import random
import networkx as nx

#Função para encontrar valores das portas de entrada
def find_valores(grafo, lista, node_id):
    dici_entradas = {}
    if node_id in grafo.nodes:
        for sucessor_id in grafo.successors(node_id):
            for key in grafo.nodes[sucessor_id]:  # Percorre os atributos do nó
                if key in lista:
                    dici_entradas[sucessor_id]= grafo.nodes[sucessor_id][key]  # Pega o valor ao invés do nome da chave
    return dici_entradas

# Função para propagar valores
def propagar_valores(grafo,dici_entradas,source_handle):
 
    dici_nodos= {} # dicionario para atribuir nós sources e nó target

    # Laço de repetiação para percorrer grafo
    for node_id in grafo.nodes:
        if node_id in dici_entradas.keys(): # condicional para verificar se o nodo em questao esta no dici
            for sucessor_id in grafo.successors(node_id): 
                dici_nodos[node_id] = sucessor_id # adiconando nó target ao nó source


        if node_id in dici_nodos.values(): # condicional para verificar se o nodo em questao esta no dici_nodos

            # Analisando nodo com operação AND
            if grafo.nodes[node_id].get("signal") == "and":
 
                if all(valor > 0 for valor in dici_entradas.values()):
                    for sucessor_id in grafo.successors(node_id):

                        # Se o nó for do tipo "decision", verifica o threshold e ativa a porta
                        if grafo.nodes[sucessor_id].get("label") == "decision":
                            threshold = float(grafo.nodes[sucessor_id]["text"])  # Pegando o limiar do nó "decision"
                            #print(f'Edge: {list(grafo.in_edges(sucessor_id, data=True))}')

                            for edge in grafo.edges(sucessor_id, data=True):
                                source = edge[0]  # Nó de orige
                                target_node = edge[1]  # Nó de destino

                                _,pos2 = grafo.nodes[target_node].items() # obtendo itens do nodo target

                                # Zera todas as portas de saída associadas ao nó de destino
                                if grafo.nodes[target_node].get("label") == "outport":
                                    grafo.nodes[target_node][pos2[0]] = 0

                                if source_handle['true'] == [[source, target_node]] and valor > threshold:
                                    grafo.nodes[target_node][pos2[0]] = 1
                                elif source_handle['false'] == [[source, target_node]] and valor <= threshold:
                                    grafo.nodes[target_node][pos2[0]] = 1
                                else:
                                    pass  # Nenhuma atualização se a condição não for atendida

            # Analisando nodo com operação OR
            if grafo.nodes[node_id].get("signal") == "or":
                
                if any(valor > 0 for valor in dici_entradas.values()):
                    for sucessor_id in grafo.successors(node_id):

                        # Se o nó for do tipo "decision", verifica o threshold e ativa a porta
                        if grafo.nodes[sucessor_id].get("label") == "decision":
                            threshold = float(grafo.nodes[sucessor_id]["text"])  # Pegando o limiar do nó "decision"
                            #print(f'Edge: {list(grafo.in_edges(sucessor_id, data=True))}')

                            for edge in grafo.edges(sucessor_id, data=True):
                                source = edge[0]  # Nó de origem
                                target_node = edge[1]  # Nó de destino

                                _,pos2 = grafo.nodes[target_node].items() # obtendo itens do nodo target

                                # Zera todas as portas de saída associadas ao nó de destino
                                if grafo.nodes[target_node].get("label") == "outport":
                                    grafo.nodes[target_node][pos2[0]] = 0

                                if source_handle['true'] == [[source, target_node]] and valor > threshold:
                                    grafo.nodes[target_node][pos2[0]] = 1
                                elif source_handle['false'] == [[source, target_node]] and valor <= threshold:
                                    grafo.nodes[target_node][pos2[0]] = 1
                                else:
                                    pass  # Nenhuma atualização se a condição não for atendida

            # Analisando nodo com apenas decision               
            if grafo.nodes[node_id].get("label") == "decision":
  
                threshold = float(grafo.nodes[sucessor_id]["text"])  # Pegando o limiar do nó "decision"
                #print(f'Edge: {list(grafo.in_edges(sucessor_id, data=True))}')

                for edge in grafo.edges(sucessor_id, data=True):
                    source = edge[0]  # Nó de origem
                    target_node = edge[1]  # Nó de destino

                    _,pos2 = grafo.nodes[target_node].items() # obtendo itens do nodo target

                    # Zera todas as portas de saída associadas ao nó de destino
                    if grafo.nodes[target_node].get("label") == "outport":
                        grafo.nodes[target_node][pos2[0]] = 0

                    if source_handle['true'] == [[source, target_node]] and valor > threshold:
                        grafo.nodes[target_node][pos2[0]] = 1
                    elif source_handle['false'] == [[source, target_node]] and valor <= threshold:
                        grafo.nodes[target_node][pos2[0]] = 1
                    else:
                        pass  # Nenhuma atualização se a condição não for atendida
                

with open("caso4.json") as file:
    data = json.load(file)

G = nx.DiGraph()

# Criando nodos
for node in data["nodes"]:
    node_id = node['id']
    label = node['data']['label']

    G.add_node(node_id, label=label)

    if label == 'inport':
        port_text = node["data"].get("text", None)
        G.nodes[node_id][port_text] = 0
    if label == 'outport':
        port_text = node["data"].get("text", None)
        G.nodes[node_id][port_text] = 0
    if label == 'decision':
        G.nodes[node_id]["text"] = node["data"].get("text", None)
    if label == 'andor':
        G.nodes[node_id]["signal"] = node["data"].get("signal", None)

print("Nodos do grafo:", G.nodes(data=True))


source_handle = {}

# laço para obter o nodo fonte e nodo final
for edge in data['edges']:
    source_id = edge['source']
    target_id = edge['target']
    if edge["sourceHandle"] not in source_handle:
        source_handle[edge["sourceHandle"]] = []
    source_handle[edge["sourceHandle"]].append([source_id, target_id])
    G.add_edge(source_id, target_id)


# ------WHILE--------
nodos_entrada = []
var = ''
while var != 'sair':

    # laços aninhados para atribuir valores randoms para as portas de entrada
    for node_id in G.nodes:
        for sucessor_id in G.successors(node_id):
            if G.nodes[sucessor_id]['label'] == 'inport':
                existing_key = next((key for key in G.nodes[sucessor_id] if key != 'label'), None)
                if existing_key:
                    nodos_entrada.append(existing_key)
                    valor = round(5 + (random() * 5), 2)
                    G.nodes[sucessor_id][existing_key] = valor

    # chamando função para obter valores
    dici = find_valores(G, nodos_entrada, node_id='dndnode_0')

    # chamando função para propagar valores no grafo
    propagar_valores(G, dici, source_handle)
    print("Nodos do grafo:", G.nodes(data=True))
    var = input('\nDigite "sair" para encerrar ou qualquer outra tecla para continuar: ').strip().lower()
