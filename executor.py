import threading
import json
import networkx as nx
import matplotlib.pyplot as plt
import random
import time

from globals import socketio

class Executor(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, filename=None):
        threading.Thread.__init__(self, group=group, target=target, name=name)
        self.filename = filename
        self._stop_event = threading.Event()
        self.initilized = False

    def update_input_ports(self, G):
        dirty = False

        if not self.initilized or random.randint(1, 100) < 3:
            self.initilized = True

            for node_id in G.nodes:
                node = G.nodes[node_id]
                if node.get("type") == "inport":
                    text = node.get("data", {}).get("text", "")
                    if 'R' in text:
                        new_value = random.randint(0, 1) 
                    elif text == 'Vi1':
                        new_value = random.uniform(0, 5)
                    elif text == 'Vi2':
                        new_value = random.uniform(0, 10)
                    elif text == 'Li':
                        new_value = random.uniform(0, 20)
                    elif text == 'Di':
                        new_value = random.randint(0, 1)
                    else:
                        new_value = 0
            
                    # Atualiza todas as arestas saindo desse nó
                    for target_id in G.successors(node_id):  
                        edge_data = G.get_edge_data(node_id, target_id)
                
                        if edge_data and edge_data.get("value") != new_value:
                            G.edges[node_id, target_id]["value"] = new_value
                            dirty = True  # Indica que houve mudança
        return dirty


    def plot_graph(self, G):
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
    def recalc_values(self, G):
        # Obtemos a ordem topológica (necessário que o grafo seja acíclico)
        topo_order = list(nx.topological_sort(G))
    
        for node_id in topo_order:
            node_data = G.nodes[node_id]
            node_type = node_data.get("type", "")
            result = None
        
            # Se for um nó de entrada (inport), assumimos que o valor já foi atribuído nas arestas sucessoras.
            if node_type == "inport":
                continue
        
            # Coleta os valores a partir das arestas de entrada conectadas ao nó
            # Alguns nós podem ter mais de uma aresta de entrada, por exemplo o nó de logica.
            parent_values = []
            for parent_id in G.predecessors(node_id):
                edge_data = G.get_edge_data(parent_id, node_id)
                if edge_data is not None and "value" in edge_data:
                    parent_values.append(edge_data["value"])

            """
                Trata nó de acordo com o seu tipo.
            """
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
                #for target_id in G.successors(node_id):
                #    G.edges[node_id, target_id]["value"] = result

            elif node_type == "decision":
                # Pega o operador e o valor de comparação.
                operator = node_data['data'].get('signal')
                compare_value = int(node_data['data'].get('text', 0))

                # Assume que há apenas uma entrada
                parent_value = parent_values[0] if parent_values else None
            
                if operator == "==":
                    result = (parent_value == compare_value)
                elif operator == ">":
                    result = (parent_value > compare_value)
                elif operator == "<":
                    result = (parent_value < compare_value)
                elif operator == ">=":
                    result = (parent_value >= compare_value)
                elif operator == "<=":
                    result = (parent_value <= compare_value)
                elif operator == "!=":
                    result = (parent_value != compare_value)
                else:
                    result = False

                # Propaga o resultado para cada aresta de saída do nó
                #for target_id in G.successors(node_id):
                #    G.edges[node_id, target_id]["value"] = 1 if result_bool else 0            


            elif node_type == "andor":
                # Pega o operador da propriedade signal.
                operator = node_data['data'].get('signal')

                result = False            
                if operator == "and":
                        result = all(parent_values)
                elif operator == "or":
                    result = any(parent_values)

                # Propaga o resultado para cada aresta de saída do nó
                #for target_id in G.successors(node_id):
                #    G.edges[node_id, target_id]["value"] = 1 if result_bool else 0


            elif node_type == "equation":
                # Pega a equação da propriedade text
                equation = node_data['data'].get('text', 0)

                # Assume que há apenas uma entrada
                parent_value = parent_values[0] if parent_values else None
            
                result = eval(equation.format(x=parent_value))

            elif node_type == "switch":
                #Posição 1 é signal, posição 2 é value
                signal = parent_values[1] if parent_values else 0
                parent_value = parent_values[0] if parent_values else None
            
                if signal == 1:
                    result = parent_value
                else:
                    result = 0

            elif node_type == "outport":
                # Para nós de saída, atualiza o campo "value" do nó a partir da aresta de entrada
                node_data["value"] = parent_values[0] if parent_values else None
                result = node_data["value"]


            # Propaga o resultado para cada aresta de saída do nó, assim é possível dar continuidade ao fluxo.
            for target_id in G.successors(node_id):
                G.edges[node_id, target_id]["value"] = result



    def load_graph(self):
        data = None
        with open(self.filename) as file:
            data = json.load(file)

        G = nx.DiGraph()

        for node in data["nodes"]:
            G.add_node(node['id'], **node)

        for edge in data['edges']:
            G.add_edge(edge['source'], edge['target'], value=0, sourceHandle=True if edge['sourceHandle'] == 'true' else False)
        
        return G
    
    def getEdgeValue(self, G):
        edges = []
        
        for u, v, data in G.edges(data=True):
            edge_id = (u, v)
            value = data.get("value")

            if isinstance(value, (float)):
                value = f"{value:.2f}" 

            edges.append((edge_id, value))
        
        return edges

         
    def run(self):
        G = self.load_graph()
        
        start_time = start = time.perf_counter()
        
        while not self._stop_event.is_set():
            
            if (self.update_input_ports(G)):
                
                self.recalc_values(G)

                if time.perf_counter() - start_time > 1:
                    start_time = start = time.perf_counter()
                    e = self.getEdgeValue(G)
                    socketio.emit('update', e)

            time.sleep(0.05)


    def stop(self):
        self._stop_event.set()

