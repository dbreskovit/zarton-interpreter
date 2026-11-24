from typing import NamedTuple


KEYWORDS = ["if", "else", "while", "hip", "positivo", "negativo", "zero"]


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
                raise ErroLexico(
                    "o símbolo '" + caractere + "' não foi identificado na posição " + str(pos)
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
                raise ErroLexico("número decimal inválido na posição " + str(inicio))
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
                raise ErroLexico("faltou fechar o comentário iniciado na posição " + str(inicio))
            else:
                pos += 1
        elif estado == 13:
            if entrada[pos] == '"':
                pos += 1
                estado = 14
            elif entrada[pos] == "\0":
                raise ErroLexico("string sem fechamento na posição " + str(inicio))
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
                raise ErroLexico("char sem fechamento na posição " + str(inicio))
            else:
                estado = 16
                pos += 1
        elif estado == 16:
            if entrada[pos] == "'":
                pos += 1
                estado = 19
            elif entrada[pos] == "\0":
                raise ErroLexico("char sem fechamento na posição " + str(inicio))
            else:
                estado = 18
                pos += 1
        elif estado == 18:
            if entrada[pos] == "'":
                pos += 1
                estado = 20
            elif entrada[pos] == "\0":
                raise ErroLexico("char sem fechamento na posição " + str(inicio))
            else:
                pos += 1
        elif estado == 19:
            emitir("CHAR")
            estado = 0
        elif estado == 17:
            raise ErroLexico("char vazio iniciado na posição " + str(inicio))
        elif estado == 20:
            raise ErroLexico("char iniciado na posição " + str(inicio) + " deveria ter no máximo 1 símbolo")

    return tokens