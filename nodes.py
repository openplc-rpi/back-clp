import time

class NodeProcessor:
    def __init__(self, node_data, G):
        self.node_data = node_data
        self.G = G

    def process(self, parent_values):
        return None

class PID(NodeProcessor):
    def __init__(self, node_data, G):
        super().__init__(node_data, G)

        self.erro = 0.0
        self.erro_d = 0.0
        self.erro_int = 0.0
        self.erro_ant = 0.0
        self.erro_int_ant = 0.0
        self.ts = 0.05
    
    def process(self, parent_values):
        Kp = float(self.node_data['data'].get('P', 0))
        Ki = float(self.node_data['data'].get('I', 0))
        Kd = float(self.node_data['data'].get('D', 0))

        self.erro = parent_values[0] if parent_values else 0

        self.erro_int = self.erro_int_ant + ((self.erro + self.erro_ant) * self.ts / 2)  # integração trapezoidal
        self.erro_int_ant = self.erro_int

        self.erro_d = (self.erro - self.erro_ant) / self.ts  # derivada
        self.erro_ant = self.erro

        result = self.erro * Kp + self.erro_int * Ki + self.erro_d * Kd  # saída PID

        return result


class ProporcionalNode(NodeProcessor):
    def process(self, parent_values):
        kp = float(self.node_data['data'].get('text', 1))
        parent_value = parent_values[0] if parent_values else 0
        result = kp * parent_value

        return result
    



class OperationNode(NodeProcessor):
    def process(self, parent_values):
        operation = self.node_data['data']['operation']
        op1 = parent_values[0] if parent_values else 0
        op2 = parent_values[1] if parent_values else 0

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
    def process(self, parent_values):
        operator = self.node_data['data'].get('signal')
        compare_value = float(self.node_data['data'].get('text', 0))
        parent_value = parent_values[0] if parent_values else None

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
    def process(self, parent_values):
        operator = self.node_data['data'].get('signal')
        if operator == "and":
            return all(parent_values)
        elif operator == "or":
            return any(parent_values)
        elif operator == "xor":
            return sum(parent_values) % 2 == 1        
        return False

class EquationNode(NodeProcessor):
    def process(self, parent_values):
        equation = self.node_data['data'].get('text', "0")
        parent_value = parent_values[0] if parent_values else None
        return eval(equation.format(x=parent_value))

class SwitchNode(NodeProcessor):
    def process(self, parent_values):
        signal = parent_values[1] if len(parent_values) > 1 else 0
        parent_value = parent_values[0] if parent_values else None
        return parent_value if signal == 1 else 0

class OutportNode(NodeProcessor):
    def process(self, parent_values):
        return parent_values[0] if parent_values else 0

    
class ValueOf(NodeProcessor):
    def __init__(self, node_data, G):
        self.node_data = node_data
        self.G = G

    def process(self, parent_values):
        ret = 0
        text = self.node_data.get("data", {}).get("text", "")
        for node_id in self.G.nodes:
            node = self.G.nodes[node_id]
            if node.get("data", {}).get("text", "") == text and node.get("type") == "outport":
                ret = node.get("data", {}).get("value", 0)
                break

        ret = 0.0 if ret is None else ret

        return ret

class ReferenceValue(NodeProcessor):
    def __init__(self, node_data, G):
        self.node_data = node_data
        self.G = G

    def process(self, parent_values):
        ret = float(self.node_data.get("data", {}).get("text", "0"))
        ret = 0.0 if ret is None else ret
        return ret
