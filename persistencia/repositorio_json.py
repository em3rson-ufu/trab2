"""
============================================================
MÓDULO: persistencia/repositorio_json.py
============================================================
REQUISITO 2: cada ativo/vulnerabilidade em arquivo JSON,
no formato de ARRAY de objetos.

Também aplica o padrão Repository (isola acesso a dados).
Escrita atômica via tempfile + os.replace (evita corromper
o arquivo em caso de falha).
============================================================
"""

import json
import os
import tempfile

from dominio.ativo import ativo_from_dict
from dominio.dependencia import Dependencia
from dominio.vulnerabilidade import Vulnerabilidade


class RepositorioJSON:
    def __init__(self, pasta: str = "dados"):
        self.pasta = pasta
        os.makedirs(pasta, exist_ok=True)

    def _caminho(self, nome: str) -> str:
        return os.path.join(self.pasta, f"{nome}.json")

    def _salvar_lista(self, nome: str, lista: list):
        """Grava um array de objetos JSON com escrita atômica."""
        caminho = self._caminho(nome)
        fd, tmp = tempfile.mkstemp(dir=self.pasta, suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=2)
            os.replace(tmp, caminho)
        except Exception:
            os.unlink(tmp)
            raise

    def _carregar_lista(self, nome: str) -> list:
        caminho = self._caminho(nome)
        if not os.path.exists(caminho):
            return []
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            raise ValueError(
                f"{caminho}: esperado array JSON, "
                f"encontrado {type(dados).__name__}."
            )
        return dados

    # ---------- ativos ----------
    def carregar_ativos(self) -> list:
        return [ativo_from_dict(d) for d in self._carregar_lista("ativos")]

    def salvar_ativos(self, ativos: list):
        self._salvar_lista("ativos", [a.to_dict() for a in ativos])

    # ---------- vulnerabilidades ----------
    def carregar_vulnerabilidades(self) -> list:
        return [Vulnerabilidade.from_dict(d)
                for d in self._carregar_lista("vulnerabilidades")]

    def salvar_vulnerabilidades(self, vulns: list):
        self._salvar_lista("vulnerabilidades", [v.to_dict() for v in vulns])

    # ---------- dependências ----------
    def carregar_dependencias(self) -> list:
        return [Dependencia.from_dict(d)
                for d in self._carregar_lista("dependencias")]

    def salvar_dependencias(self, deps: list):
        self._salvar_lista("dependencias", [d.to_dict() for d in deps])