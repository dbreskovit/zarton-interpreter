#!/usr/bin/env bash
# Lista os exemplos e roda o escolhido no interpretador.
# Uso: ./exemplos.sh   (ou: bash exemplos.sh)
cd "$(dirname "$0")"
for PY in python3 python; do "$PY" -c "" 2>/dev/null && break; done

PS3=$'\nNúmero do exemplo (Ctrl+C sai): '
select arquivo in exemplos/*/*.zt; do
    [ -z "$arquivo" ] && { echo "Opção inválida."; continue; }
    echo "==================== $arquivo"
    cat "$arquivo"
    echo "-------------------- saída"
    "$PY" zarton.py "$arquivo"
    echo
done
