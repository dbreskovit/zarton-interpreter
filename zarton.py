import math
import sys
from typing import NamedTuple

#GRAMÁTICA

#<comandos>   -> <comando> { <comando> }
#<comando>    -> <if>
#              | <while>
#              | <positivo>
#              | <atrib>                         
#<bloco>      -> { [ <comandos> ] }               
#<if>         -> if ( <expc> ) <bloco> [ else <bloco> ]
#<while>      -> while ( <expc> ) <bloco>
#<positivo>   -> positivo ( <exp> ) <bloco> negativo <bloco> zero <bloco>
#<atrib>      -> _id_ = <expc> ;
#<expc>       -> <exp> [ <comp> <exp> ]
#<comp>       -> < | == | >
#<exp>        -> <termo> { <soma> <termo> }
#<soma>       -> + | - | @                  
#<termo>      -> <fator> { <mult> <fator> }
#<mult>       -> * | /
#<fator>      -> ( <expc> )
#              | _int_
#              | _float_
#              | _string_
#              | _id_
#              | <hip>                         
#<hip>        -> hip ( _id_ , _id_ )          

pos = 0 #Indica qual token está sendo lido
KEYWORDS = ['if', 'else', 'while', 'hip', 'positivo','negativo','zero'] #Palavras reservadas: não podem ser identificadores
tabela_simbolos = {} #tabela de símbolos
executar = True #Se falso analisa somente a sintaxe sem executar.
codigo_atual = ""

# {
#   "x": {"tipo": "INT", "valor": 5},
#   "y": {"tipo": "FLOAT", "valor": 0.1}
# }
#
# tabela_simbolos["x"] = {"tipo": "INT", "valor": 5}
# y = tabela_simbolos["y"]

# ==================================== análise léxica ==

class Token(NamedTuple):
    tipo: str
    lexema: str
    posicao: int


class ErroLexico(Exception):
    pass


def tokenizar(codigo):
    entrada = codigo + "\0"
    tokens = []
    estado = 0
    pos = 0
    inicio = 0

    def linha(p):
        return "na linha " + str(codigo[:p].count("\n") + 1) + ": "

    def emitir(tipo):
        nonlocal inicio
        tokens.append(Token(tipo, entrada[inicio:pos], inicio))
        inicio = pos

    while pos < len(entrada):
        if estado == 0:
            caractere = entrada[pos]
            if caractere == "\0":
                pos += 1
            elif caractere.isalpha() or caractere == "_":
                estado = 1
                pos += 1
            elif caractere.isdigit():
                estado = 5
                pos += 1
            elif caractere == "#":
                estado = 10
                pos += 1
            elif entrada.startswith("/*", pos):
                estado = 11
                pos += 2
            elif caractere == '"':
                estado = 13
                pos += 1
            elif caractere == "'":
                estado = 15
                pos += 1
            elif caractere in ["+", "-", "/", "*", "@"]:
                estado = 6
                pos += 1
            elif caractere in ["=", ">", "<", "!"]:
                estado = 7
                pos += 1
            elif caractere in [" ", "\n", "\t", "\r"]:
                pos += 1
                inicio = pos
            elif caractere in ["(", ")", ",", ";", "{", "}"]:
                pos += 1
                emitir("PONTUACAO")
            else:
                raise ErroLexico(linha(pos) + "o símbolo '" + caractere + "' não foi identificado"
                )
        elif estado == 1:
            if entrada[pos].isalnum() or entrada[pos] == "_":
                pos += 1
            else:
                estado = 2
        elif estado == 2:
            lexema = entrada[inicio:pos]
            tipo = "RESERVADA" if lexema in KEYWORDS else "ID"
            emitir(tipo)
            estado = 0
        elif estado == 5:
            if entrada[pos].isdigit():
                pos += 1
            elif (entrada[pos] in [".", ","] and entrada[pos + 1].isdigit()):
                estado = 8
                pos += 1
            else:
                estado = 4
        elif estado == 8:
            if entrada[pos].isdigit():
                pos += 1
            else:
                estado = 9
        elif estado == 4:
            emitir("INT")
            estado = 0
        elif estado == 9:
            if pos == inicio or entrada[pos - 1] == ".":
                raise ErroLexico(linha(inicio) + "número decimal inválido")
            emitir("FLOAT")
            estado = 0
        elif estado == 6:
            lexema = entrada[inicio:pos]
            emitir("ATRIBUICAO" if lexema == "=" else "OP")
            estado = 0
        elif estado == 7:
            if entrada[pos] == "=":
                pos += 1
            estado = 6
        elif estado == 10:
            if entrada[pos] in ["\n", "\0"]:
                estado = 0
                pos += 1
                inicio = pos
            else:
                pos += 1
        elif estado == 11:
            if entrada.startswith("*/", pos):
                pos += 2
                inicio = pos
                estado = 0
            elif entrada[pos] == "\0":
                raise ErroLexico(linha(inicio) + "faltou fechar o comentário")
            else:
                pos += 1
        elif estado == 13:
            if entrada[pos] == '"':
                pos += 1
                estado = 14
            elif entrada[pos] == "\0":
                raise ErroLexico(linha(inicio) + "string sem fechamento")
            else:
                pos += 1
        elif estado == 14:
            emitir("STRING")
            estado = 0
        elif estado == 15:
            if entrada[pos] == "'":
                pos += 1
                estado = 17
            elif entrada[pos] == "\0":
                raise ErroLexico(linha(inicio) + "char sem fechamento")
            else:
                estado = 16
                pos += 1
        elif estado == 16:
            if entrada[pos] == "'":
                pos += 1
                estado = 19
            elif entrada[pos] == "\0":
                raise ErroLexico(linha(inicio) + "char sem fechamento")
            else:
                estado = 18
                pos += 1
        elif estado == 18:
            if entrada[pos] == "'":
                pos += 1
                estado = 20
            elif entrada[pos] == "\0":
                raise ErroLexico(linha(inicio) + "char sem fechamento")
            else:
                pos += 1
        elif estado == 19:
            emitir("CHAR")
            estado = 0
        elif estado == 17:
            raise ErroLexico(linha(inicio) + "char vazio")
        elif estado == 20:
            raise ErroLexico(linha(inicio) + "o char deveria ter no máximo 1 símbolo")

    return tokens

