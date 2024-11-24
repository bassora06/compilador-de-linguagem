import re
import os

"""
Editor de Codigo Simples com Lexer e Parser
=========================================

Este e um editor de codigo simples que implementa um lexer e parser para uma linguagem de programacao basica.
O programa suporta varias funcionalidades como variaveis, funcoes, loops, condicionais e operacoes com listas.

Estrutura Principal:
------------------
1. TOKENS: Definicao dos tokens da linguagem
2. Lexer: Analise lexica do codigo
3. Parser: Analise sintatica e execucao do codigo
4. Funcoes Utilitarias: Manipulacao de arquivos e tratamento de erros
5. Interface do Usuario: Sistema de entrada/saida interativo

Funcionalidades Suportadas:
-------------------------
- Declaracao de variaveis (let)
- Funcoes (function)
- Loops (while, for)
- Condicionais (if/else)
- Operacoes matematicas e logicas
- Manipulacao de listas
- Sistema de undo/redo
- Salvamento e carregamento de arquivos

Comandos do Editor:
-----------------
- 'compilar': Executa o codigo atual
- 'salvar <arquivo>': Salva o codigo em um arquivo
- 'abrir <arquivo>': Carrega codigo de um arquivo
- 'desfazer': Desfaz ultima acao
- 'refazer': Refaz ultima acao desfeita
- 'sair': Encerra o programa
"""

# Definicao dos tokens da linguagem
TOKENS = {
    'FOR': r'\bfor\b',                           # Laco 'for'
    'IN': r'\bin\b',                             # Palavra-chave 'in'
    'LET': r'\blet\b',                           # Declaracao de variavel
    'PRINT': r'\bprint\b',                       # Comando de impressao
    'INPUT': r'\binput\b',                       # Comando de entrada
    'IF': r'\bif\b',                             # Condicional 'if'
    'ELSE': r'\belse\b',                         # Condicional 'else'
    'WHILE': r'\bwhile\b',                       # Laco 'while'
    'DO': r'\bdo\b',                             # Palavra-chave 'do'
    'FUNCTION': r'\bfunction\b',                 # Declaracao de funcao
    'RETURN': r'\breturn\b',                     # Comando de retorno
    'END': r'\bend\b',                           # Fim de bloco
    'NUMBER': r'\b\d+\b',                        # Numero inteiro
    'LOGICAL': r'\b(and|or|not)\b',              # Operadores logicos
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', # Identificador
    'OPERATOR': r'[+\-*/]',                      # Operadores matematicos
    'COMPARISON': r'<=|>=|==|!=|>|<',            # Operadores de comparacao
    'ASSIGN': r'=',                             # Novo token para atribuicao
    'COMMA': r',',                               # Virgula
    'OPEN_PAREN': r'\(',                         # Parentese de abertura
    'CLOSE_PAREN': r'\)',                         # Parentese de fechamento
    'LIST_START': r'\[',                         # Inicio de lista
    'LIST_END': r'\]',                           # Fim de lista
    'STRING': r'\"[^\"]*\"|\'[^\']*\'',          # Strings com aspas simples ou duplas
}

def lexer(code):
    """
    Realiza a analise lexica do codigo fonte.
    
    Args:
        code (str): Codigo fonte a ser analisado
        
    Returns:
        list: Lista de tuplas (tipo_token, valor)
        
    Raises:
        SyntaxError: Quando encontra um token desconhecido
    """
    tokens = [] # Lista de tokens
    code = code.strip() # Remove espacos em branco
    while code: # Loop principal
        match = None # Inicializa a variavel de correspondencia
        for token_type, pattern in TOKENS.items(): # Itera sobre os tokens
            regex = re.compile(pattern) # Compila a expressao regular
            match = regex.match(code) # Tenta fazer correspondencia com o inicio do codigo
            if match: # Se houver correspondencia
                token = (token_type, match.group(0)) # Cria uma tupla com o tipo do token e o valor
                tokens.append(token) # Adiciona o token a lista
                print(f"Token encontrado: {token}")  # Debug print
                code = code[match.end():] # Atualiza o codigo removendo o token encontrado
                code = code.strip() # Remove espacos em branco
                break # Sai do loop interno
        if not match: # Se nao houver correspondencia
            raise SyntaxError(f"Token desconhecido: {code[:10]}") # Gera um erro de token desconhecido
    return tokens # Retorna a lista de tokens

