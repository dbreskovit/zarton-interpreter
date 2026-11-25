import math
import sys
from tokenizar import ErroLexico, tokenizar

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

# ==================================== interpretador ==

def obter_linha(indice=None):
    if indice is None:
        indice = pos
    if not codigo_atual:
        return 1
    if not tokens:
        return 1

    idx=min(max(indice, 0), len(tokens)-1)
    lexema = tokens[idx].lexema

    pos_char = codigo_atual.find(lexema)
    if pos_char == -1:
        return 1
    return codigo_atual[:pos_char].count("\n") + 1   

def erro_semantico(msg, linha=None):
    if linha is None:
        linha = obter_linha()
    print(f"Linha {linha}: Erro Semântico:", msg)
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
    print(f"Linha {linha}: Erro Sintático:", msg)
    sys.exit(1)

#avalia se o token é igual ao token esperado
#se for avança para o proximo token, senão causa um erro.
def consumir(token_esperado):
    global pos
    if token_atual() == token_esperado:
        pos = pos + 1 #avança para o proximo token
    else:
        erro_sintatico("era esperado '" + token_esperado + "' mas encontrou '" + str(token_atual()) + "'")

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
        numero = float(token_atual())
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
        erro_sintatico("era esperado '(', um número, uma string ou um identificador mas encontrou '" + str(token_atual()) + "'")

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
        erro_sintatico("era esperado um identificador mas encontrou '" + str(token_atual()) + "'")

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
        erro_sintatico("era esperado 'if', 'while', 'positivo' ou um identificador mas encontrou '" + str(token_atual()) + "'")

# <comandos> -> <comando> { <comando> }
def regra_comandos():
    regra_comando()
    while tipo_token_atual() in ["ID", "RESERVADA"]:
        regra_comando()

#Função principal
def analisar(codigo, correto):
    global pos
    global tokens
    global tabela_simbolos
    global executar
    codigo_atual = codigo
    executar = True
    print("=" * 60)
    print(codigo)
    pos = 0
    tabela_simbolos = {} #Reinicia a tabela de símbolos
    ok = True
    try:
        tokens = tokenizar(codigo)
        regra_comandos() #chamando a regra inicial da gramática
        if pos < len(tokens):
            erro_sintatico("'" + token_atual() + "' não era esperado.")
        else:
            print("A sintaxe está correta.")
            print(tabela_simbolos)
    except ErroLexico as erro:
        print("Erro Léxico:", erro)
        ok = False
    except SystemExit:
        ok = False #só entra aqui se houve erro sintático ou semântico identificado pelas nossas funções de erro.

    print("[OK]" if ok == correto else "[PROBLEMA]")

analisar("a = 1 ; b = 2 ; z = a @ b ;", True)  # z=2
analisar("z = 1 @  ;", False)  # "Erro sintático! Esperava INT ou o indentificador, mas encontrou ";""
analisar("z = 1 @ 2 @ 3 ;", True) # z = 3
analisar("z = ( 1 @ 2 ) + ( 3 @ 4 ) ;", True)
analisar("z = 1 @ 2 + 3 @ 4 ;", True) #z = 5
analisar("a = 3 ; b = 4 ; z = hip ( a , b ) ;", True) # z = 5.0
analisar("a = 3 ; b = 4 ; z = hip ( a , b ) @ 2 * 3 ;", True) # z = 6
analisar("z = hip ( 3 , 4 ) ;", False) # só aceita identificador
analisar("a = 3 ; z = hip ( a , c ) ;", False) # c não declarado
analisar("a = 0 ; if ( a ) { z = hip ( a , c ) ; }", True) # não executa: c não é buscado
analisar('z = "Digite o valor:" ;', True) # usuário digita 7 -> z = 7
analisar('z = "Primeiro:" + "Segundo:" ;', True) # lê dois números e soma
analisar('z = "Decimal:" * 2 ;', True) # usuário digita 1,5 -> z = 3.0
analisar('z = "Digite:" ;', False) # usuário digita abc -> erro semântico
analisar('a = 0 ; if ( a ) { z = "não pergunta" ; }', True) # bloco pulado: não lê nada
analisar("a = 5 ; positivo ( a ) { z = 1 ; } negativo { z = 2 ; } zero { z = 3 ; }", True) # z = 1
analisar("a = 0 - 5 ; positivo ( a ) { z = 1 ; } negativo { z = 2 ; } zero { z = 3 ; }", True) # z = 2
analisar("a = 0 ; positivo ( a ) { z = 1 ; } negativo { z = 2 ; } zero { z = 3 ; }", True) # z = 3
analisar("a = 1 ; positivo ( a - 3 ) { z = 1 ; } negativo { } zero { z = 3 ; }", True) # negativo vazio: nada executa
analisar("positivo ( 1 ) { } negativo { } zero { }", True) # todos os blocos vazios
analisar("a = 2 ; b = 3 ; positivo ( a + b ) { z = 1 ; } negativo { z = 2 ; } zero { z = 3 ; }", True) # z = 1
analisar("a = 2 ; b = 3 ; positivo ( a - b * 2 ) { z = 1 ; } negativo { z = 2 ; } zero { z = 3 ; }", True) # z = 2
analisar("a = 2 ; b = 2 ; positivo ( ( a - b ) * 5 ) { z = 1 ; } negativo { z = 2 ; } zero { z = 3 ; }", True) # z = 3
analisar("a = 0 - 2 ; b = 0 - 3 ; positivo ( a @ b ) { z = 1 ; } negativo { z = 2 ; } zero { }", True) # z = 2
analisar("a = 2 ; b = 3 ; positivo ( a < b ) { z = 1 ; } negativo { } zero { }", False) # comparação (booleano) não é permitida
analisar("a = 2 ; b = 3 ; positivo ( a + 1 == b ) { z = 1 ; } negativo { } zero { }", False) # comparação (booleano) não é permitida
analisar("a = 1 ; positivo ( a ) { z = 1 ; } negativo { z = hip ( a , c ) ; } zero { }", True) # bloco pulado: c não é buscado
analisar("a = 1 ; if ( 0 ) { positivo ( a ) { z = 1 ; } negativo { } zero { } }", True) # dentro de bloco pulado: nada executa
analisar("a = 1 ; positivo ( a ) { z = 1 ; } zero { z = 3 ; } negativo { z = 2 ; }", False) # ordem errada
analisar("a = 1 ; positivo ( a ) { z = 1 ; }", False) # faltam negativo e zero
analisar("a = 1 ; positivo ( a ) { z = 1 ; } negativo { z = 2 ; }", False) # falta zero
analisar("a = 1 ; positivo ( a ) { z = 1 ; } zero { z = 3 ; }", False) # falta negativo
analisar("negativo { z = 2 ; }", False) # negativo sem positivo
analisar('x = 5 ; positivo ( x ) { z = 1 ; } negativo { z = 2 ; } zero { z = 3 ; }', True) # z = 1
analisar('x = 5.67 ;', True)