# ==================================== interpretador ==

def obter_linha(indice=None):
    if indice is None:
        indice = pos
    if not tokens:
        return 1
    idx = min(max(indice, 0), len(tokens) - 1)
    return codigo_atual[:tokens[idx].posicao].count("\n") + 1

def erro_semantico(msg, linha=None):
    if linha is None:
        linha = obter_linha()
    print(f"Erro Semântico na linha {linha}:", msg)
    sys.exit(1)

def executar_operacao(esquerda, op, direita):
    if not executar:
        return (None, None)

    tipo = "INT"
    valor = 0

    #Trata a comparação (resultado padrão: INT 0, ou seja, falso)
    if op in ['<','==','>']:
        if op == '==' and esquerda[1] == direita[1]:
            valor = 1
        if op == '<' and esquerda[1] < direita[1]:
            valor = 1
        if op == '>' and esquerda[1] > direita[1]:
            valor = 1
        return (tipo, valor)

    #Trata a divisão
    if op == '/':
        if direita[1] == 0:
            erro_semantico("Divisão por zero.")
        valor = esquerda[1] / direita[1]
        tipo = "FLOAT"
        return (tipo, valor)

    #computa o valor das operações + - * @
    if op == '+':
        valor = esquerda[1] + direita[1]
    elif op == '-':
        valor = esquerda[1] - direita[1]
    elif op == '*':
        valor = esquerda[1] * direita[1]
    elif op == '@':
        valor = max(esquerda[1], direita[1])
    else:
        #Não deveria chegar aqui: léxico ou sintático já deveria proibir operadores inválidos
        erro_semantico("Operador desconhecido '" + op + "'.")

    #Infere o tipo do retorno de + - * @
    if esquerda[0] == "FLOAT" or direita[0] == "FLOAT":
        tipo = "FLOAT"

    return (tipo, valor)

#Retorna (tipo,valor) do identificador ou causa erro semântico se não declarado.
def buscar_identificador(identificador):
    if not executar:
        return (None, None)

    if identificador not in tabela_simbolos:
        erro_semantico("Identificador '" + identificador + "' não declarado.")

    valor = tabela_simbolos[identificador]['valor'] #capturar antes do consumo
    tipo  = tabela_simbolos[identificador]['tipo'] #capturar antes do consumo

    return (tipo,valor)

#Atualiza na tabela de símbolos o identificador com x = (tipo,valor)
def salvar_identificador(identificador, x):
    if not executar:
        return

    tabela_simbolos[identificador] = {"tipo": x[0], "valor": x[1]}
    if identificador in ["z","Z"]:
        print(identificador, "=", str(x[1]))

#Hipotenusa dos catetos a e b, recebidos como (tipo, valor). Sempre retorna FLOAT.
def calcular_hip(a, b):
    if not executar:
        return (None, None)
    return ("FLOAT", math.sqrt(a[1] * a[1] + b[1] * b[1]))

