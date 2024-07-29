import re
from typing import Dict, List, Union, Tuple

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        if self.type == "operand":
            return f"Node('operand', value='{self.value}')"
        elif self.type == "operator":
            return f"Node('operator', {self.left}, {self.right}, value='{self.value}')"
        else:
            return f"Node({self.type}, {self.value}, {self.left}, {self.right})"

def create_rule(rule_string: str) -> Node:
    def parse_expression(tokens: List[str]) -> Node:
        output_queue = []
        operator_stack = []
        
        precedence = {
            'OR': 1,
            'AND': 2,
            '>': 3, '<': 3, '>=': 3, '<=': 3, '=': 3, '==': 3
        }

        def pop_greater_precedence(op):
            while (operator_stack and operator_stack[-1] != '(' and 
                   precedence.get(operator_stack[-1], 0) >= precedence.get(op, 0)):
                output_queue.append(operator_stack.pop())

        for token in tokens:
            if token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output_queue.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    raise ValueError("Mismatched parentheses")
            elif token in precedence:
                pop_greater_precedence(token)
                operator_stack.append(token)
            else:
                output_queue.append(Node("operand", value=token))

        while operator_stack:
            if operator_stack[-1] == '(':
                raise ValueError("Mismatched parentheses")
            output_queue.append(operator_stack.pop())

        stack = []
        for item in output_queue:
            if isinstance(item, Node):
                stack.append(item)
            else:  # operator
                if len(stack) < 2:
                    raise ValueError(f"Invalid expression: not enough operands for {item}")
                right = stack.pop()
                left = stack.pop()
                stack.append(Node("operator", value=item, left=left, right=right))

        if len(stack) != 1:
            raise ValueError("Invalid expression")

        return stack[0]

    tokens = re.findall(r'\(|\)|\w+|[<>=]+|\'[^\']*\'', rule_string)
    return parse_expression(tokens)

def combine_rules(rules: List[str], operator="OR") -> Node:
    if not rules:
        return None

    rule_asts = [create_rule(rule) for rule in rules]

    combined_ast = rule_asts[0]
    for ast in rule_asts[1:]:
        combined_ast = Node("operator", value=operator, left=combined_ast, right=ast)

    return combined_ast

def evaluate_rule(ast: Node, data: Dict[str, Union[int, str, float]]) -> bool:
    def convert_value(value):
        if isinstance(value, str):
            value = value.strip("'\"")
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value
        return value

    if ast.type == "operand":
        return convert_value(data.get(ast.value, ast.value))

    if ast.type == "operator":
        left_value = evaluate_rule(ast.left, data)
        right_value = evaluate_rule(ast.right, data)

        # Convert both values to the same type for comparison
        left_value = convert_value(left_value)
        right_value = convert_value(right_value)

        if ast.value == "AND":
            return bool(left_value) and bool(right_value)
        elif ast.value == "OR":
            return bool(left_value) or bool(right_value)
        elif ast.value in ["==", "="]:
            return left_value == right_value
        elif ast.value == ">":
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return left_value > right_value
            else:
                return str(left_value) > str(right_value)
        elif ast.value == "<":
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return left_value < right_value
            else:
                return str(left_value) < str(right_value)
        elif ast.value == ">=":
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return left_value >= right_value
            else:
                return str(left_value) >= str(right_value)
        elif ast.value == "<=":
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return left_value <= right_value
            else:
                return str(left_value) <= str(right_value)
        else:
            raise ValueError(f"Unknown operator: {ast.value}")

    raise ValueError(f"Invalid AST node type: {ast.type}")

# Sample rules
rule1 = "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)"
rule2 = "(age > 30 AND department = 'Marketing') AND (salary > 20000 OR experience > 5)"

# Create ASTs for both rules
ast1 = create_rule(rule1)
ast2 = create_rule(rule2)

# Combine rules using OR
combined_ast = combine_rules([rule1, rule2], operator="OR")

# Represent rules as a list of tuples
rules = [
    ('Rule 1', repr(ast1)),
    ('Rule 2', repr(ast2)),
    ('Combined Rule', repr(combined_ast))
]

# Print the rules and their AST representations
for rule_name, rule_ast in rules:
    print(f"{rule_name}: {rule_ast}")