class Parser:
    """
    Realiza a analise sintatica e execucao do codigo.
    
    Attributes:
        tokens (list): Lista de tokens para analise
        position (int): Posicao atual na lista de tokens
        variables (dict): Dicionario de variaveis
        functions (dict): Dicionario de funcoes
        return_value: Valor de retorno de funcoes
        in_function (bool): Indica se esta dentro de uma funcao
    """
    def __init__(self, tokens):
        """
        Inicializa o parser com uma lista de tokens.
        
        Args:
            tokens (list): Lista de tokens para analise
        """
        self.tokens = tokens # Lista de tokens
        self.position = 0 # Posicao atual
        self.variables = {} # Dicionario de variaveis
        self.functions = {} # Dicionario de funcoes
        self.return_value = None # Valor de retorno
        self.in_function = False # Indica se esta dentro de uma funcao

    def parse_end(self): # Fim de bloco
        self.position += 1 # Avanca para o proximo token

    def parse(self): # Funcao principal
        """
        Analisa e executa o codigo token por token.
        
        Raises:
            SyntaxError: Para comandos invalidos
        """  
        while self.position < len(self.tokens): # Loop principal
            token_type, value = self.tokens[self.position] # Pega o tipo e o valor do token
            if token_type == 'LET': # Declaracao de variavel
                self.parse_let() # Chama a funcao de declaracao de variavel
            elif token_type == 'PRINT': # Comando de impressao
                self.parse_print() # Chama a funcao de impressao
            elif token_type == 'INPUT': # Comando de entrada
                self.parse_input() # Chama a funcao de entrada
            elif token_type == 'IF': # Condicional 'if'
                self.parse_if() # Chama a funcao de condicional
            elif token_type == 'WHILE': # Laco 'while'
                self.parse_while() # Chama a funcao de laco 'while'
            elif token_type == 'FUNCTION': # Declaracao de funcao
                self.parse_function() # Chama a funcao de declaracao de funcao
            elif token_type == 'FOR': # Laco 'for'
                self.parse_for() # Chama a funcao de laco 'for'
            elif token_type == 'RETURN': # Comando de retorno
                if self.in_function: # Verifica se esta dentro de uma funcao
                    self.parse_return() # Chama a funcao de retorno
                else:
                    raise SyntaxError("Comando 'return' fora de uma funcao") # Gera um erro se nao estiver em uma funcao
            elif token_type == 'IDENTIFIER': # Identificador (variavel ou funcao)
                next_token = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else (None, None) # Pega o proximo token
                if next_token[0] == 'OPEN_PAREN': # Verifica se o proximo token e '('
                    self.parse_function_call(value) # Chama a funcao de chamada de funcao
                elif next_token[1] == '=': # Verifica se o proximo token e '='
                    self.parse_assignment() # Chama a funcao de atribuicao
                else: # Se nao for uma chamada de funcao ou atribuicao
                    raise SyntaxError(f"Comando invalido: {value}") # Gera um erro
            elif token_type == 'END': # Fim de bloco
                if self.in_function: # Verifica se esta dentro de uma funcao
                    self.position += 1 # Avanca para o proximo token
                    break # Interrompe a execucao
                else: # Se nao estiver em uma funcao
                    self.parse_end() # Chama a funcao de fim de bloco
            else: # Se nao for nenhum dos comandos acima
                raise SyntaxError(f"Comando invalido: {value}") # Gera um erro
            
        
    def parse_let(self): # Declaracao de variavel
        self.position += 1 # Pula o token 'LET'
        var_name = self.tokens[self.position][1] # Pega o nome da variavel
        self.position += 1 # Pula o identificador
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'ASSIGN':  # Alterado de 'COMPARISON' para 'ASSIGN'
            raise SyntaxError("Erro de sintaxe em declaracao de variavel")
        
        self.position += 1 # Pula o '='
        value = self.evaluate_expression() # Avalia a expressao a direita do '='
        self.variables[var_name] = value # Atribui o valor a variavel

    def parse_print(self): # Comando de impressao
        self.position += 1 # Pula o token 'PRINT'
        value = self.evaluate_expression() # Avalia a expressao a ser impressa
        print("Saida:", value) # Exibe a saida

    def parse_input(self): # Comando de entrada
        self.position += 1 # Pula o token 'INPUT'
        var_name = self.tokens[self.position][1] # Pega o nome da variavel
        self.position += 1 # Pula o identificador
        user_input = input("Entrada: ") # Le a entrada do usuario
        try: # Tenta converter a entrada para inteiro
            self.variables[var_name] = int(user_input) # Converte a entrada para inteiro e atribui a variavel
        except ValueError: # Se a conversao falhar
            raise SyntaxError("Entrada invalida: esperado um numero inteiro.") # Gera um erro se a entrada nao for um numero

    def parse_if(self):
        self.position += 1  # Pula o token 'IF'
        
        # Coleta os tokens da condicao
        condition_tokens = []
        while self.position < len(self.tokens) and self.tokens[self.position][0] not in ('PRINT', 'IF', 'ELSE', 'END'):
            condition_tokens.append(self.tokens[self.position])
            self.position += 1
        
        # Avalia a condicao
        condition_parser = Parser(condition_tokens)
        condition_parser.variables = self.variables.copy()
        condition_parser.functions = self.functions
        condition_result = condition_parser.evaluate_condition()
        
        # Coleta os tokens do bloco if ate encontrar 'ELSE' ou 'END'
        if_block_tokens = []
        while self.position < len(self.tokens) and self.tokens[self.position][0] not in ('ELSE', 'END'):
            if_block_tokens.append(self.tokens[self.position])
            self.position += 1
        
        # Coleta os tokens do bloco else se existir
        else_block_tokens = []
        if self.position < len(self.tokens) and self.tokens[self.position][0] == 'ELSE':
            self.position += 1  # Pula o 'ELSE'
            while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END':
                else_block_tokens.append(self.tokens[self.position])
                self.position += 1
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END':
            raise SyntaxError("Esperado 'end' para fechar o bloco if")
        
        self.position += 1  # Pula o 'END'
        
        # Executa o bloco apropriado
        if condition_result:
            block_parser = Parser(if_block_tokens)
            block_parser.variables = self.variables.copy()
            block_parser.functions = self.functions
            block_parser.parse()
            self.variables.update(block_parser.variables)
        elif else_block_tokens:
            block_parser = Parser(else_block_tokens)
            block_parser.variables = self.variables.copy()
            block_parser.functions = self.functions
            block_parser.parse()
            self.variables.update(block_parser.variables)

    def parse_while(self): # Laco 'while'
        self.position += 1 # Pula o token 'WHILE'
        condition_tokens = [] # Lista de tokens da condicao
        
        # Coleta os tokens da condicao ate encontrar 'DO' ou um comando
        while self.position < len(self.tokens): # Loop para coletar os tokens da condicao
            current_token = self.tokens[self.position][0] # Pega o tipo do token
            if current_token == 'DO': # Verifica se o token atual e 'DO'
                self.position += 1  # Pula o 'DO' se existir
                break # Interrompe o loop
            elif current_token in ('LET', 'PRINT', 'INPUT', 'IF', 'ELSE', 'WHILE', 'FUNCTION', 'RETURN'): # Verifica se o token atual e um comando
                break # Interrompe o loop
            condition_tokens.append(self.tokens[self.position]) # Adiciona o token a lista de condicao
            self.position += 1 # Avanca para o proximo token
        
        # Coleta os tokens do corpo do loop ate encontrar 'END'
        loop_body_tokens = [] # Lista de tokens do corpo do loop
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END': # Verifica se o token atual e 'END'
            loop_body_tokens.append(self.tokens[self.position]) # Adiciona o token ao corpo do loop
            self.position += 1 # Avanca para o proximo token
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END': # Verifica se o token atual e 'END'
            raise SyntaxError("Esperado 'end' para fechar o loop 'while'") # Gera um erro se nao for
        
        self.position += 1  # Pula o token 'END'
        
        while True: # Loop do laco 'while'
            # Avalia a condicao usando um sub-parser
            condition_parser = Parser(condition_tokens) # Cria um novo parser para a condicao
            condition_parser.variables = self.variables.copy() # Copia as variaveis do escopo atual
            condition_parser.functions = self.functions # Copia as funcoes
            condition_result = condition_parser.evaluate_condition() # Avalia a condicao
            
            if not condition_result: # Se a condicao for falsa
                break # Interrompe o loop
            
            # Executa o corpo do loop usando um sub-parser
            loop_parser = Parser(loop_body_tokens) # Cria um novo parser para o corpo do loop
            loop_parser.variables = self.variables.copy() # Copia as variaveis do escopo atual
            loop_parser.functions = self.functions # Copia as funcoes
            loop_parser.parse() # Chama a funcao de analise sintatica
            self.variables.update(loop_parser.variables) # Atualiza as variaveis do escopo externo

    def parse_function(self): # Declaracao de funcao
        self.position += 1 # Pula o token 'FUNCTION'
        func_name = self.tokens[self.position][1] # Pega o nome da funcao
        self.position += 1 # Pula o identificador
        parameters = [] # Lista de parametros
    
        if self.tokens[self.position][0] == 'OPEN_PAREN': # Verifica se o proximo token e '('
            self.position += 1 # Pula '('
            while self.tokens[self.position][0] != 'CLOSE_PAREN': # Verifica se o token atual e ')'
                if self.tokens[self.position][0] == 'IDENTIFIER': # Verifica se o token atual e um identificador
                    parameters.append(self.tokens[self.position][1]) # Adiciona o identificador a lista de parametros
                    self.position += 1 # Avanca para o proximo token
                    if self.tokens[self.position][0] == 'COMMA': # Verifica se o proximo token e ','
                        self.position += 1 # Pula ','
                else: # Se nao for um identificador 
                    raise SyntaxError("Parametros invalidos na definicao da funcao") # Gera um erro se nao for um identificador 
            self.position += 1  # Pula ')'
        else: # Se nao houver parametros
            raise SyntaxError("Esperado '(' apos o nome da funcao") # Gera um erro se nao houver parenteses de abertura
    
        func_body_tokens = [] # Lista de tokens do corpo da funcao
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END': # Verifica se o token atual e 'END' 
            func_body_tokens.append(self.tokens[self.position]) # Adiciona o token ao corpo da funcao 
            self.position += 1 # Avanca para o proximo token
    
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END': # Verifica se o token atual e 'END' 
            raise SyntaxError("Esperado 'end' para fechar a funcao") # Gera um erro se nao for 'END'
    
        self.position += 1  # Pula o token 'END'
    
        self.functions[func_name] = { # Adiciona a funcao ao dicionario de funcoes
            'parameters': parameters, # Parametros da funcao
            'body': func_body_tokens # Corpo da funcao
        }

    def parse_return(self): # Comando de retorno
        self.position += 1 # Pula o token 'RETURN'
        self.return_value = self.evaluate_expression() # Avalia a expressao de retorno
        self.position = len(self.tokens)  # Interrompe a execucao atual

    def parse_function_call(self, func_name): # Chamada de funcao
        self.position += 1  # Pula o nome da funcao
        args = [] # Lista de argumentos
    
        if self.tokens[self.position][0] == 'OPEN_PAREN': # Verifica se o proximo token e '('
            self.position += 1  # Pula '('
            while self.tokens[self.position][0] != 'CLOSE_PAREN': # Verifica se o token atual e ')'
                arg = self.evaluate_expression() # Avalia a expressao do argumento
                args.append(arg) # Adiciona o argumento a lista de argumentos
                if self.tokens[self.position][0] == 'COMMA': # Verifica se o proximo token e ','
                    self.position += 1  # Pula ','
            self.position += 1  # Pula ')'
        else: # Se nao houver argumentos
            raise SyntaxError("Esperado '(' apos o nome da funcao") # Gera um erro se nao houver parenteses de abertura
    
        if func_name not in self.functions: # Verifica se a funcao foi definida
            raise NameError(f"Funcao nao definida: {func_name}") # Gera um erro se a funcao nao foi definida
    
        function = self.functions[func_name] # Pega a funcao do dicionario de funcoes
        if len(args) != len(function['parameters']): # Verifica se o numero de argumentos e igual ao numero de parametros
            raise SyntaxError("Numero incorreto de argumentos na chamada da funcao") # Gera um erro se o numero de argumentos for diferente do numero de parametros
    
        func_parser = Parser(function['body']) # Cria um novo parser para a funcao
        func_parser.variables = self.variables.copy() # Copia as variaveis do escopo atual
        func_parser.functions = self.functions # Copia as funcoes
        func_parser.in_function = True # Indica que esta dentro de uma funcao
    
        for param, arg in zip(function['parameters'], args): # Associa os parametros com os argumentos
            func_parser.variables[param] = arg # Atribui o argumento ao parametro
     
        func_parser.parse() # Chama a funcao de analise sintatica 
    
        return_value = func_parser.return_value # Pega o valor de retorno da funcao

        return return_value # Retorna o valor de retorno

    def parse_assignment(self): # Atribuicao de variavel
        var_name = self.tokens[self.position][1]  # Pega o nome da variavel
        self.position += 1  # Pula o identificador
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'ASSIGN':  # Alterado de 'COMPARISON' para 'ASSIGN'
            raise SyntaxError("Erro de sintaxe em atribuicao de variavel")
        
        self.position += 1  # Pula o '='
        value = self.evaluate_expression()  # Avalia a expressao a direita do '='
        self.variables[var_name] = value

    def evaluate_expression(self): # Avalia a expressao
        result = self.get_term() # Pega o primeiro termo
        while self.position < len(self.tokens) and \
              self.tokens[self.position][0] in ('OPERATOR', 'LOGICAL', 'COMPARISON'): # Verifica se o token atual e um operador
            operator = self.tokens[self.position][1] # Pega o operador
            self.position += 1 # Avanca para o proximo token
            right = self.get_term() # Pega o proximo termo
            result = self.apply_operator(result, operator, right) # Aplica o operador
        return result # Retorna o resultado

    def get_term(self): # Pega o termo
        token_type, value = self.tokens[self.position] # Pega o tipo e o valor do token
        if token_type == 'LIST_START': # Verifica se o token e '['
            return self.parse_list() # Chama a funcao de lista
        elif token_type == 'NUMBER': # Verifica se o token e um numero
            self.position += 1 # Avanca para o proximo token
            return int(value) # Retorna o valor do numero
        elif token_type == 'IDENTIFIER': # Verifica se o token e um identificador
            next_token = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else (None, None) # Pega o proximo token
            if next_token[0] == 'OPEN_PAREN': # Verifica se o proximo token e '('
                result = self.parse_function_call(value) # Chama a funcao de chamada de funcao
                return result # Retorna o resultado
            else: # Se nao for uma chamada de funcao
                self.position += 1 # Avanca para o proximo token
                if value in self.variables: # Verifica se a variavel foi definida
                    return self.variables[value] # Retorna o valor da variavel
                else: # Se a variavel nao foi definida
                    raise NameError(f"Variavel nao definida: {value}") # Gera um erro
        elif token_type == 'OPEN_PAREN': # Verifica se o token e '('
            self.position += 1 # Pula '('
            value = self.evaluate_expression() # Avalia a expressao
            if self.tokens[self.position][0] != 'CLOSE_PAREN': # Verifica se o proximo token e ')'
                raise SyntaxError("Esperado ')' na expressao") # Gera um erro se nao for
            self.position += 1  # Pula ')'
            return value # Retorna o valor da expressao
        elif token_type == 'STRING':  # Adicione este caso
            self.position += 1
            return value[1:-1]  # Remove as aspas
        else: # Se nao for nenhum dos tipos acima
            raise SyntaxError(f"Expressao invalida: {value}") # Gera um erro
 
    def parse_list(self): # Lista
        self.position += 1  # Skip '['
        elements = [] # Lista de elementos
        
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'LIST_END': # Verifica se o token atual e ']'
            value = self.evaluate_expression() # Avalia a expressao
            elements.append(value) # Adiciona o valor a lista
            
            if self.position < len(self.tokens) and self.tokens[self.position][0] == 'COMMA': # Verifica se o token atual e ','
                self.position += 1 # Pula ','
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'LIST_END': # Verifica se o token atual e ']'
            raise SyntaxError("Lista nao fechada: esperado ']'") # Gera um erro se nao for ']'
            
        self.position += 1  # Skip ']'
        return elements # Retorna a lista de elementos

    def evaluate_condition(self): # Avalia a condicao
        return self.evaluate_expression() # Avalia a expressao

    def apply_operator(self, left, operator, right): # Aplica o operador a expressao 
        if operator == '+': # Adicao 
            if isinstance(left, list) or isinstance(right, list): # Verifica se left ou right e uma lista
                if isinstance(left, list) and isinstance(right, list): # Verifica se ambos sao listas
                    return left + right # Concatena as listas
                elif isinstance(left, list): # Verifica se left e uma lista
                    return left + [right] # Adiciona right a lista left
                else: # Se right for uma lista
                    return [left] + right # Adiciona left a lista right
            return left + right # Soma os valores
        elif operator == '-': # Subtracao
            return left - right # Subtrai os valores 
        elif operator == '*': # Multiplicacao
            return left * right # Multiplica os valores
        elif operator == '/': # Divisao
            return left / right # Divide os valores
        elif operator == '>': # Maior que
            return left > right # Verifica se left e maior que right
        elif operator == '<': # Menor que
            return left < right # Verifica se left e menor que right
        elif operator == '>=': # Maior ou igual
            return left >= right # Verifica se left e maior ou igual a right
        elif operator == '<=': # Menor ou igual
            return left <= right # Verifica se left e menor ou igual a right
        elif operator == '==': # Igualdade
            return left == right # Verifica se left e igual a right
        elif operator == '!=': # Diferente
            return left != right # Verifica se left e diferente de right
        elif operator == 'and': # Operador logico 'and'
            return left and right # Verifica se left e right sao verdadeiros
        elif operator == 'or': # Operador logico 'or'
            return left or right # Verifica se left ou right sao verdadeiros
        elif operator == 'not': # Operador logico 'not'
            return not right # Verifica se right e falso
        else: # Se o operador for desconhecido
            raise SyntaxError(f"Operador desconhecido: {operator}") # Gera um erro se o operador for desconhecido

    def parse_for(self): # Laco 'for'
        self.position += 1  # Pula 'for'
        
        # Pega o nome da variavel de iteracao
        if self.tokens[self.position][0] != 'IDENTIFIER': # Verifica se o token atual e um identificador
            raise SyntaxError("Esperado um identificador apos 'for'") # Gera um erro se nao for
        iterator_var = self.tokens[self.position][1] # Pega o nome da variavel
        self.position += 1 # Pula o identificador
        
        # Verifica a palavra 'in'
        if self.tokens[self.position][0] != 'IN': # Verifica se o token atual e 'in'
            raise SyntaxError("Esperado 'in' apos o identificador no laco for") # Gera um erro se nao for
        self.position += 1 # Pula 'in'
        
        # Avalia a expressao que gera a sequencia (lista) 
        sequence = self.evaluate_expression() # Avalia a expressao
        if not isinstance(sequence, list): # Verifica se a sequencia e uma lista
            raise TypeError("For precisa de uma lista para iterar") # Gera um erro se nao for
        
        # Coleta os tokens do corpo do loop ate encontrar 'END'
        loop_body_tokens = [] # Lista de tokens do corpo do loop
        while self.position < len(self.tokens) and self.tokens[self.position][0] != 'END': # Verifica se o token atual e 'END'
            loop_body_tokens.append(self.tokens[self.position]) # Adiciona o token ao corpo do loop
            self.position += 1 # Avanca para o proximo token
        
        if self.position >= len(self.tokens) or self.tokens[self.position][0] != 'END': # Verifica se o token atual e 'END'
            raise SyntaxError("Esperado 'end' para fechar o laco 'for'") # Gera um erro se nao for
        
        self.position += 1  # Pula o token 'END'
        
        # Executa o corpo do loop para cada elemento da sequencia
        for item in sequence: # Itera sobre a sequencia
            # Cria um novo parser para cada iteracao
            loop_parser = Parser(loop_body_tokens) # Cria um novo parser para o corpo do loop
            loop_parser.variables = self.variables.copy() # Copia as variaveis do escopo atual
            loop_parser.functions = self.functions # Copia as funcoes
            
            # Define a variavel de iteracao
            loop_parser.variables[iterator_var] = item # Atribui o item a variavel de iteracao
            
            # Executa o corpo do loop
            loop_parser.parse() # Chama a funcao de analise sintatica 
            
            # Atualiza as variaveis do escopo externo
            self.variables.update(loop_parser.variables) # Atualiza as variaveis do escopo externo

