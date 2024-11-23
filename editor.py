import re
import os

"""
Editor de Código Simples com Lexer e Parser
=========================================

Este é um editor de código simples que implementa um lexer e parser para uma linguagem de programação básica.
O programa suporta várias funcionalidades como variáveis, funções, loops, condicionais e operações com listas.

Estrutura Principal:
------------------
1. TOKENS: Definição dos tokens da linguagem
2. Lexer: Análise léxica do código
3. Parser: Análise sintática e execução do código
4. Funções Utilitárias: Manipulação de arquivos e tratamento de erros
5. Interface do Usuário: Sistema de entrada/saída interativo

Funcionalidades Suportadas:
-------------------------
- Declaração de variáveis (let)
- Funções (function)
- Loops (while, for)
- Condicionais (if/else)
- Operações matemáticas e lógicas
- Manipulação de listas
- Sistema de undo/redo
- Salvamento e carregamento de arquivos

Comandos do Editor:
-----------------
- 'compilar': Executa o código atual
- 'salvar <arquivo>': Salva o código em um arquivo
- 'abrir <arquivo>': Carrega código de um arquivo
- 'desfazer': Desfaz última ação
- 'refazer': Refaz última ação desfeita
- 'sair': Encerra o programa
"""

# Definição dos tokens da linguagem
TOKENS = {
    'FOR': r'\bfor\b',                           # Laço 'for'
    'IN': r'\bin\b',                             # Palavra-chave 'in'
    'LET': r'\blet\b',                           # Declaração de variável
    'PRINT': r'\bprint\b',                       # Comando de impressão
    'INPUT': r'\binput\b',                       # Comando de entrada
    'IF': r'\bif\b',                             # Condicional 'if'
    'ELSE': r'\belse\b',                         # Condicional 'else'
    'WHILE': r'\bwhile\b',                       # Laço 'while'
    'DO': r'\bdo\b',                             # Palavra-chave 'do'
    'FUNCTION': r'\bfunction\b',                 # Declaração de função
    'RETURN': r'\breturn\b',                     # Comando de retorno
    'END': r'\bend\b',                           # Fim de bloco
    'NUMBER': r'\b\d+\b',                        # Número inteiro
    'LOGICAL': r'\b(and|or|not)\b',              # Operadores lógicos
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', # Identificador
    'OPERATOR': r'[+\-*/]',                      # Operadores matemáticos
    'COMPARISON': r'[><=]+',                     # Operadores de comparação
    'COMMA': r',',                               # Vírgula
    'OPEN_PAREN': r'\(',                         # Parêntese de abertura
    'CLOSE_PAREN': r'\)',                        # Parêntese de fechamento
    'LIST_START': r'\[',                         # Início de lista
    'LIST_END': r'\]',                           # Fim de lista
}

def lexer(code):
    """
    Realiza a análise léxica do código fonte.
    
    Args:
        code (str): Código fonte a ser analisado
        
    Returns:
        list: Lista de tuplas (tipo_token, valor)
        
    Raises:
        SyntaxError: Quando encontra um token desconhecido
    """
    tokens = [] # Lista de tokens
    code = code.strip() # Remove espaços em branco
    while code: # Loop principal
        match = None # Inicializa a variável de correspondência
        for token_type, pattern in TOKENS.items(): # Itera sobre os tokens
            regex = re.compile(pattern) # Compila a expressão regular
            match = regex.match(code) # Tenta fazer correspondência com o início do código
            if match: # Se houver correspondência
                token = (token_type, match.group(0)) # Cria uma tupla com o tipo do token e o valor
                tokens.append(token) # Adiciona o token à lista
                print(f"Token encontrado: {token}")  # Debug print
                code = code[match.end():] # Atualiza o código removendo o token encontrado
                code = code.strip() # Remove espaços em branco
                break # Sai do loop interno
        if not match: # Se não houver correspondência
            raise SyntaxError(f"Token desconhecido: {code[:10]}") # Gera um erro de token desconhecido
    return tokens # Retorna a lista de tokens

