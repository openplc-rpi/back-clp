import time

class NodeProcessor:
    def __init__(self, node_data, parent_values):
        self.node_data = node_data
        self.parent_values = parent_values

    def process(self):
        return None
    
class ProporcionalNode(NodeProcessor):
    def process(self):
        print("Dados do nó:", self.node_data)  # Verifique os dados recebidos pelo nó
        kp = float(self.node_data['data'].get('text', 1))
        parent_value = self.parent_values[0] if self.parent_values else 0

        result = kp * parent_value
        print(f"kp: {kp}, parent_value: {parent_value}, result: {result}")
        return result
    

class DerivativeNode(NodeProcessor):
    def __init__(self, node_data, parent_values):
        super().__init__(node_data, parent_values)
        # Se a variável 'prev_value' ainda não existe, inicialize ela
        if not hasattr(self, 'prev_value'):
            self.prev_value = 0
            self.ts = 0.1  # Definindo um intervalo de amostragem de 10ms (100 Hz)
            self.flag = False
            #self.prev_time = time.perf_counter()
            #self.kd = float(node_data.get('data', {}).get('kd', 1))  # KD vindo dos dados do nó (padrão 1)

    def process(self):
        #current_time = time.perf_counter()
        kd = float(self.node_data.get('data', {}).get('kd', 1))
        current_value = self.parent_values[0] if self.parent_values else 0

        # Se for a primeira execução, inicialize as variáveis e retorne 0
        if not hasattr(self, 'prev_value'):
             self.prev_value = current_value
        #    self.prev_time = current_time
        #    print(f"Inicializando DerivativeNode. prev_value: {self.prev_value}, prev_time: {self.prev_time}")
        #    return 0
        print(self.prev_value)
        # Calcula a derivada (valor atual - valor anterior) / (tempo atual - tempo anterior)
        delta_value = current_value - self.prev_value
        #delta_time = current_time - self.prev_time
    
        # Calcula o termo derivativo (KD * derivada)
        derivative = (delta_value / self.ts) if self.ts > 0 else 0
        result = kd * derivative


        # Atualiza os valores anteriores
        self.prev_value = current_value
        
        #self.prev_time = current_time

        # Retorna o valor calculado com KD
        return result




class OperationNode(NodeProcessor):
    def process(self):
        operation = self.node_data['data']['operation']
        op1 = self.parent_values[0] if self.parent_values else 0
        op2 = self.parent_values[1] if self.parent_values else 0

        if operation == "+":
            return op1 + op2
        elif operation == "*":
            return op1 * op2
        elif operation == "-":
            return op1 - op2
        elif operation == "/":
            return op1 / op2 if op2 != 0 else None
        
        return None

class DecisionNode(NodeProcessor):
    def process(self):
        operator = self.node_data['data'].get('signal')
        compare_value = float(self.node_data['data'].get('text', 0))
        parent_value = self.parent_values[0] if self.parent_values else None

        operators = {
            "==": parent_value == compare_value,
            ">": parent_value > compare_value,
            "<": parent_value < compare_value,
            ">=": parent_value >= compare_value,
            "<=": parent_value <= compare_value,
            "!=": parent_value != compare_value
        }
        return operators.get(operator, False)

class AndOrNode(NodeProcessor):
    def process(self):
        operator = self.node_data['data'].get('signal')
        if operator == "and":
            return all(self.parent_values)
        elif operator == "or":
            return any(self.parent_values)
        elif operator == "xor":
            return sum(self.parent_values) % 2 == 1        
        return False

class EquationNode(NodeProcessor):
    def process(self):
        equation = self.node_data['data'].get('text', "0")
        parent_value = self.parent_values[0] if self.parent_values else None
        return eval(equation.format(x=parent_value))

class SwitchNode(NodeProcessor):
    def process(self):
        signal = self.parent_values[1] if len(self.parent_values) > 1 else 0
        parent_value = self.parent_values[0] if self.parent_values else None
        return parent_value if signal == 1 else 0

class OutportNode(NodeProcessor):
    def process(self):
        return self.parent_values[0] if self.parent_values else None
    
