import re
import os

TOKENS = {
    'FOR': r'\bfor\b',  
    'IN': r'\bin\b',    
    'LET': r'\blet\b',
    'PRINT': r'\bprint\b',
    'INPUT': r'\binput\b',
    'IF': r'\bif\b',
    'ELSE': r'\belse\b',
    'WHILE': r'\bwhile\b',
    'DO': r'\bdo\b',
    'FUNCTION': r'\bfunction\b',
    'RETURN': r'\breturn\b',
    'END': r'\bend\b',
    'NUMBER': r'\b\d+\b',
    'LOGICAL': r'\b(and|or|not)\b',
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    'OPERATOR': r'[+\-*/^]',
    'COMPARISON': r'[><=]+',
    'COMMA': r',',
    'OPEN_PAREN': r'\(',
    'CLOSE_PAREN': r'\)',
    'LIST_START': r'\[',
    'LIST_END': r'\]',
}

def lexer(code):
    tokens = []
    code = code.strip()
    while code:
        match = None
        for token_type, pattern in TOKENS.items():
            regex = re.compile(pattern)
            match = regex.match(code)
            if match:
                token = (token_type, match.group(0))
                tokens.append(token)
                print(f"Token encontrado: {token}")  # Debug print
                code = code[match.end():]
                code = code.strip()
                break
        if not match:
            raise SyntaxError(f"Token desconhecido: {code[:10]}")
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.variables = {}
        self.functions = {}
        self.return_value = None
        self.in_function = False

    def parse_end(self):
        self.position += 1

    def parse(self):  
        while self.position < len(self.tokens):
            token_type, value = self.tokens[self.position]
            if token_type == 'LET':
                self.parse_let()
            elif token_type == 'PRINT':
                self.parse_print()
            elif token_type == 'INPUT':
                self.parse_input()
            elif token_type == 'IF':
                self.parse_if()
            elif token_type == 'WHILE':
                self.parse_while()
            elif token_type == 'FUNCTION':
                self.parse_function()
            elif token_type == 'FOR':
                self.parse_for()
            elif token_type == 'RETURN':
                if self.in_function:
                    self.parse_return()
                else:
                    raise SyntaxError("Comando 'return' fora de uma função")
            elif token_type == 'IDENTIFIER':
                next_token = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else (None, None)
                if next_token[0] == 'OPEN_PAREN':
                    self.parse_function_call(value)
                elif next_token[1] == '=':
                    self.parse_assignment()
                else:
                    raise SyntaxError(f"Comando inválido: {value}")
            elif token_type == 'END':
                if self.in_function:
                    self.position += 1
                    break
                else:
                    self.parse_end()
            else:
                raise SyntaxError(f"Comando inválido: {value}")
            
    def parse_let(self):
        self.position += 1
        var_name = self.tokens[self.position][1]
        self.position += 1
        if self.position >= len(self.tokens) or self.tokens[self.position][1] != '=':
            raise SyntaxError("Erro de sintaxe em declaração de variável")
        self.position += 1
        value = self.evaluate_expression()
        self.variables[var_name] = value

    def parse_print(self):
        self.position += 1
        value = self.evaluate_expression()
        print("Saída:", value)

    def parse_input(self):
        self.position += 1
        var_name = self.tokens[self.position][1]
        self.position += 1
        user_input = input("Entrada: ")
        try:
            self.variables[var_name] = int(user_input)
        except ValueError:
            raise SyntaxError("Entrada inválida: esperado um número inteiro.")

    def parse_if(self):
        self.position += 1  # Pula o token 'IF'
        
        # Coleta os tokens da condição até encontrar um token que indica o início do bloco
        condition_tokens = []
        while self.position < len(self.tokens) and self.tokens[self.position][0] not in ('LET', 'PRINT', 'INPUT', 'IF', 'ELSE', 'WHILE', 'DO', 'FUNCTION', 'RETURN', 'END'):
            condition_tokens.append(self.tokens[self.position])
            self.position += 1
        
        # Avalia a condição usando um sub-parser
        condition_parser = Parser(condition_tokens)
        condition_parser.variables = self.variables.copy()
        condition_parser.functions = self.functions
        condition_result = condition_parser.evaluate_condition()
        
        if condition_result:
            # Executa o bloco 'if'
            if self.position < len(self.tokens) and self.tokens[self.position][0] == 'END':
                self.position += 1
                return
            self.parse()
        else:
            # Pula o bloco 'if' até encontrar 'ELSE' ou 'END'
            while self.position < len(self.tokens) and self.tokens[self.position][0] not in ('ELSE', 'END'):
                self.position += 1
            if self.position < len(self.tokens) and self.tokens[self.position][0] == 'ELSE':
                self.position += 1
                self.parse()
        
        # Pula o token 'END'
        if self.position < len(self.tokens) and self.tokens[self.position][0] == 'END':
            self.position += 1

    def parse_while(self):
        self.position += 1
        condition_tokens = []
        
        # Coleta os tokens da condição até encontrar 'DO' ou um comando
        while self.position < len(self.tokens):
            current_token = self.tokens[self.position][0]
            if current_token == 'DO':
                self.position += 1  # Pula o 'DO' se existir
                break
            elif current_token in ('LET', 'PRINT', 'INPUT', 'IF', 'ELSE', 'WHILE', 'FUNCTION', 'RETURN'):
                break
            condition_tokens.append(self.tokens[self.position])
            self.position += 1
        
        # Coleta os tokens do corpo do loop até encontrar 'END'
        loop_body_tokens = []
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END':
            loop_body_tokens.append(self.tokens[self.position])
            self.position += 1
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END':
            raise SyntaxError("Esperado 'end' para fechar o loop 'while'")
        
        self.position += 1  # Pula o token 'END'
        
        while True:
            # Avalia a condição usando um sub-parser
            condition_parser = Parser(condition_tokens)
            condition_parser.variables = self.variables.copy()
            condition_parser.functions = self.functions
            condition_result = condition_parser.evaluate_condition()
            
            if not condition_result:
                break
            
            # Executa o corpo do loop usando um sub-parser
            loop_parser = Parser(loop_body_tokens)
            loop_parser.variables = self.variables.copy()
            loop_parser.functions = self.functions
            loop_parser.parse()
            self.variables.update(loop_parser.variables)

    def parse_function(self):
        self.position += 1
        func_name = self.tokens[self.position][1]
        self.position += 1
        parameters = []
    
        if self.tokens[self.position][0] == 'OPEN_PAREN':
            self.position += 1
            while self.tokens[self.position][0] != 'CLOSE_PAREN':
                if self.tokens[self.position][0] == 'IDENTIFIER':
                    parameters.append(self.tokens[self.position][1])
                    self.position += 1
                    if self.tokens[self.position][0] == 'COMMA':
                        self.position += 1
                else:
                    raise SyntaxError("Parâmetros inválidos na definição da função")
            self.position += 1  # Pula ')'
        else:
            raise SyntaxError("Esperado '(' após o nome da função")
    
        func_body_tokens = []
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END':
            func_body_tokens.append(self.tokens[self.position])
            self.position += 1
    
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END':
            raise SyntaxError("Esperado 'end' para fechar a função")
    
        self.position += 1  # Pula o token 'END'
    
        self.functions[func_name] = {
            'parameters': parameters,
            'body': func_body_tokens
        }

    def parse_return(self):
        self.position += 1
        self.return_value = self.evaluate_expression()
        self.position = len(self.tokens)  # Interrompe a execução atual

    def parse_function_call(self, func_name):
        self.position += 1  # Pula o nome da função
        args = []
    
        if self.tokens[self.position][0] == 'OPEN_PAREN':
            self.position += 1  # Pula '('
            while self.tokens[self.position][0] != 'CLOSE_PAREN':
                arg = self.evaluate_expression()
                args.append(arg)
                if self.tokens[self.position][0] == 'COMMA':
                    self.position += 1  # Pula ','
            self.position += 1  # Pula ')'
        else:
            raise SyntaxError("Esperado '(' após o nome da função")
    
        if func_name not in self.functions:
            raise NameError(f"Função não definida: {func_name}")
    
        function = self.functions[func_name]
        if len(args) != len(function['parameters']):
            raise SyntaxError("Número incorreto de argumentos na chamada da função")
    
        func_parser = Parser(function['body'])
        func_parser.variables = self.variables.copy()
        func_parser.functions = self.functions
        func_parser.in_function = True
    
        for param, arg in zip(function['parameters'], args):
            func_parser.variables[param] = arg
    
        func_parser.parse()
    
        return_value = func_parser.return_value
    
        return return_value

    def parse_assignment(self):
        var_name = self.tokens[self.position][1]
        self.position += 1  # Pula o identificador
        self.position += 1  # Pula o '='
        value = self.evaluate_expression()
        self.variables[var_name] = value

    def evaluate_expression(self):
        result = self.get_term()
        while self.position < len(self.tokens) and \
              self.tokens[self.position][0] in ('OPERATOR', 'LOGICAL', 'COMPARISON'):
            operator = self.tokens[self.position][1]
            self.position += 1
            right = self.get_term()
            result = self.apply_operator(result, operator, right)
        return result

    def get_term(self):
        token_type, value = self.tokens[self.position]
        if token_type == 'LIST_START':
            return self.parse_list()
        elif token_type == 'NUMBER':
            self.position += 1
            return int(value)
        elif token_type == 'IDENTIFIER':
            next_token = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else (None, None)
            if next_token[0] == 'OPEN_PAREN':
                result = self.parse_function_call(value)
                return result
            else:
                self.position += 1
                if value in self.variables:
                    return self.variables[value]
                else:
                    raise NameError(f"Variável não definida: {value}")
        elif token_type == 'OPEN_PAREN':
            self.position += 1
            value = self.evaluate_expression()
            if self.tokens[self.position][0] != 'CLOSE_PAREN':
                raise SyntaxError("Esperado ')' na expressão")
            self.position += 1  # Pula ')'
            return value
        else:
            raise SyntaxError(f"Expressão inválida: {value}")

    def parse_list(self):
        self.position += 1  # Skip '['
        elements = []
        
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'LIST_END':
            value = self.evaluate_expression()
            elements.append(value)
            
            if self.position < len(self.tokens) and self.tokens[self.position][0] == 'COMMA':
                self.position += 1
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'LIST_END':
            raise SyntaxError("Lista não fechada: esperado ']'")
            
        self.position += 1  # Skip ']'
        return elements

    def evaluate_condition(self):
        return self.evaluate_expression()

    def apply_operator(self, left, operator, right):
        if operator == '+':
            if isinstance(left, list) or isinstance(right, list):
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                elif isinstance(left, list):
                    return left + [right]
                else:
                    return [left] + right
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            return left / right
        elif operator == '^':
            return left ** right
        elif operator == '>':
            return left > right
        elif operator == '<':
            return left < right
        elif operator == '==':
            return left == right
        elif operator == 'and':
            return left and right
        elif operator == 'or':
            return left or right
        elif operator == 'not':
            return not right
        else:
            raise SyntaxError(f"Operador desconhecido: {operator}")

    def parse_for(self):
        self.position += 1  # Pula 'for'
        
        # Pega o nome da variável de iteração
        if self.tokens[self.position][0] != 'IDENTIFIER':
            raise SyntaxError("Esperado um identificador após 'for'")
        iterator_var = self.tokens[self.position][1]
        self.position += 1
        
        # Verifica a palavra 'in'
        if self.tokens[self.position][0] != 'IN':
            raise SyntaxError("Esperado 'in' após o identificador no laço for")
        self.position += 1
        
        # Avalia a expressão que gera a sequência (lista)
        sequence = self.evaluate_expression()
        if not isinstance(sequence, list):
            raise TypeError("For precisa de uma lista para iterar")
        
        # Coleta os tokens do corpo do loop até encontrar 'END'
        loop_body_tokens = []
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END':
            loop_body_tokens.append(self.tokens[self.position])
            self.position += 1
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END':
            raise SyntaxError("Esperado 'end' para fechar o laço 'for'")
        
        self.position += 1  # Pula o token 'END'
        
        # Executa o corpo do loop para cada elemento da sequência
        for item in sequence:
            # Cria um novo parser para cada iteração
            loop_parser = Parser(loop_body_tokens)
            loop_parser.variables = self.variables.copy()
            loop_parser.functions = self.functions
            
            # Define a variável de iteração
            loop_parser.variables[iterator_var] = item
            
            # Executa o corpo do loop
            loop_parser.parse()
            
            # Atualiza as variáveis do escopo externo
            self.variables.update(loop_parser.variables)