#Mostra o texto e lê um número do teclado
def ler_entrada(texto):
    if not executar:
        return (None, None) #Bloco pulado: não pede nada ao usuário
    digitado = input(texto + " ").strip()
    if digitado.isdigit():
        return ("INT", int(digitado))
    try:
        return ("FLOAT", float(digitado))
    except ValueError:
        erro_semantico("o valor digitado '" + digitado + "' não é um número.")

#Retorna falso se o valor do número for 0, ou True caso contrário
#Receber o número como (tipo, valor)
def verdadeiro(numero):
    if not executar:
        return False

    if numero[1] == 0:
        return False
    else:
        return True

#Analisar apenas a sintaxe do bloco de comandos sem executar.
def pular_comandos():
    global executar
    anterior = executar
    executar = False
    regra_comandos()
    executar = anterior

# ==================================== análise sintática ==

#Retorna o token atual
def token_atual():
    if pos < len(tokens):
        return tokens[pos].lexema
    else:
        return None

#Texto do token atual para mensagens de erro
def encontrado():
    if token_atual() is None:
        return "o fim do arquivo"
    return "'" + token_atual() + "'"

def tipo_token_atual():
    if pos < len(tokens):
        return tokens[pos].tipo
    else:
        return None

#Função de relatório de erro sintático
def erro_sintatico(msg, linha=None):
    if linha is None:
        linha = obter_linha()
    print("Contexto: " + ' '.join(token.lexema for token in tokens[0:pos]))
    print(f"Erro Sintático na linha {linha}:", msg)
    sys.exit(1)

#avalia se o token é igual ao token esperado
#se for avança para o proximo token, senão causa um erro.
def consumir(token_esperado):
    global pos
    if token_atual() == token_esperado:
        pos = pos + 1 #avança para o proximo token
    else:
        erro_sintatico("era esperado '" + token_esperado + "' mas encontrou " + encontrado())

#Consome um identificador e retorna o nome dele, ou causa erro sintático.
def consumir_identificador():
    identificador = token_atual() #capturar antes do consumo
    if tipo_token_atual() != "ID":
        erro_sintatico("era esperado um identificador mas encontrou '" + str(identificador) + "'")
    consumir(identificador)
    return identificador

# <hip> -> hip ( _id_ , _id_ )
# z = hip ( a , b ) ;
def regra_hip():
    consumir("hip")
    consumir("(")
    a = buscar_identificador(consumir_identificador())
    consumir(",")
    b = buscar_identificador(consumir_identificador())
    consumir(")")
    return calcular_hip(a, b)

# <fator> -> (<expc>) | _int_ | _float_ | _string_ | _id_ | <hip>
# (7 + 6)
# Retorna (tipo, valor)
def regra_fator():
    if token_atual() == "hip":
        return regra_hip()
    elif token_atual() == "(":
        consumir("(")
        temp = regra_expc() #("INT", 11)
        consumir(")")
        return temp #retorno depois do consumo
    elif tipo_token_atual() == "FLOAT":
        numero = float(token_atual().replace(",", ".")) # 2,5 -> 2.5
        consumir(token_atual())
        return ("FLOAT", numero)
    elif tipo_token_atual() == "INT":
        numero = int(token_atual()) # capturar antes do consumo
        consumir(token_atual())
        return ("INT", numero) # retornar depois do consumo
    elif tipo_token_atual() == "STRING":
        texto = token_atual()[1:-1] # capturar antes do consumo, sem as aspas
        consumir(token_atual())
        return ler_entrada(texto)
    elif tipo_token_atual() == "ID":
        identificador = token_atual() # capturar antes do consumo
        consumir(token_atual())
        (tipo, valor) = buscar_identificador(identificador)
        return (tipo, valor)
    else:
        erro_sintatico("era esperado '(', um número, uma string ou um identificador mas encontrou " + encontrado())

# <termo> -> <fator> { <mult> <fator> }
# a = 2 * 3 * 4
def regra_termo():
    esquerda = regra_fator() # ("INT", 2)
    while token_atual() in ['*','/']:
        op = token_atual() #Guarda o operador antes de consumir
        consumir(token_atual())
        direita = regra_fator() #("INT", 3)
        esquerda = executar_operacao(esquerda, op, direita) # ("INT", 6)
    return esquerda

# <exp> -> <termo> { <soma> <termo> }
# a = 1 - 2
def regra_exp():
    esquerda = regra_termo() # ("INT", 1)
    while token_atual() in ['+','-', '@']:
        op = token_atual()
        consumir(token_atual())
        direita = regra_termo() #("INT", 2)
        esquerda = executar_operacao(esquerda, op, direita)
    return esquerda #("INT",-1)