class Parser:
    """
    Realiza a análise sintática e execução do código.
    
    Attributes:
        tokens (list): Lista de tokens para análise
        position (int): Posição atual na lista de tokens
        variables (dict): Dicionário de variáveis
        functions (dict): Dicionário de funções
        return_value: Valor de retorno de funções
        in_function (bool): Indica se está dentro de uma função
    """
    def __init__(self, tokens):
        """
        Inicializa o parser com uma lista de tokens.
        
        Args:
            tokens (list): Lista de tokens para análise
        """
        self.tokens = tokens # Lista de tokens
        self.position = 0 # Posição atual
        self.variables = {} # Dicionário de variáveis
        self.functions = {} # Dicionário de funções
        self.return_value = None # Valor de retorno
        self.in_function = False # Indica se está dentro de uma função

    def parse_end(self): # Fim de bloco
        self.position += 1 # Avança para o próximo token

    def parse(self): # Função principal
        """
        Analisa e executa o código token por token.
        
        Raises:
            SyntaxError: Para comandos inválidos
        """  
        while self.position < len(self.tokens): # Loop principal
            token_type, value = self.tokens[self.position] # Pega o tipo e o valor do token
            if token_type == 'LET': # Declaração de variável
                self.parse_let() # Chama a função de declaração de variável
            elif token_type == 'PRINT': # Comando de impressão
                self.parse_print() # Chama a função de impressão
            elif token_type == 'INPUT': # Comando de entrada
                self.parse_input() # Chama a função de entrada
            elif token_type == 'IF': # Condicional 'if'
                self.parse_if() # Chama a função de condicional
            elif token_type == 'WHILE': # Laço 'while'
                self.parse_while() # Chama a função de laço 'while'
            elif token_type == 'FUNCTION': # Declaração de função
                self.parse_function() # Chama a função de declaração de função
            elif token_type == 'FOR': # Laço 'for'
                self.parse_for() # Chama a função de laço 'for'
            elif token_type == 'RETURN': # Comando de retorno
                if self.in_function: # Verifica se está dentro de uma função
                    self.parse_return() # Chama a função de retorno
                else:
                    raise SyntaxError("Comando 'return' fora de uma função") # Gera um erro se não estiver em uma função
            elif token_type == 'IDENTIFIER': # Identificador (variável ou função)
                next_token = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else (None, None) # Pega o próximo token
                if next_token[0] == 'OPEN_PAREN': # Verifica se o próximo token é '('
                    self.parse_function_call(value) # Chama a função de chamada de função
                elif next_token[1] == '=': # Verifica se o próximo token é '='
                    self.parse_assignment() # Chama a função de atribuição
                else: # Se não for uma chamada de função ou atribuição
                    raise SyntaxError(f"Comando inválido: {value}") # Gera um erro
            elif token_type == 'END': # Fim de bloco
                if self.in_function: # Verifica se está dentro de uma função
                    self.position += 1 # Avança para o próximo token
                    break # Interrompe a execução
                else: # Se não estiver em uma função
                    self.parse_end() # Chama a função de fim de bloco
            else: # Se não for nenhum dos comandos acima
                raise SyntaxError(f"Comando inválido: {value}") # Gera um erro
            
        
    def parse_let(self): # Declaração de variável
        self.position += 1 # Pula o token 'LET'
        var_name = self.tokens[self.position][1] # Pega o nome da variável
        self.position += 1 # Pula o identificador
        if self.position >= len(self.tokens) or self.tokens[self.position][1] != '=': # Verifica se o próximo token é '='
            raise SyntaxError("Erro de sintaxe em declaração de variável") # Se não for, gera um erro
        self.position += 1 # Pula o '='
        value = self.evaluate_expression() # Avalia a expressão à direita do '='
        self.variables[var_name] = value # Atribui o valor à variável

    def parse_print(self): # Comando de impressão
        self.position += 1 # Pula o token 'PRINT'
        value = self.evaluate_expression() # Avalia a expressão a ser impressa
        print("Saída:", value) # Exibe a saída

    def parse_input(self): # Comando de entrada
        self.position += 1 # Pula o token 'INPUT'
        var_name = self.tokens[self.position][1] # Pega o nome da variável
        self.position += 1 # Pula o identificador
        user_input = input("Entrada: ") # Lê a entrada do usuário
        try: # Tenta converter a entrada para inteiro
            self.variables[var_name] = int(user_input) # Converte a entrada para inteiro e atribui à variável
        except ValueError: # Se a conversão falhar
            raise SyntaxError("Entrada inválida: esperado um número inteiro.") # Gera um erro se a entrada não for um número

    def parse_if(self): # Condicional 'if'
        self.position += 1  # Pula o token 'IF'
        
        # Coleta os tokens da condição até encontrar um token que indica o início do bloco
        condition_tokens = [] # Lista de tokens da condição
        while self.position < len(self.tokens) and self.tokens[self.position][0] not in ('LET', 'PRINT', 'INPUT', 'IF', 'ELSE', 'WHILE', 'DO', 'FUNCTION', 'RETURN', 'END'): # Verifica se o token atual é um comando
            condition_tokens.append(self.tokens[self.position]) # Adiciona o token à lista de condição
            self.position += 1 # Avança para o próximo token
        
        # Avalia a condição usando um sub-parser
        condition_parser = Parser(condition_tokens) # Cria um novo parser para a condição
        condition_parser.variables = self.variables.copy() # Copia as variáveis do escopo atual
        condition_parser.functions = self.functions # Copia as funções
        condition_result = condition_parser.evaluate_condition() # Avalia a condição
        
        if condition_result: # Se a condição for verdadeira
            # Executa o bloco 'if'
            if self.position < len(self.tokens) and self.tokens[self.position][0] == 'END': # Verifica se o bloco 'if' está vazio
                self.position += 1  # Pula o token 'END'
                return # Interrompe a execução
            self.parse() # Chama a função de análise sintática
        else: # Se a condição for falsa
            # Pula o bloco 'if' até encontrar 'ELSE' ou 'END'
            while self.position < len(self.tokens) and self.tokens[self.position][0] not in ('ELSE', 'END'): # Verifica se o token atual é 'ELSE' ou 'END' 
                self.position += 1 # Avança para o próximo token
            if self.position < len(self.tokens) and self.tokens[self.position][0] == 'ELSE': # Verifica se o token atual é 'ELSE'
                self.position += 1 # Pula o token 'ELSE'
                self.parse() # Chama a função de análise sintática
        
        # Pula o token 'END'
        if self.position < len(self.tokens) and self.tokens[self.position][0] == 'END': # Verifica se o token atual é 'END'
            self.position += 1 # Pula o token 'END'

    def parse_while(self): # Laço 'while'
        self.position += 1 # Pula o token 'WHILE'
        condition_tokens = [] # Lista de tokens da condição
        
        # Coleta os tokens da condição até encontrar 'DO' ou um comando
        while self.position < len(self.tokens): # Loop para coletar os tokens da condição
            current_token = self.tokens[self.position][0] # Pega o tipo do token
            if current_token == 'DO': # Verifica se o token atual é 'DO'
                self.position += 1  # Pula o 'DO' se existir
                break # Interrompe o loop
            elif current_token in ('LET', 'PRINT', 'INPUT', 'IF', 'ELSE', 'WHILE', 'FUNCTION', 'RETURN'): # Verifica se o token atual é um comando
                break # Interrompe o loop
            condition_tokens.append(self.tokens[self.position]) # Adiciona o token à lista de condição
            self.position += 1 # Avança para o próximo token
        
        # Coleta os tokens do corpo do loop até encontrar 'END'
        loop_body_tokens = [] # Lista de tokens do corpo do loop
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END': # Verifica se o token atual é 'END'
            loop_body_tokens.append(self.tokens[self.position]) # Adiciona o token ao corpo do loop
            self.position += 1 # Avança para o próximo token
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END': # Verifica se o token atual é 'END'
            raise SyntaxError("Esperado 'end' para fechar o loop 'while'") # Gera um erro se não for
        
        self.position += 1  # Pula o token 'END'
        
        while True: # Loop do laço 'while'
            # Avalia a condição usando um sub-parser
            condition_parser = Parser(condition_tokens) # Cria um novo parser para a condição
            condition_parser.variables = self.variables.copy() # Copia as variáveis do escopo atual
            condition_parser.functions = self.functions # Copia as funções
            condition_result = condition_parser.evaluate_condition() # Avalia a condição
            
            if not condition_result: # Se a condição for falsa
                break # Interrompe o loop
            
            # Executa o corpo do loop usando um sub-parser
            loop_parser = Parser(loop_body_tokens) # Cria um novo parser para o corpo do loop
            loop_parser.variables = self.variables.copy() # Copia as variáveis do escopo atual
            loop_parser.functions = self.functions # Copia as funções
            loop_parser.parse() # Chama a função de análise sintática
            self.variables.update(loop_parser.variables) # Atualiza as variáveis do escopo externo

    def parse_function(self): # Declaração de função
        self.position += 1 # Pula o token 'FUNCTION'
        func_name = self.tokens[self.position][1] # Pega o nome da função
        self.position += 1 # Pula o identificador
        parameters = [] # Lista de parâmetros
    
        if self.tokens[self.position][0] == 'OPEN_PAREN': # Verifica se o próximo token é '('
            self.position += 1 # Pula '('
            while self.tokens[self.position][0] != 'CLOSE_PAREN': # Verifica se o token atual é ')'
                if self.tokens[self.position][0] == 'IDENTIFIER': # Verifica se o token atual é um identificador
                    parameters.append(self.tokens[self.position][1]) # Adiciona o identificador à lista de parâmetros
                    self.position += 1 # Avança para o próximo token
                    if self.tokens[self.position][0] == 'COMMA': # Verifica se o próximo token é ','
                        self.position += 1 # Pula ','
                else: # Se não for um identificador 
                    raise SyntaxError("Parâmetros inválidos na definição da função") # Gera um erro se não for um identificador 
            self.position += 1  # Pula ')' 
        else: # Se não houver parâmetros
            raise SyntaxError("Esperado '(' após o nome da função") # Gera um erro se não houver parênteses de abertura
    
        func_body_tokens = [] # Lista de tokens do corpo da função
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END': # Verifica se o token atual é 'END' 
            func_body_tokens.append(self.tokens[self.position]) # Adiciona o token ao corpo da função 
            self.position += 1 # Avança para o próximo token
    
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END': # Verifica se o token atual é 'END' 
            raise SyntaxError("Esperado 'end' para fechar a função") # Gera um erro se não for 'END'
    
        self.position += 1  # Pula o token 'END'
    
        self.functions[func_name] = { # Adiciona a função ao dicionário de funções
            'parameters': parameters, # Parâmetros da função
            'body': func_body_tokens # Corpo da função
        }

    def parse_return(self): # Comando de retorno
        self.position += 1 # Pula o token 'RETURN'
        self.return_value = self.evaluate_expression() # Avalia a expressão de retorno
        self.position = len(self.tokens)  # Interrompe a execução atual

    def parse_function_call(self, func_name): # Chamada de função
        self.position += 1  # Pula o nome da função
        args = [] # Lista de argumentos
    
        if self.tokens[self.position][0] == 'OPEN_PAREN': # Verifica se o próximo token é '('
            self.position += 1  # Pula '(' 
            while self.tokens[self.position][0] != 'CLOSE_PAREN': # Verifica se o token atual é ')'
                arg = self.evaluate_expression() # Avalia a expressão do argumento
                args.append(arg) # Adiciona o argumento à lista de argumentos
                if self.tokens[self.position][0] == 'COMMA': # Verifica se o próximo token é ','
                    self.position += 1  # Pula ',' 
            self.position += 1  # Pula ')'
        else: # Se não houver argumentos
            raise SyntaxError("Esperado '(' após o nome da função") # Gera um erro se não houver parênteses de abertura
    
        if func_name not in self.functions: # Verifica se a função foi definida
            raise NameError(f"Função não definida: {func_name}") # Gera um erro se a função não foi definida
    
        function = self.functions[func_name] # Pega a função do dicionário de funções
        if len(args) != len(function['parameters']): # Verifica se o número de argumentos é igual ao número de parâmetros
            raise SyntaxError("Número incorreto de argumentos na chamada da função") # Gera um erro se o número de argumentos for diferente do número de parâmetros
    
        func_parser = Parser(function['body']) # Cria um novo parser para a função
        func_parser.variables = self.variables.copy() # Copia as variáveis do escopo atual
        func_parser.functions = self.functions # Copia as funções
        func_parser.in_function = True # Indica que está dentro de uma função
    
        for param, arg in zip(function['parameters'], args): # Associa os parâmetros com os argumentos
            func_parser.variables[param] = arg # Atribui o argumento ao parâmetro
     
        func_parser.parse() # Chama a função de análise sintática 
    
        return_value = func_parser.return_value # Pega o valor de retorno da função

        return return_value # Retorna o valor de retorno

    def parse_assignment(self): # Atribuição de variável
        var_name = self.tokens[self.position][1] # Pega o nome da variável
        self.position += 1  # Pula o identificador
        self.position += 1  # Pula o '='
        value = self.evaluate_expression() # Avalia a expressão à direita do '='
        self.variables[var_name] = value # Atribui o valor à variável

    def evaluate_expression(self): # Avalia a expressão
        result = self.get_term() # Pega o primeiro termo
        while self.position < len(self.tokens) and \
              self.tokens[self.position][0] in ('OPERATOR', 'LOGICAL', 'COMPARISON'): # Verifica se o token atual é um operador
            operator = self.tokens[self.position][1] # Pega o operador
            self.position += 1 # Avança para o próximo token
            right = self.get_term() # Pega o próximo termo
            result = self.apply_operator(result, operator, right) # Aplica o operador
        return result # Retorna o resultado

    def get_term(self): # Pega o termo
        token_type, value = self.tokens[self.position] # Pega o tipo e o valor do token
        if token_type == 'LIST_START': # Verifica se o token é '['
            return self.parse_list() # Chama a função de lista
        elif token_type == 'NUMBER': # Verifica se o token é um número
            self.position += 1 # Avança para o próximo token
            return int(value) # Retorna o valor do número
        elif token_type == 'IDENTIFIER': # Verifica se o token é um identificador
            next_token = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else (None, None) # Pega o próximo token
            if next_token[0] == 'OPEN_PAREN': # Verifica se o próximo token é '('
                result = self.parse_function_call(value) # Chama a função de chamada de função
                return result # Retorna o resultado
            else: # Se não for uma chamada de função
                self.position += 1 # Avança para o próximo token
                if value in self.variables: # Verifica se a variável foi definida
                    return self.variables[value] # Retorna o valor da variável
                else: # Se a variável não foi definida
                    raise NameError(f"Variável não definida: {value}") # Gera um erro
        elif token_type == 'OPEN_PAREN': # Verifica se o token é '('
            self.position += 1 # Pula '('
            value = self.evaluate_expression() # Avalia a expressão
            if self.tokens[self.position][0] != 'CLOSE_PAREN': # Verifica se o próximo token é ')'
                raise SyntaxError("Esperado ')' na expressão") # Gera um erro se não for
            self.position += 1  # Pula ')'
            return value # Retorna o valor da expressão
        else: # Se não for nenhum dos tipos acima
            raise SyntaxError(f"Expressão inválida: {value}") # Gera um erro
 
    def parse_list(self): # Lista
        self.position += 1  # Skip '['
        elements = [] # Lista de elementos
        
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'LIST_END': # Verifica se o token atual é ']'
            value = self.evaluate_expression() # Avalia a expressão
            elements.append(value) # Adiciona o valor à lista
            
            if self.position < len(self.tokens) and self.tokens[self.position][0] == 'COMMA': # Verifica se o token atual é ','
                self.position += 1 # Pula ','
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'LIST_END': # Verifica se o token atual é ']'
            raise SyntaxError("Lista não fechada: esperado ']'") # Gera um erro se não for ']'
            
        self.position += 1  # Skip ']'
        return elements # Retorna a lista de elementos

    def evaluate_condition(self): # Avalia a condição
        return self.evaluate_expression() # Avalia a expressão

    def apply_operator(self, left, operator, right): # Aplica o operador à expressão 
        if operator == '+': # Adição 
            if isinstance(left, list) or isinstance(right, list): # Verifica se left ou right é uma lista
                if isinstance(left, list) and isinstance(right, list): # Verifica se ambos são listas
                    return left + right # Concatena as listas
                elif isinstance(left, list): # Verifica se left é uma lista
                    return left + [right] # Adiciona right à lista left
                else: # Se right for uma lista
                    return [left] + right # Adiciona left à lista right
            return left + right # Soma os valores
        elif operator == '-': # Subtração
            return left - right # Subtrai os valores 
        elif operator == '*': # Multiplicação
            return left * right # Multiplica os valores
        elif operator == '/': # Divisão
            return left / right # Divide os valores
        elif operator == '>': # Maior que
            return left > right # Verifica se left é maior que right
        elif operator == '<': # Menor que
            return left < right # Verifica se left é menor que right
        elif operator == '==': # Igualdade
            return left == right # Verifica se left é igual a right
        elif operator == 'and': # Operador lógico 'and'
            return left and right # Verifica se left e right são verdadeiros
        elif operator == 'or': # Operador lógico 'or'
            return left or right # Verifica se left ou right são verdadeiros
        elif operator == 'not': # Operador lógico 'not'
            return not right # Verifica se right é falso
        else: # Se o operador for desconhecido
            raise SyntaxError(f"Operador desconhecido: {operator}") # Gera um erro se o operador for desconhecido

    def parse_for(self): # Laço 'for'
        self.position += 1  # Pula 'for'
        
        # Pega o nome da variável de iteração
        if self.tokens[self.position][0] != 'IDENTIFIER': # Verifica se o token atual é um identificador
            raise SyntaxError("Esperado um identificador após 'for'") # Gera um erro se não for
        iterator_var = self.tokens[self.position][1] # Pega o nome da variável
        self.position += 1 # Pula o identificador
        
        # Verifica a palavra 'in'
        if self.tokens[self.position][0] != 'IN': # Verifica se o token atual é 'in'
            raise SyntaxError("Esperado 'in' após o identificador no laço for") # Gera um erro se não for
        self.position += 1 # Pula 'in'
        
        # Avalia a expressão que gera a sequência (lista) 
        sequence = self.evaluate_expression() # Avalia a expressão
        if not isinstance(sequence, list): # Verifica se a sequência é uma lista
            raise TypeError("For precisa de uma lista para iterar") # Gera um erro se não for
        
        # Coleta os tokens do corpo do loop até encontrar 'END'
        loop_body_tokens = [] # Lista de tokens do corpo do loop
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END': # Verifica se o token atual é 'END'
            loop_body_tokens.append(self.tokens[self.position]) # Adiciona o token ao corpo do loop
            self.position += 1 # Avança para o próximo token
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END': # Verifica se o token atual é 'END'
            raise SyntaxError("Esperado 'end' para fechar o laço 'for'") # Gera um erro se não for
        
        self.position += 1  # Pula o token 'END'
        
        # Executa o corpo do loop para cada elemento da sequência
        for item in sequence: # Itera sobre a sequência
            # Cria um novo parser para cada iteração
            loop_parser = Parser(loop_body_tokens) # Cria um novo parser para o corpo do loop
            loop_parser.variables = self.variables.copy() # Copia as variáveis do escopo atual
            loop_parser.functions = self.functions # Copia as funções
            
            # Define a variável de iteração
            loop_parser.variables[iterator_var] = item # Atribui o item à variável de iteração
            
            # Executa o corpo do loop
            loop_parser.parse() # Chama a função de análise sintática 
            
            # Atualiza as variáveis do escopo externo
            self.variables.update(loop_parser.variables) # Atualiza as variáveis do escopo externo