def suggest_correction(error_message, code_lines):
    suggestion = {
        "Token desconhecido": "Verifique a sintaxe do seu código.",
        "Erro de sintaxe em declaração de variável": "Certifique-se de usar 'let' para declarar variáveis e '=' para atribuir valores.",
        "Variável não definida": "Verifique se a variável foi declarada antes de usá-la.",
        "Função não definida": "Verifique se a função foi declarada antes de chamá-la.",
        "Expressão inválida": "Verifique a expressão para garantir que está correta.",
        "Operador desconhecido": "Use operadores válidos como +, -, *, /, >, <, ==, and, or, not.",
        "Esperado 'do' após a condição 'while'": "Inclua 'do' após a condição do 'while'.",
        "Esperado 'end' para fechar o loop 'while'": "Certifique-se de fechar o loop 'while' com 'end'.",
        "Parâmetros inválidos na definição da função": "Verifique a lista de parâmetros na definição da função.",
        "Esperado '(' após o nome da função": "Inclua '(' após o nome da função.",
        "Número incorreto de argumentos na chamada da função": "Verifique o número de argumentos ao chamar a função.",
        "Entrada inválida: esperado um número inteiro.": "Certifique-se de inserir um número inteiro válido.",
        "Lista não fechada: esperado ']'": "Certifique-se de fechar a lista com ']'.",
    }
    for error, suggestion_text in suggestion.items():
        if error in error_message:
            return suggestion_text
    return "Corrija o erro no código."

