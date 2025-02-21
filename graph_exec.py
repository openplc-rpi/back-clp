import json
import numpy as np
from random import random
import networkx as nx
import matplotlib.pyplot as plt
import random


def update_input_ports(G):
    dirty = False
    for node_id in G.nodes:
        node = G.nodes[node_id]
        
        if node.get("type") == "inport":
            new_value = random.randint(1, 100)  # Gera novo valor aleatório
            
            # Atualiza todas as arestas saindo desse nó
            for target_id in G.successors(node_id):  # Nó destino da aresta
                edge_data = G.get_edge_data(node_id, target_id)
                
                if edge_data and edge_data.get("value") != new_value:
                    G.edges[node_id, target_id]["value"] = new_value
                    dirty = True  # Indica que houve mudança
                
    return dirty


def plot_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G) 
    
    nx.draw(G, pos, with_labels=False, node_color="lightblue", edge_color="gray", node_size=1000, font_size=4)
    
    node_labels = {node: G.nodes[node].get("data", {}).get("label", node) for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=6, font_color="black")
    
    edge_labels = {(u, v): G.edges[u, v].get("value", "") for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color="red")
    
    plt.savefig("grafo.png", dpi=300, bbox_inches="tight")
    

"""
  Recalcula os valores dos nós em ordem topológica,
  utilizando o campo "value" presente na aresta diretamente conectada ao nó.
"""
def recalc_values(G):
    """
    Recalcula os valores dos nós em ordem topológica, 
    propagando o resultado das operações para as arestas de saída do nó.
    """
    # Obtemos a ordem topológica (necessário que o grafo seja acíclico)
    topo_order = list(nx.topological_sort(G))
    
    for node_id in topo_order:
        node_data = G.nodes[node_id]
        node_type = node_data.get("type", "")
        print(f'node_type: {node_type}')
        
        # Se for um nó de entrada (inport), assumimos que o valor já foi atribuído via aresta
        if node_type == "inport":
            continue
        
        # Coleta os valores a partir das arestas de entrada conectadas ao nó
        parent_values = []
        for parent_id in G.predecessors(node_id):
            edge_data = G.get_edge_data(parent_id, node_id)
            if edge_data is not None and "value" in edge_data:
                parent_values.append(edge_data["value"])
        
        print(f'parent_values: {parent_values}')
        
        # Se o nó é do tipo "operation", calculamos o resultado e propagamos para as arestas de saída
        if node_type == "operation":
            operation = node_data['data']['operation']
            value = float(node_data['data']['text'])
            # Para operações, assumimos que há apenas um valor vindo da aresta de entrada
            parent_value = parent_values[0] if parent_values else 0
            
            if operation == "+":
                result = parent_value + value
            elif operation == "*":
                result = parent_value * value
            elif operation == "-":
                result = parent_value - value
            elif operation == "/":
                result = parent_value / value if value != 0 else None
            else:
                result = None

            # Propaga o resultado para cada aresta de saída do nó
            for target_id in G.successors(node_id):
                # Atualiza o campo "value" da aresta que sai de node_id
                G.edges[node_id, target_id]["value"] = result

        elif node_type == "decision":
            # Assume que há apenas uma entrada
            parent_value = parent_values[0] if parent_values else None
            
            # Pega o operador e o valor de comparação da propriedade 'data'
            operator = node_data['data'].get('signal')
            try:
                compare_value = int(node_data['data'].get('text', 0))
            except (ValueError, TypeError):
                compare_value = 0
            
            # Realiza a comparação; se parent_value for None, consideramos como False
            if parent_value is None:
                result_bool = False
            else:
                if operator == "==":
                    result_bool = (parent_value == compare_value)
                elif operator == ">":
                    result_bool = (parent_value > compare_value)
                elif operator == "<":
                    result_bool = (parent_value < compare_value)
                elif operator == ">=":
                    result_bool = (parent_value >= compare_value)
                elif operator == "<=":
                    result_bool = (parent_value <= compare_value)
                elif operator == "!=":
                    result_bool = (parent_value != compare_value)
                else:
                    result_bool = False

            print(f'Decision node {node_id}: {parent_value} {operator} {compare_value} evaluates to {result_bool}')

            for target_id in G.successors(node_id):
                G.edges[node_id, target_id]["value"] = 1 if result_bool else 0            

        elif node_type == "andor":
            # Pega o operador e o valor de comparação da propriedade 'data'
            operator = node_data['data'].get('signal')

            result_bool = False            
            if operator == "and":
                    result_bool = all(parent_values)
            elif operator == "or":
                    result_bool = any(parent_values)

            for target_id in G.successors(node_id):
                G.edges[node_id, target_id]["value"] = 1 if result_bool else 0

            print(f'Logic node {node_id}: {parent_values} {operator} evaluates to {result_bool}')

        elif node_type == "outport":
            # Para nós de saída, atualiza o campo "value" do nó a partir da aresta de entrada
            node_data["value"] = parent_values[0] if parent_values else None
            # Propaga o resultado para cada aresta de saída do nó
            for target_id in G.successors(node_id):
                # Atualiza o campo "value" da aresta que sai de node_id
                G.edges[node_id, target_id]["value"] = node_data["value"]


        else:
            # Para outros tipos, podemos definir outro comportamento ou simplesmente não fazer nada
            pass


data = None
with open("projects/simple1.flow") as file:
    data = json.load(file)

G = nx.DiGraph()

for node in data["nodes"]:
    G.add_node(node['id'], **node)

for edge in data['edges']:
    G.add_edge(edge['source'], edge['target'], value=0, sourceHandle= True if edge['sourceHandle'] == 'true' else False)

print(update_input_ports(G))

recalc_values(G)

plot_graph(G)









# laço para obter o nodo fonte e nodo final
"""
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
"""