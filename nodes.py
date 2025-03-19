
class NodeProcessor:
    def __init__(self, node_data, parent_values):
        self.node_data = node_data
        self.parent_values = parent_values

    def process(self):
        return None

class OperationNode(NodeProcessor):
    def process(self):
        operation = self.node_data['data']['operation']
        value = float(self.node_data['data']['text'])
        parent_value = self.parent_values[0] if self.parent_values else 0

        if operation == "+":
            return parent_value + value
        elif operation == "*":
            return parent_value * value
        elif operation == "-":
            return parent_value - value
        elif operation == "/":
            return parent_value / value if value != 0 else None
        return None

class DecisionNode(NodeProcessor):
    def process(self):
        operator = self.node_data['data'].get('signal')
        compare_value = int(self.node_data['data'].get('text', 0))
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