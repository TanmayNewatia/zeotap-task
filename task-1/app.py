from flask import Flask, request, jsonify
import sqlite3
import json
import re
from typing import Dict, List, Union, Tuple
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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

def create_rule_fun(rule_string: str) -> Node:
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

    rule_asts = [create_rule_fun(rule) for rule in rules]

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

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    data = data["data"]
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name, age, department, income, experience) VALUES (?, ?, ?, ?, ?)',
                 (data['name'], data['age'], data['department'], data['income'], data['experience']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'User created successfully'}), 201

@app.route('/rules', methods=['POST'])
def create_rule():
    data = request.get_json()
    data = data['data']
    conn = get_db_connection()
    conn.execute('INSERT INTO rules (name, condition) VALUES (?, ?)',
                 (data['name'], data['condition']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Rule created successfully'}), 201

@app.route('/evaluate/<int:user_id>', methods=['GET'])
def evaluate_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    
    rules = conn.execute('SELECT * FROM rules').fetchall()
    conn.close()
    
    user_dict = dict(user)
    for rule in rules:
        rule_ast = create_rule_fun(rule["condition"])
        
        # Add 'salary' and 'experience' to user_dict if not present
        if 'salary' not in user_dict:
            user_dict['salary'] = user_dict.get('income', 0)
        if 'experience' not in user_dict:
            user_dict['experience'] = 0  # Assume 0 if not provided
        if evaluate_rule(rule_ast, user_dict):
            return jsonify({'eligible': True}), 200
    return jsonify({'eligible': False}), 200

@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    data = request.get_json()
    rule_string = data.get('rule_string')
    if not rule_string:
        return jsonify({'error': 'rule_string is required'}), 400

    try:
        rule_ast = create_rule_fun(rule_string)
        return jsonify({'rule_ast': repr(rule_ast)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    data = request.get_json()
    rules = data.get('rules')
    if not rules:
        return jsonify({'error': 'rules list is required'}), 400

    try:
        combined_ast = combine_rules(rules)
        return jsonify({'combined_rule_ast': repr(combined_ast)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    data = request.get_json()
    rule_ast_json = data.get('rule_ast')
    user_data = data.get('data')
    if not rule_ast_json or not user_data:
        return jsonify({'error': 'rule_ast and data are required'}), 400

    try:
        rule_ast = json.loads(rule_ast_json, object_hook=lambda d: Node(**d))
        result = evaluate_rule(rule_ast, user_data)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
