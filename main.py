"""
============================================================
MÓDULO: main.py
============================================================
Ponto de entrada do Trabalho 2.

Modos:
    --relatorio  → imprime o relatório de risco (não interativo,
                   adequado ao health check do Docker).
    (padrão)     → menu interativo.
============================================================
"""

import sys
from persistencia.repositorio_json import RepositorioJSON
from servico.servico_inventario import ServicoInventario


def modo_relatorio():
    """Modo não interativo (usado pelo health check do Docker)."""
    repo = RepositorioJSON("dados")
    serv = ServicoInventario(repo)
    print(serv.gerar_relatorio_risco())


def modo_interativo():
    repo = RepositorioJSON("dados")
    serv = ServicoInventario(repo)

    while True:
        print("\n" + "=" * 50)
        print("  INVENTÁRIO DE ATIVOS E VULNERABILIDADES (OO)")
        print("=" * 50)
        print("  [1] Cadastrar ativo")
        print("  [2] Listar ativos")
        print("  [3] Cadastrar vulnerabilidade")
        print("  [4] Cadastrar dependência")
        print("  [5] Calcular risco")
        print("  [0] Sair")
        print("=" * 50)

        try:
            op = int(input("  Opção: ").strip())
        except ValueError:
            print("  [!] Entrada inválida.")
            continue

        if op == 1:
            tipo = input("  Tipo (Notebook/Servidor/Roteador): ").strip()
            nome = input("  Nome: ").strip()
            resp = input("  Responsável: ").strip()
            setor = input("  Setor: ").strip()
            loc = input("  Localização: ").strip()
            try:
                a = serv.cadastrar_ativo(tipo, nome, resp, setor, loc)
                print(f"  [OK] Ativo {a} cadastrado.")
            except ValueError as e:
                print(f"  [!] {e}")

        elif op == 2:
            for a in serv.ativos:
                print(f"  {a}  f={a.fator_exposicao():.2f}")

        elif op == 3:
            cve = input("  CVE (ex.: CVE-2024-0001): ").strip()
            desc = input("  Descrição: ").strip()
            try:
                sev = float(input("  Severidade (0-10): ").strip())
            except ValueError:
                print("  [!] Severidade inválida.")
                continue
            ids_raw = input("  IDs de ativos afetados (vírgula): ").strip()
            try:
                ids = [int(x) for x in ids_raw.split(",") if x.strip()]
            except ValueError:
                print("  [!] IDs inválidos.")
                continue
            try:
                v = serv.cadastrar_vulnerabilidade(cve, desc, sev, ids)
                print(f"  [OK] Vulnerabilidade #{v.id} cadastrada.")
            except ValueError as e:
                print(f"  [!] {e}")

        elif op == 4:
            try:
                origem = int(input("  ID origem (j): ").strip())
                destino = int(input("  ID destino (i): ").strip())
                peso = float(input("  Peso (0-1): ").strip())
                d = serv.cadastrar_dependencia(origem, destino, peso)
                print(f"  [OK] {d}")
            except ValueError as e:
                print(f"  [!] {e}")

        elif op == 5:
            try:
                print(serv.gerar_relatorio_risco())
            except ValueError as e:
                print(f"  [!] {e}")

        elif op == 0:
            print("  Encerrando.")
            break


if __name__ == "__main__":
    if "--relatorio" in sys.argv:
        modo_relatorio()
    else:
        modo_interativo()