import re #importa a biblioteca de expressões regulares
import os

# Dicionário com os padrões de tokens.
# Cada token representa uma palavra reservada ou tipo de valor reconhecido pelo interpretador.
TOKENS = {
    'LET': r'\blet\b',            # Palavra reservada para declaração de variável.
    'PRINT': r'\bprint\b',        # Palavra reservada para exibir valores.
    'IF': r'\bif\b',              # Palavra reservada para estrutura condicional.
    'ELSE': r'\belse\b',          # Palavra reservada para bloco 'else' da condição.
    'FOR': r'\bfor\b',
    'END': r'\bend\b',            # Palavra reservada para fim de blocos de código condicional.
    'NUMBER': r'\b\d+\b',         # Números inteiros.
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',  # Identificadores de variáveis.
    'OPERATOR': r'[+\-*/^]',       # Operadores matemáticos.
    'COMPARISON': r'[><=]+',      # Operadores de comparação.
}

# Função lexer: converte o código do usuário em uma lista de tokens para serem processados pelo parser.
def lexer(code):
    tokens = []
    code = code.strip()  # Remove espaços no início e no final do código.
    while code:  # Continua enquanto houver código não processado.
        match = None
        for token_type, pattern in TOKENS.items():
            regex = re.compile(pattern)
            match = regex.match(code)  # Verifica se há correspondência com algum token.
            if match:
                # Adiciona o token encontrado à lista.
                tokens.append((token_type, match.group(0)))
                # Remove o token encontrado do código para continuar o processamento.
                code = code[match.end():].strip()
                break
        if not match:
            # Caso não encontre um token, gera um erro de sintaxe.
            raise SyntaxError(f"Token desconhecido: {code[:10]}")
    return tokens