def export_error(filename, error_message, code_lines):
    with open(filename, 'w') as file:
        file.write(f"Erro: {error_message}\n")
        file.write("Código com erro:\n")
        for i, line in enumerate(code_lines, start=1):
            file.write(f"{i}: {line}\n")

def save_file(filename, code_lines):
    with open(filename, 'w') as file:
        file.write("\n".join(code_lines))

def open_file(filename):
    with open(filename, 'r') as file:
        return file.readlines()

def limpar_console():
    os.system('clear')
    print("Digite seu código. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.\n")
    print("Para salvar o código, digite 'salvar <nome_do_arquivo>'. Para abrir um arquivo, digite 'abrir <nome_do_arquivo>'.\n")
    print("Para desfazer a última ação, digite 'desfazer'. Para refazer a última ação desfeita, digite 'refazer'.\n")
    print("Para limpar o console, digite 'clear'. Para excluir o código feito, digite excluir'.\n")

def execute_user_code():
    print("Digite seu código. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.\n")
    print("Para salvar o código, digite 'salvar <nome_do_arquivo>'. Para abrir um arquivo, digite 'abrir <nome_do_arquivo>'.\n")
    print("Para desfazer a última ação, digite 'desfazer'. Para refazer a última ação desfeita, digite 'refazer'.\n")
    print("Para limpar o console, digite cls. Para excluir o código feito, digite excluir'.\n")

    code_lines = []
    undo_stack = []
    redo_stack = []

    def undo():
        if code_lines:
            last_action = code_lines.pop()
            undo_stack.append(last_action)
            print("Ação desfeita.")
        else:
            print("Não há ações para desfazer.")

    def redo():
        if undo_stack:
            last_undo = undo_stack.pop()
            code_lines.append(last_undo)
            print("Ação refeita.")
        else:
            print("Não há ações para refazer.")

    while True:
        line = input(">>> ")
        if line.strip().lower() == 'sair':
            break
        elif line.strip().lower() == 'compilar':
            if not code_lines:
                print('Não há código para se executar')
            code = "\n".join(code_lines)
            try:
                tokens = lexer(code)
                parser = Parser(tokens)
                parser.parse()
            except (SyntaxError, NameError) as e:
                erro_msg = str(e)
                print(f"Erro: {erro_msg}")
                linha_erro = len(code_lines)
                if linha_erro > 0:
                    print(f"Erro na linha {linha_erro}: {code_lines[linha_erro-1]}")
                sugestao = suggest_correction(erro_msg, code_lines)
                print(f"Sugestão: {sugestao}")
                corrigir = input("Deseja corrigir a linha? (s/n): ").strip().lower()
                if corrigir == 's':
                    nova_linha = input("Digite a linha corrigida: ")
                    if 0 < linha_erro <= len(code_lines):
                        code_lines[linha_erro-1] = nova_linha
                exportar = input("Deseja exportar o erro para um arquivo? (s/n): ").strip().lower()
                if exportar == 's':
                    nome_arquivo = input("Digite o nome do arquivo para exportar o erro: ")
                    export_error(nome_arquivo, erro_msg, code_lines)
                    print(f"Erro exportado para o arquivo {nome_arquivo}.")
        elif line.strip().lower().startswith('salvar '):
            filename = line.strip().split(' ', 1)[1]
            save_file(filename, code_lines)
            print(f"Arquivo {filename} salvo com sucesso.")
        elif line.strip().lower().startswith('abrir '):
            filename = line.strip().split(' ', 1)[1]
            try:
                code_lines = open_file(filename)
                print(f"Arquivo {filename} aberto com sucesso.")
                for i, code_line in enumerate(code_lines):
                    print(f"{i+1}: {code_line.strip()}")
            except FileNotFoundError:
                print(f"Arquivo {filename} não encontrado.")
        elif line.strip().lower() == 'desfazer':
            undo()
        elif line.strip().lower() == 'refazer':
            redo()
        elif line.strip().lower() == 'clear':
            limpar_console()
        elif line.strip().lower() == 'excluir':
            if not code_lines:
                print('Não há código para limpar')
            else:
                code_lines.clear()
                print('Código excluido com sucesso')
        else:
            code_lines.append(line)
            undo_stack.clear()

execute_user_code()