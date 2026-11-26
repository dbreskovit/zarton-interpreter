import zarton


def analisar(codigo, correto):
    print("=" * 60)
    print(codigo)
    ok = True
    try:
        zarton.rodar(codigo)
    except SystemExit:
        ok = False
    print("[OK]" if ok == correto else "[PROBLEMA]")


analisar("x = 2,5 ; z = x * 2 ;", True) # z = 5.0
analisar("a = 1 ;\nb = 2\nz = 3 ;", False) # erro sintático na linha 3
analisar("a = 1 ;\n\nz = y ;", False) # erro semântico na linha 3
analisar("a = 1 ;\nb = $ ;", False) # erro léxico na linha 2
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