# <expc> -> <exp> [ <comp> <exp> ]
# a = 1 + 1 < 2 + 2
def regra_expc():
    esquerda = regra_exp() # ("INT", 2)
    if token_atual() in ['<','==','>']:
        op = token_atual()
        consumir(token_atual()) # <
        direita = regra_exp() # ("INT", 4)
        esquerda = executar_operacao(esquerda, op, direita) # ("INT", 1)
    return esquerda

# <atrib> -> _id_ = <expc> ;
# a = 1 + 1 ;
def regra_atrib():
    if tipo_token_atual() == "ID":
        identificador = token_atual() #Capturando antes do consumo o id
        consumir(token_atual()) #a
        consumir("=")
        temp = regra_expc() # ("INT", 2)
        consumir(";")
        salvar_identificador(identificador, temp)
        #NÃO TEM RETURN
    else:
        erro_sintatico("era esperado um identificador mas encontrou " + encontrado())

# <if> -> if ( <expc> ) { <comandos> } [ else { <comandos> } ]
# a = 1 ;
# if ( a < 5 ) {
#     b = 0 ;
# } else {
#     b = 1 ;
# }
def regra_if():
    consumir("if")
    consumir("(")
    condicao = regra_expc() # ("INT", 1)
    consumir(")")
    consumir("{")
    if verdadeiro(condicao):
        regra_comandos()
    else:
        pular_comandos()
    consumir("}")
    if token_atual() == "else":
        consumir("else")
        consumir("{")
        if not verdadeiro(condicao):
            regra_comandos()
        else:
            pular_comandos()
        consumir("}")

def sinal(numero):
    if not executar:
        return None

    if numero[1] > 0:
        return "positivo"
    elif numero[1] < 0:
        return "negativo"
    elif numero[1] == 0:
        return "zero"

def regra_bloco(executa):
    consumir("{")
    if token_atual() != "}":
        if executa:
            regra_comandos()
        else:
            pular_comandos()
    consumir("}")

def regra_positivo():
    consumir("positivo")
    consumir("(")
    resultado = sinal(regra_exp()) # "negativo"
    consumir(")")
    regra_bloco(resultado == "positivo")
    consumir("negativo")
    regra_bloco(resultado == "negativo")
    consumir("zero")
    regra_bloco(resultado == "zero")

# <while> -> while ( <expc> ) { <comandos> }
# x = 0 ;
# while ( x < 2 ) {
#     x = x + 1 ;
# }
def regra_while():
    global pos
    consumir("while")
    consumir("(")
    pos_cond = pos #guardar a posição do token antes de avaliar a condição
    while True:
        cond = regra_expc() # ("INT",1)
        consumir(")")
        consumir("{")
        if verdadeiro(cond):
            regra_comandos()
            consumir("}")
            pos = pos_cond #Restaura a posição para o token antes da condição
        else:
            #Condição falsa: analisa o corpo sem executar e sai do laço
            pular_comandos()
            consumir("}")
            break

# <comando> -> <if> | <while> | <positivo> | <atrib>
def regra_comando():
    if token_atual() == "if":
        regra_if()
    elif token_atual() == "while":
        regra_while()
    elif token_atual() == "positivo":
        regra_positivo()
    elif tipo_token_atual() == "ID":
        regra_atrib()
    else:
        erro_sintatico("era esperado 'if', 'while', 'positivo' ou um identificador mas encontrou " + encontrado())

# <comandos> -> <comando> { <comando> }
def regra_comandos():
    regra_comando()
    while tipo_token_atual() in ["ID", "RESERVADA"]:
        regra_comando()

def rodar(codigo):
    global pos, tokens, tabela_simbolos, executar, codigo_atual
    codigo_atual = codigo
    pos = 0
    tokens = []
    tabela_simbolos = {}
    executar = True
    try:
        tokens = tokenizar(codigo)
    except ErroLexico as erro:
        print("Erro Léxico", erro)
        sys.exit(1)
    regra_comandos() #chamando a regra inicial da gramática
    if pos < len(tokens):
        erro_sintatico("'" + token_atual() + "' não era esperado.")

# Uso: python3 zarton.py programa.zt
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 zarton.py <arquivo.zt>")
        sys.exit(1)
    try:
        with open(sys.argv[1], encoding="utf-8") as arquivo:
            codigo = arquivo.read()
    except OSError:
        print("Não foi possível abrir o arquivo '" + sys.argv[1] + "'.")
        sys.exit(1)
    rodar(codigo)