def suggest_correction(error_message, code_lines):
    """
    Sugere correcoes para erros comuns no codigo.
    
    Args:
        error_message (str): Mensagem de erro
        code_lines (list): Linhas do codigo
        
    Returns:
        str: Sugestao de correcao
    """
    suggestion = {
        "Token desconhecido": "Verifique a sintaxe do seu codigo.",
        "Erro de sintaxe em declaracao de variavel": "Certifique-se de usar 'let' para declarar variaveis e '=' para atribuir valores.",
        "Variavel nao definida": "Verifique se a variavel foi declarada antes de usa-la.",
        "Funcao nao definida": "Verifique se a funcao foi declarada antes de chama-la.",
        "Expressao invalida": "Verifique a expressao para garantir que esta correta.",
        "Operador desconhecido": "Use operadores validos como +, -, *, /, >, <, ==, and, or, not.",
        "Esperado 'do' apos a condicao 'while'": "Inclua 'do' apos a condicao do 'while'.",
        "Esperado 'end' para fechar o loop 'while'": "Certifique-se de fechar o loop 'while' com 'end'.",
        "Parametros invalidos na definicao da funcao": "Verifique a lista de parametros na definicao da funcao.",
        "Esperado '(' apos o nome da funcao": "Inclua '(' apos o nome da funcao.",
        "Numero incorreto de argumentos na chamada da funcao": "Verifique o numero de argumentos ao chamar a funcao.",
        "Entrada invalida: esperado um numero inteiro.": "Certifique-se de inserir um numero inteiro valido.",
        "Lista nao fechada: esperado ']'": "Certifique-se de fechar a lista com ']'.",
    }
    for error, suggestion_text in suggestion.items(): # Itera sobre as sugestoes
        if error in error_message: # Verifica se o erro esta na mensagem
            return suggestion_text # Retorna a sugestao
    return "Corrija o erro no codigo." # Retorna uma mensagem padrao