def suggest_correction(error_message, code_lines):
    """
    Sugere correções para erros comuns no código.
    
    Args:
        error_message (str): Mensagem de erro
        code_lines (list): Linhas do código
        
    Returns:
        str: Sugestão de correção
    """
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
    for error, suggestion_text in suggestion.items(): # Itera sobre as sugestões
        if error in error_message: # Verifica se o erro está na mensagem
            return suggestion_text # Retorna a sugestão
    return "Corrija o erro no código." # Retorna uma mensagem padrão

def export_error(filename, error_message, code_lines): # Exporta informações de erro para um arquivo
    """
    Exporta informações de erro para um arquivo.
    
    Args:
        filename (str): Nome do arquivo de saída
        error_message (str): Mensagem de erro
        code_lines (list): Linhas do código
    """
    with open(filename, 'w') as file: # Abre o arquivo para escrita
        file.write(f"Erro: {error_message}\n") # Escreve a mensagem de erro
        file.write("Código com erro:\n") # Escreve o cabeçalho
        for i, line in enumerate(code_lines, start=1): # Itera sobre as linhas do código
            file.write(f"{i}: {line}\n") # Escreve a linha no arquivo

def save_file(filename, code_lines): # Salva o código em um arquivo
    """
    Salva o código em um arquivo.
    
    Args:
        filename (str): Nome do arquivo
        code_lines (list): Linhas do código
    """
    with open(filename, 'w') as file: # Abre o arquivo para escrita
        file.write("\n".join(code_lines)) # Escreve o código no arquivo

