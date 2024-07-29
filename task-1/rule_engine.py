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
        stack = []
        operators = []

        for token in tokens:
            if token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    right = stack.pop()
                    left = stack.pop()
                    op = operators.pop()
                    stack.append(Node("operator", value=op, left=left, right=right))
                operators.pop()  # remove the '('
            elif token in ['AND', 'OR']:
                while operators and operators[-1] in ['AND', 'OR']:
                    right = stack.pop()
                    left = stack.pop()
                    op = operators.pop()
                    stack.append(Node("operator", value=op, left=left, right=right))
                operators.append(token)
            elif token in ['>', '<', '>=', '<=', '=', '==']:
                operators.append(token)
            else:
                stack.append(Node("operand", value=token))

            # Handle comparison operations immediately
            if len(stack) == 2 and operators and operators[-1] in ['>', '<', '>=', '<=', '=', '==']:
                right = stack.pop()
                left = stack.pop()
                op = operators.pop()
                # Normalize '=' to '=='
                if op == '=':
                    op = '=='
                stack.append(Node("operator", value=op, left=left, right=right))

        while operators:
            right = stack.pop()
            left = stack.pop()
            op = operators.pop()
            stack.append(Node("operator", value=op, left=left, right=right))

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

def evaluate_rule(ast: Node, data: Dict[str, Union[int, str]]) -> bool:
    def convert_value(value):
        if isinstance(value, str):
            value = value.strip("'\"")
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

        if ast.value == "AND":
            return left_value and right_value
        elif ast.value == "OR":
            return left_value or right_value
        elif ast.value == "==":
            return left_value == right_value
        elif ast.value == ">":
            return left_value > right_value
        elif ast.value == "<":
            return left_value < right_value
        elif ast.value == ">=":
            return left_value >= right_value
        elif ast.value == "<=":
            return left_value <= right_value
        else:
            raise ValueError(f"Unknown operator: {ast.value}")

    raise ValueError(f"Invalid AST node type: {ast.type}")