def export_error(filename, error_message, code_lines): # Exporta informacoes de erro para um arquivo
    """
    Exporta informacoes de erro para um arquivo.
    
    Args:
        filename (str): Nome do arquivo de saida
        error_message (str): Mensagem de erro
        code_lines (list): Linhas do codigo
    """
    with open(filename, 'w') as file: # Abre o arquivo para escrita
        file.write(f"Erro: {error_message}\n") # Escreve a mensagem de erro
        file.write("Codigo com erro:\n") # Escreve o cabecalho
        for i, line in enumerate(code_lines, start=1): # Itera sobre as linhas do codigo
            file.write(f"{i}: {line}\n") # Escreve a linha no arquivo

def save_file(filename, code_lines): # Salva o codigo em um arquivo
    """
    Salva o codigo em um arquivo.
    
    Args:
        filename (str): Nome do arquivo
        code_lines (list): Linhas do codigo
    """
    with open(filename, 'w') as file: # Abre o arquivo para escrita
        file.write("\n".join(code_lines)) # Escreve o codigo no arquivo

def open_file(filename): # Abre e le um arquivo
    """
    Abre e le um arquivo de codigo.
    
    Args:
        filename (str): Nome do arquivo
        
    Returns:
        list: Linhas do codigo lido
        
    Raises:
        FileNotFoundError: Se o arquivo nao existir
    """
    with open(filename, 'r') as file: # Abre o arquivo para leitura
        return file.readlines() # Le as linhas do arquivo