def open_file(filename): # Abre e lê um arquivo
    """
    Abre e lê um arquivo de código.
    
    Args:
        filename (str): Nome do arquivo
        
    Returns:
        list: Linhas do código lido
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
    """
    with open(filename, 'r') as file: # Abre o arquivo para leitura
        return file.readlines() # Lê as linhas do arquivo

def clear_console(): # Limpa o console
    os.system('cls') # Executa o comando 'cls' no terminal
    print("Digite seu código. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.\n") # Exibe mensagem de início
    print("Para salvar o código, digite 'salvar <nome_do_arquivo>'. Para abrir um arquivo, digite 'abrir <nome_do_arquivo>'.\n") # Exibe mensagem de salvar/abrir arquivo
    print("Para desfazer a última ação, digite 'desfazer'. Para refazer a última ação desfeita, digite 'refazer'.\n") # Exibe mensagem de desfazer/refazer
    print("Para limpar o console, digite 'cls'. Para excluir o código feito, digite 'excluir'.\n") # Exibe mensagem de limpar/excluir código

def execute_user_code(): # Função principal
    """ 
    Função principal que executa o loop interativo do editor.
    
    Implementa:
        - Interface de linha de comando
        - Sistema de undo/redo
        - Compilação do código
        - Manipulação de arquivos
    """
    print("Digite seu código. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.\n") # Exibe mensagem de início
    print("Para salvar o código, digite 'salvar <nome_do_arquivo>'. Para abrir um arquivo, digite 'abrir <nome_do_arquivo>'.\n") # Exibe mensagem de salvar/abrir arquivo
    print("Para desfazer a última ação, digite 'desfazer'. Para refazer a última ação desfeita, digite 'refazer'.\n") # Exibe mensagem de desfazer/refazer

    code_lines = [] # Lista de linhas de código
    undo_stack = [] # Pilha de desfazer
    redo_stack = [] # Pilha de refazer


    def undo(): # Desfaz a última ação
        if code_lines: # Verifica se há ações para desfazer
            last_action = code_lines.pop() # Remove a última ação
            undo_stack.append(last_action) # Adiciona a ação à pilha de desfazer
            print("Ação desfeita.") # Exibe mensagem de ação desfeita
        else:
            print("Não há ações para desfazer.") # Exibe mensagem se não houver ações para desfazer

    def redo(): # Refaz a última ação desfeita
        if undo_stack: # Verifica se há ações para refazer
            last_undo = undo_stack.pop() # Remove a última ação desfeita
            code_lines.append(last_undo) # Adiciona a ação de volta ao código
            print("Ação refeita.") # Exibe mensagem de ação refeita
        else:
            print("Não há ações para refazer.") # Exibe mensagem se não houver ações para refazer

    while True: # Loop principal
        line = input(">>> ") # Lê a entrada do usuário
        if line.strip().lower() == 'sair': # Verifica se o usuário digitou 'sair'
            break
        elif line.strip().lower() == 'compilar': # Verifica se o usuário digitou 'compilar'
            code = "\n".join(code_lines) # Junta as linhas de código em uma única string
            try: # Tenta compilar o código
                tokens = lexer(code) # Realiza a análise léxica
                parser = Parser(tokens) # Cria um parser
                parser.parse() # Realiza a análise sintática e executa o código
            except (SyntaxError, NameError) as e: # Trata erros de sintaxe e nomes
                erro_msg = str(e) # Pega a mensagem de erro
                print(f"Erro: {erro_msg}") # Exibe a mensagem de erro
                linha_erro = len(code_lines) # Pega a linha do erro
                if linha_erro > 0: # Verifica se há código
                    print(f"Erro na linha {linha_erro}: {code_lines[linha_erro-1]}") # Exibe a linha do erro
                sugestao = suggest_correction(erro_msg, code_lines) # Sugere uma correção para o erro
                print(f"Sugestão: {sugestao}") # Exibe a sugestão
                corrigir = input("Deseja corrigir a linha? (s/n): ").strip().lower() # Pergunta se deseja corrigir a linha
                if corrigir == 's': # Verifica se deseja corrigir a linha
                    nova_linha = input("Digite a linha corrigida: ") # Lê a nova linha
                    if 0 < linha_erro <= len(code_lines): # Verifica se a linha do erro é válida
                        code_lines[linha_erro-1] = nova_linha # Substitui a linha do erro pela nova linha
                exportar = input("Deseja exportar o erro para um arquivo? (s/n): ").strip().lower() # Pergunta se deseja exportar o erro
                if exportar == 's': # Verifica se deseja exportar o erro
                    nome_arquivo = input("Digite o nome do arquivo para exportar o erro: ") # Pede o nome do arquivo
                    export_error(nome_arquivo, erro_msg, code_lines) # Exporta o erro para o arquivo
                    print(f"Erro exportado para o arquivo {nome_arquivo}.") # Exibe mensagem de erro exportado
        elif line.strip().lower().startswith('salvar '): # Verifica se o usuário digitou 'salvar'
            filename = line.strip().split(' ', 1)[1] # Pega o nome do arquivo
            save_file(filename, code_lines) # Salva o código no arquivo
            print(f"Arquivo {filename} salvo com sucesso.") # Exibe mensagem de arquivo salvo
        elif line.strip().lower().startswith('abrir '): # Verifica se o usuário digitou 'abrir'
            filename = line.strip().split(' ', 1)[1] # Pega o nome do arquivo
            try: # Tenta abrir o arquivo 
                code_lines = open_file(filename) # Abre o arquivo
                print(f"Arquivo {filename} aberto com sucesso.") # Exibe mensagem de arquivo aberto
                for i, code_line in enumerate(code_lines): # Exibe o código do arquivo
                    print(f"{i+1}: {code_line.strip()}") # Exibe a linha do código
            except FileNotFoundError: # Trata erro de arquivo não encontrado
                print(f"Arquivo {filename} não encontrado.") # Exibe mensagem de arquivo não encontrado
        elif line.strip().lower() == 'desfazer': # Verifica se o usuário digitou 'desfazer'
            undo() # Desfaz a última ação
        elif line.strip().lower() == 'refazer': # Verifica se o usuário digitou 'refazer'
            redo() # Refaz a última ação desfeita
        elif line.strip().lower() == 'cls': # Verifica se o usuário digitou 'cls'
            clear_console() # Limpa o console
        elif line.strip().lower() == 'excluir': # Verifica se o usuário digitou 'excluir'
            if not code_lines: # Verifica se há código
                print("Não há código para limpar.") # Exibe mensagem se não houver código
            else: # Se houver código
                code_lines.clear() # Limpa o código
                print("Código excluido com sucesso.") # Exibe mensagem de código excluído
        else: # Se não for um comando
            code_lines.append(line) # Adiciona a linha ao código
            undo_stack.clear() # Limpa a pilha de desfazer

execute_user_code() # Executa o loop interativo do editor
