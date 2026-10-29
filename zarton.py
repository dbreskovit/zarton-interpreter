
pos = 0 #Indica qual token está sendo lido
KEYWORDS = ['if', 'else', 'while', 'hip'] #Palavras reservadas: não podem ser identificadores
tabela_simbolos = {} #tabela de símbolos
executar = True #Se falso analisa somente a sintaxe sem executar. 

# {  
#   "x": {"tipo": "INT", "valor": 5},
#   "y": {"tipo": "FLOAT", "valor": 0.1}
# }
#
# tabela_simbolos["x"] = {"tipo": "INT", "valor": 5} 
# y = tabela_simbolos["y"] 

# ==================================== interpretador ==

def erro_semantico(msg):
    print("Erro Semântico:", msg)
    exit(1) #Esse erro será capturado na função analisar.

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

    #computa o valor das operações + - *
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

        

    #Infere o tipo do retorno de + - *
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
        return tokens[pos]
    else:
        return None

#Função de relatório de erro sintático
def erro_sintatico(msg):
    print("Contexto: " + ' '.join(tokens[0:pos])) #Imprime o que deu certo
    print("Erro Sintático:", msg)
    exit(1) #Esse exit será capturado na função analisar

#avalia se o token é igual ao token esperado
#se for avança para o proximo token, senão causa um erro.
def consumir(token_esperado):
    global pos
    if token_atual() == token_esperado:
        pos = pos + 1 #avança para o proximo token
    else:
        erro_sintatico("era esperado '" + token_esperado + "' mas encontrou '" + str(token_atual()) + "'")

# <fator> -> (<expc>) | _int_ | _id_
# (7 + 6)
# Retorna (tipo, valor) 
def regra_fator():
    if token_atual() == "(":
        consumir("(")
        temp = regra_expc() #("INT", 11)  
        consumir(")")
        return temp #retorno depois do consumo
    elif token_atual()!=None and token_atual().isdigit():
        numero = int(token_atual()) # capturar antes do consumo
        consumir(token_atual())
        return ("INT", numero) # retornar depois do consumo
    elif token_atual()!=None and token_atual().isalpha() and token_atual() not in KEYWORDS:
        identificador = token_atual() # capturar antes do consumo
        consumir(token_atual())
        (tipo, valor) = buscar_identificador(identificador)
        return (tipo, valor)  
    else:
        erro_sintatico("era esperado '(', um número ou um identificador mas encontrou '" + str(token_atual()) + "'")

# <termo> -> <fator> { <mult> <fator> }
# a = 2 * 3 * 4
def regra_termo():
    esquerda = regra_fator() # ("INT", 2) 
    while token_atual() in ['*','/']:
        op = token_atual() #Guarda o operador antes de consumir 
        consumir(token_atual())
        direita = regra_fator() #("INT, 3) 
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
    if token_atual() in ['<','==','>','@']:
        op = token_atual() 
        consumir(token_atual()) # < 
        direita = regra_exp() # ("INT", 4)
        esquerda = executar_operacao(esquerda, op, direita) # ("INT", 1)  
    return esquerda

# <atrib> -> _id_ = <expc> ;
# a = 1 + 1 ;
def regra_atrib():
    if token_atual()!=None and token_atual().isalpha() and token_atual() not in KEYWORDS:
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

# def regra_hip():
#     global pos

# <comando> -> <if> | <while> | <atrib>
def regra_comando():
    if token_atual() == "if":
        regra_if()
    elif token_atual() == "while":
        regra_while()
    elif token_atual()!=None and token_atual().isalpha() and token_atual() not in KEYWORDS:
        regra_atrib()
    else:
        erro_sintatico("era esperado 'if', 'while' ou um identificador mas encontrou '" + str(token_atual()) + "'")

# <comandos> -> <comando> { <comando> }
def regra_comandos():
    regra_comando()
    while token_atual() != None and token_atual().isalpha():
        regra_comando()

#Função principal
def analisar(codigo, correto):
    global pos
    global tokens
    global tabela_simbolos
    global executar
    executar = True 
    print("=" * 60)
    print(codigo)
    pos = 0
    tabela_simbolos = {} #Reinicia a tabela de símbolos
    tokens = codigo.split(" ")
    ok = True
    try:
        regra_comandos() #chamando a regra inicial da gramática
        if pos < len(tokens):
            erro_sintatico("'" + token_atual() + "' não era esperado.")
        else:
            print("A sintaxe está correta.")
            print(tabela_simbolos)
    except SystemExit:
        ok = False #só entra aqui se houve erro sintático ou semântico identificado pelas nossas funções de erro.

    print("[OK]" if ok == correto else "[PROBLEMA]")

analisar("a = 1 ; b = 2 ; z = a @ b ;", True)  # z=2
analisar("z = 1 @  ;", False)  # "Erro sintático! Esperava INT ou o indentificador, mas encontrou ";"" 
analisar("z = 1 @ 2 @ 3 ;", True) # z = 3
analisar("z = ( 1 @ 2 ) + ( 3 @ 4 ) ;", True)
analisar("z = 1 @ 2 + 3 @ 4 ;", True) #z = 5