def clear_console(): # Limpa o console
    os.system('clear') # Executa o comando 'clear' no terminal. So pode utilizar 'cls' caso seja no VSCode
    print("Digite seu codigo. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.\n") # Exibe mensagem de inicio
    print("Para salvar o codigo, digite 'salvar <nome_do_arquivo>'. Para abrir um arquivo, digite 'abrir <nome_do_arquivo>'.\n") # Exibe mensagem de salvar/abrir arquivo
    print("Para desfazer a ultima acao, digite 'desfazer'. Para refazer a ultima acao desfeita, digite 'refazer'.\n") # Exibe mensagem de desfazer/refazer
    print("Para limpar o console, digite 'clear'. Para excluir o codigo feito, digite 'excluir'.\n") # Exibe mensagem de limpar/excluir codigo

def execute_user_code(): # Funcao principal
    """ 
    Funcao principal que executa o loop interativo do editor.
    
    Implementa:
        - Interface de linha de comando
        - Sistema de undo/redo
        - Compilacao do codigo
        - Manipulacao de arquivos
    """
    print("Digite seu codigo. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.\n") # Exibe mensagem de inicio
    print("Para salvar o codigo, digite 'salvar <nome_do_arquivo>'. Para abrir um arquivo, digite 'abrir <nome_do_arquivo>'.\n") # Exibe mensagem de salvar/abrir arquivo
    print("Para desfazer a ultima acao, digite 'desfazer'. Para refazer a ultima acao desfeita, digite 'refazer'.\n") # Exibe mensagem de desfazer/refazer

    code_lines = [] # Lista de linhas de codigo
    undo_stack = [] # Pilha de desfazer
    redo_stack = [] # Pilha de refazer


    def undo(): # Desfaz a ultima acao
        if code_lines: # Verifica se ha acoes para desfazer
            last_action = code_lines.pop() # Remove a ultima acao
            undo_stack.append(last_action) # Adiciona a acao a pilha de desfazer
            print("Acao desfeita.") # Exibe mensagem de acao desfeita
        else:
            print("Nao ha acoes para desfazer.") # Exibe mensagem se nao houver acoes para desfazer

    def redo(): # Refaz a ultima acao desfeita
        if undo_stack: # Verifica se ha acoes para refazer
            last_undo = undo_stack.pop() # Remove a ultima acao desfeita
            code_lines.append(last_undo) # Adiciona a acao de volta ao codigo
            print("Acao refeita.") # Exibe mensagem de acao refeita
        else:
            print("Nao ha acoes para refazer.") # Exibe mensagem se nao houver acoes para refazer

    while True: # Loop principal
        line = input(">>> ") # Le a entrada do usuario
        if line.strip().lower() == 'sair': # Verifica se o usuario digitou 'sair'
            break
        elif line.strip().lower() == 'compilar': # Verifica se o usuario digitou 'compilar'
            code = "\n".join(code_lines) # Junta as linhas de codigo em uma unica string
            try: # Tenta compilar o codigo
                tokens = lexer(code) # Realiza a analise lexica
                parser = Parser(tokens) # Cria um parser
                parser.parse() # Realiza a analise sintatica e executa o codigo
            except (SyntaxError, NameError) as e: # Trata erros de sintaxe e nomes
                erro_msg = str(e) # Pega a mensagem de erro
                print(f"Erro: {erro_msg}") # Exibe a mensagem de erro
                linha_erro = len(code_lines) # Pega a linha do erro
                if linha_erro > 0: # Verifica se ha codigo
                    print(f"Erro na linha {linha_erro}: {code_lines[linha_erro-1]}") # Exibe a linha do erro
                sugestao = suggest_correction(erro_msg, code_lines) # Sugere uma correcao para o erro
                print(f"Sugestao: {sugestao}") # Exibe a sugestao
                corrigir = input("Deseja corrigir a linha? (s/n): ").strip().lower() # Pergunta se deseja corrigir a linha
                if corrigir == 's': # Verifica se deseja corrigir a linha
                    nova_linha = input("Digite a linha corrigida: ") # Le a nova linha
                    if 0 < linha_erro <= len(code_lines): # Verifica se a linha do erro e valida
                        code_lines[linha_erro-1] = nova_linha # Substitui a linha do erro pela nova linha
                exportar = input("Deseja exportar o erro para um arquivo? (s/n): ").strip().lower() # Pergunta se deseja exportar o erro
                if exportar == 's': # Verifica se deseja exportar o erro
                    nome_arquivo = input("Digite o nome do arquivo para exportar o erro: ") # Pede o nome do arquivo
                    export_error(nome_arquivo, erro_msg, code_lines) # Exporta o erro para o arquivo
                    print(f"Erro exportado para o arquivo {nome_arquivo}.") # Exibe mensagem de erro exportado
        elif line.strip().lower().startswith('salvar '): # Verifica se o usuario digitou 'salvar'
            filename = line.strip().split(' ', 1)[1] # Pega o nome do arquivo
            save_file(filename, code_lines) # Salva o codigo no arquivo
            print(f"Arquivo {filename} salvo com sucesso.") # Exibe mensagem de arquivo salvo
        elif line.strip().lower().startswith('abrir '): # Verifica se o usuario digitou 'abrir'
            filename = line.strip().split(' ', 1)[1] # Pega o nome do arquivo
            try: # Tenta abrir o arquivo 
                code_lines = open_file(filename) # Abre o arquivo
                print(f"Arquivo {filename} aberto com sucesso.") # Exibe mensagem de arquivo aberto
                for i, code_line in enumerate(code_lines): # Exibe o codigo do arquivo
                    print(f"{i+1}: {code_line.strip()}") # Exibe a linha do codigo
            except FileNotFoundError: # Trata erro de arquivo nao encontrado
                print(f"Arquivo {filename} nao encontrado.") # Exibe mensagem de arquivo nao encontrado
        elif line.strip().lower() == 'desfazer': # Verifica se o usuario digitou 'desfazer'
            undo() # Desfaz a ultima acao
        elif line.strip().lower() == 'refazer': # Verifica se o usuario digitou 'refazer'
            redo() # Refaz a ultima acao desfeita
        elif line.strip().lower() == 'clear': # Verifica se o usuario digitou 'clear'
            clear_console() # Limpa o console
        elif line.strip().lower() == 'excluir': # Verifica se o usuario digitou 'excluir'
            if not code_lines: # Verifica se ha codigo
                print("Nao ha codigo para limpar.") # Exibe mensagem se nao houver codigo
            else: # Se houver codigo
                code_lines.clear() # Limpa o codigo
                print("Codigo excluido com sucesso.") # Exibe mensagem de codigo excluido
        else: # Se nao for um comando
            code_lines.append(line) # Adiciona a linha ao codigo
            undo_stack.clear() # Limpa a pilha de desfazer

execute_user_code() # Executa o loop interativo do editor
