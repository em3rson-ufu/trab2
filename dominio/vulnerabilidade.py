"""
============================================================
MÓDULO: dominio/vulnerabilidade.py
============================================================
Representa uma vulnerabilidade associada a um ou mais ativos.

O relacionamento N:N (ativo ↔ vulnerabilidade) é representado
pela Matriz de Incidência M no modelo de risco (ver risco.py).

Atributos:
    id (int)
    cve (str)                - identificador CVE
    descricao (str)
    severidade (float)       - nota CVSS (0.0 a 10.0)
    ativos_afetados (list)   - IDs dos ativos que ela afeta
============================================================
"""


class Vulnerabilidade:
    def __init__(self, id: int, cve: str, descricao: str,
                 severidade: float, ativos_afetados: list = None):
        # Valida a faixa do CVSS.
        if not (0.0 <= severidade <= 10.0):
            raise ValueError("Severidade (CVSS) deve estar em [0, 10].")

        self.id = id
        self.cve = cve
        self.descricao = descricao
        self.severidade = severidade
        self.ativos_afetados = list(ativos_afetados) if ativos_afetados else []

    def to_dict(self) -> dict:
        """Serializa para JSON."""
        return {
            "id": self.id,
            "cve": self.cve,
            "descricao": self.descricao,
            "severidade": self.severidade,
            "ativos_afetados": self.ativos_afetados,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Vulnerabilidade":
        """Reconstrói a partir do JSON."""
        return cls(
            id=dados["id"],
            cve=dados["cve"],
            descricao=dados["descricao"],
            severidade=dados["severidade"],
            ativos_afetados=dados.get("ativos_afetados", []),
        )

    def __repr__(self):
        return f"Vulnerabilidade(id={self.id}, cve={self.cve!r}, cvss={self.severidade})"