# Classe Parser: analisa e executa os tokens gerados pelo lexer.
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens      # Lista de tokens para processar.
        self.position = 0         # Posição atual no array de tokens.
        self.variables = {}       # Dicionário para armazenar variáveis e seus valores.

    def parse(self):
        try:
            # Itera através dos tokens, identificando e processando comandos.
            while self.position < len(self.tokens):
                token_type, value = self.tokens[self.position]
                if token_type == 'LET':
                    self.parse_let()   # Chama função para processar declaração de variável.
                elif token_type == 'PRINT':
                    self.parse_print()  # Chama função para processar comando de impressão.
                elif token_type == 'IF':
                    self.parse_if()     # Chama função para processar a estrutura condicional.
                elif token_type == 'FOR':
                    self.parse_for() 
        except IndexError as e:
            raise IndexError(f'Erro ao executar a função: {e}')
 

    def parse_let(self):
        # Processa uma declaração de variável.
        self.position += 1
        var_name = self.tokens[self.position][1]  # Nome da variável.
        self.position += 1
        if self.position >= len(self.tokens) or self.tokens[self.position][1] != '=':
            # Erro se não encontrar um operador de atribuição após o nome da variável.
            raise SyntaxError("Erro de sintaxe em declaração de variável")
        self.position += 1
        value = self.evaluate_expression()  # Avalia a expressão à direita do '='.
        self.variables[var_name] = value    # Armazena o valor da variável.

    def parse_print(self):
        try:
            # Processa um comando para exibir valores.
            self.position += 1
            value = self.evaluate_expression()  # Avalia a expressão a ser exibida.
            print("Saída:", value)  # Imprime o valor avaliado.
        except IndexError as e:
            raise IndexError('Erro ao digitar a função print')

    def parse_if(self):
        try:
            # Processa uma estrutura condicional.
            self.position += 1
            condition = self.evaluate_condition()  # Avalia a condição do 'if'.
            if condition:
                self.position += 1
                self.parse()  # Executa o bloco 'if' se a condição for verdadeira.
            else:
                # Pula o bloco 'if' até encontrar 'else' ou 'end'.
                while self.tokens[self.position][0] != 'ELSE' and self.tokens[self.position][0] != 'END':
                    self.position += 1
                if self.tokens[self.position][0] == 'ELSE':
                    self.position += 1
                    self.parse()  # Executa o bloco 'else' se encontrado.
            # Finaliza a execução do bloco 'if' ao encontrar 'end'.
            while self.tokens[self.position][0] != 'END':
                self.position += 1
        except:
            raise('Erro no parse_if')

    def parse_for(self):
        try:
            # Processa um comando para exibir valores.
            self.position += 1
            value = self.evaluate_expression()  # Avalia a expressão a ser exibida.
            
            for i in range(value):
                print("contagem...", i+1)  # Imprime o valor avaliado.

            print()
            
        except:
            raise('Erro ao executar o for')

    def parse_limpar(self):
        ...


    def evaluate_expression(self):
        try:
            # Avalia uma expressão matemática.
            left_value = self.get_term()  # Pega o primeiro termo.
            # Processa operadores matemáticos.
            while self.position < len(self.tokens) and self.tokens[self.position][0] == 'OPERATOR':
                operator = self.tokens[self.position][1]
                self.position += 1
                right_value = self.get_term()  # Pega o próximo termo.
                left_value = self.apply_operator(left_value, operator, right_value)  # Aplica o operador entre os termos.
            return left_value
        except IndexError:
            raise IndexError('Index fora do contexto')

    def get_term(self):
        try:
            # Retorna o valor de um termo (número ou variável).
            token_type, value = self.tokens[self.position]
            if token_type == 'NUMBER':
                self.position += 1
                return int(value)  # Retorna o número como inteiro.
            elif token_type == 'IDENTIFIER':
                try:
                    self.position += 1
                    # Retorna o valor da variável, se existir.
                    if value in self.variables:
                        return self.variables[value]
                except NameError:
                    raise NameError('Erro dado ao nome da variável')

        except (NameError, SyntaxError) as e:
            # Erro caso a variável não esteja definida.
            print(f"Erro: {e}")

    def evaluate_condition(self):
        try:
            # Avalia uma condição (comparação entre expressões).
            left = self.evaluate_expression()  # Avalia a expressão à esquerda.
            operator = self.tokens[self.position][1]
            self.position += 1
            right = self.evaluate_expression()  # Avalia a expressão à direita.
            return self.apply_operator(left, operator, right)
        except:
            raise('Erro no evaluate_condition')

    def apply_operator(self, left, operator, right):
        # Aplica o operador aritmético ou comparativo.
        if operator == '+':
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
        else:
            # Erro para operadores não reconhecidos.
            raise SyntaxError(f"Operador desconhecido: {operator}")

# Função para execução do código do usuário com opção de compilar e corrigir erros.
def execute_user_code():
    print("Digite seu código. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.Para limpar digite 'cls'\n")
    code_lines = []  # Armazena as linhas digitadas pelo usuário.
    while True:
        line = input(">>> ")
        if line.strip().lower() == 'sair':
            break
        elif line.strip().lower() == 'compilar':
            code = "\n".join(code_lines)  # Junta todas as linhas para compilar.
            try:
                tokens = lexer(code)  # Gera os tokens a partir do código.
                parser = Parser(tokens)  # Cria o parser com os tokens.
                parser.parse()  # Processa e executa os tokens.
            except (SyntaxError, NameError) as e:
                erro_msg = str(e)
                print(f"Erro: {erro_msg}")
                # Exibe a última linha com erro para facilitar a correção.
                linha_erro = len(code_lines)
                print(f"Erro na linha {linha_erro}: {code_lines[linha_erro-1]}")
                # Permite ao usuário corrigir a linha com erro.
                corrigir = input("Deseja corrigir a linha? (s/n): ").strip().lower()
                if corrigir == 's':
                    nova_linha = input("Digite a linha corrigida: ")
                    code_lines[linha_erro-1] = nova_linha  # Atualiza a linha corrigida.
        elif line.strip().lower() == 'cls':
            os.system('cls')
            print("Digite seu código. Para compilar e ver o resultado, digite 'compilar'. Para encerrar, digite 'sair'.Para limpar digite 'cls'\n")
        elif line.strip().lower() == 'excluir':
            for i in code_lines:
                code_lines.pop()
        else:
            # Adiciona a linha ao código.
            code_lines.append(line)

# Executa o código interativo
execute_user_code()