import threading
import json
import networkx as nx
import random
import time
import platform
import math

from globals import socketio, ParseConfig
from nodes import   (OperationNode, DecisionNode, AndOrNode, 
                    EquationNode, SwitchNode, OutportNode, 
                    NodeProcessor, ValueOf, PID,
                    ReferenceValue)

def is_raspberry_pi():
    return platform.machine().startswith('arm')

if is_raspberry_pi():
    import RPi.GPIO as GPIO
    from n4dba06Drv import N4dba06Controller

OutPutPort_Proprierties = {
    "Vo1": {
        "min": 0.05,
        "max": 5,
    },
    "Vo2": {
        "min": 0.1,
        "max": 10,
    },
}

NODE_CLASSES = {
    "operation": OperationNode,
    "decision": DecisionNode,
    "andor": AndOrNode,
    "equation": EquationNode,
    "switch": SwitchNode,
    "outport": OutportNode,
    "valueof": ValueOf,
    "pid": PID,
    "reference": ReferenceValue
}

UPDATE_INTERVAL = 0.001

class Executor(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None, filename=None):
        threading.Thread.__init__(self, group=group, target=target, name=name)
        self.filename = filename
        self._stop_event = threading.Event()
        self.initilized = False
        
        self.last_update = 0
        self.n4dba06 = None
        self.update = self.update_input_ports_random

        if is_raspberry_pi():
            serial_port = ParseConfig('serial', 'port')
            self.n4dba06 = N4dba06Controller(serial_port)

            GPIO.setmode(GPIO.BCM)
            self.update = self.update_input_ports


    def get_bounded_random(self, current_value, delta=0.5, min_value=0.0, max_value=5.0):
        lower_bound = max(current_value - delta, min_value)
        upper_bound = min(current_value + delta, max_value)
        return random.uniform(lower_bound, upper_bound)


    def update_input_ports_random(self, G):
        dirty = False

        if not self.initilized or random.randint(1, 100) < 2:
            self.initilized = True

            for node_id in G.nodes:
                node = G.nodes[node_id]
                if node.get("type") == "inport":
                    text = node.get("data", {}).get("text", "")
                    value = float(node.get("data", {}).get("value", 0))
                    if 'R' in text:
                        new_value = random.randint(0, 1) 
                    elif text == 'Vi1':
                        new_value = self.get_bounded_random(value, 0.1, 0.05, 5)
                    elif text == 'Vi2':
                        new_value = self.get_bounded_random(value, 0.1, 0.1, 10)
                    elif text == 'Li':
                        new_value = random.uniform(0, 20)
                    elif text == 'Di':
                        new_value = random.randint(0, 1)
                    else:
                        new_value = 0

                    node['data']["value"] = new_value
            
                    # Atualiza todas as arestas saindo desse nó
                    for target_id in G.successors(node_id):  
                        edge_data = G.get_edge_data(node_id, target_id)
                
                        if edge_data and edge_data.get("value") != new_value:
                            G.edges[node_id, target_id]["value"] = new_value
                            dirty = True  # Indica que houve mudança
        return dirty

    def update_input_ports(self, G):
        dirty = False

        for node_id in G.nodes:
            node = G.nodes[node_id]
            if node.get("type") == "inport":
                text = node.get("data", {}).get("text", "")
                if 'GPIO' in text:
                    gpio = int(text.removeprefix("GPIO"))
                    new_value = GPIO.input(gpio)
                else:
                    new_value = self.n4dba06.read_port(text)
            
                # Atualiza todas as arestas saindo desse nó
                for target_id in G.successors(node_id):  
                    edge_data = G.get_edge_data(node_id, target_id)
                
                    if edge_data and edge_data.get("value") != new_value:
                        G.edges[node_id, target_id]["value"] = new_value
                        dirty = True  # Indica que houve mudança
        
        return dirty
    

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
            
            # Se for um nó de entrada (inport), assumimos que o valor já foi atribuído nas arestas sucessoras.
            # Se for um no valueof, deverá ser processado o final. 
            if node_type == "inport":
                continue
        
            # Coleta os valores a partir das arestas de entrada conectadas ao nó
            # Alguns nós podem ter mais de uma aresta de entrada, por exemplo o nó de logica.
            parent_values = [
                G.get_edge_data(parent_id, node_id).get("value", None)
                for parent_id in G.predecessors(node_id)
                if G.get_edge_data(parent_id, node_id) is not None
            ]
         
            #Calcula o resultado do nó
            result = node_data["logic"].process(parent_values)

            #Se for outport, envia o valor para o dispositivo
            if node_type == 'outport':
                text = node_data.get("data", {}).get("text", "")
                G.nodes[node_id]["data"]["value"] = result
                if is_raspberry_pi():
                    if 'GPIO' in text:
                        gpio = int(text.removeprefix("GPIO"))
                        GPIO.output(gpio, result)
                    else:
                        self.n4dba06.write_port(text, result)


            # Propaga o resultado para cada aresta de saída do nó, assim é possível dar continuidade ao fluxo.
            for target_id in G.successors(node_id):
                G.edges[node_id, target_id]["value"] = result
                                

    def load_graph(self):
        data = None
        with open(self.filename) as file:
            data = json.load(file)

        G = nx.DiGraph()

        for node in data["nodes"]:
            NodeClass = NODE_CLASSES.get(node['type'], NodeProcessor)
            node['logic'] = NodeClass(node, G)
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

    def configure_rpi_gpio(self, G):
        for node_id in G.nodes:
            node = G.nodes[node_id]
            if node.get("type") == "inport":
                text = node.get("data", {}).get("text", "")
                if 'GPIO' in text:
                    gpio = int(text.removeprefix("GPIO"))
                    GPIO.setup(gpio, GPIO.IN)
            elif node.get("type") == "outport":
                text = node.get("data", {}).get("text", "")
                if 'GPIO' in text:
                    gpio = int(text.removeprefix("GPIO"))
                    GPIO.setup(gpio, GPIO.OUT)


         
    def run(self):
        G = self.load_graph()
        
        if is_raspberry_pi():
            self.configure_rpi_gpio(G)
        
        start_time = start = time.perf_counter()
        
        while not self._stop_event.is_set():
            
            self.update(G)
                
            self.recalc_values(G)

            if time.perf_counter() - start_time > 0.1:
                start_time = start = time.perf_counter()
                e = self.getEdgeValue(G)
                socketio.emit('update', e)
                   
            time.sleep(UPDATE_INTERVAL)


    def stop(self):
        self._stop_event.set()

