"""
============================================================
MÓDULO: dominio/ativo.py
============================================================
Responsabilidade:
    - Definir a classe base abstrata Ativo e suas subclasses.
    - Requisito 1 do Trabalho 2: Orientação a Objetos com
      herança, polimorfismo e abstração.

Hierarquia:
    Ativo (ABC)
    ├── Notebook
    ├── Servidor
    └── Roteador

Cada subclasse sobrescreve:
    - fator_exposicao(): pondera o risco próprio do equipamento.
    - to_dict(): serializa para JSON incluindo o campo 'tipo'.
============================================================
"""

from abc import ABC, abstractmethod


class Ativo(ABC):
    """
    Classe base abstrata que representa um ativo de TI.

    Atributos comuns:
        id (int): identificador único.
        nome (str): hostname ou nome do ativo.
        responsavel (str): pessoa responsável.
        setor (str): setor da organização.
        localizacao (str): local físico/lógico.
    """

    def __init__(self, id: int, nome: str, responsavel: str,
                 setor: str, localizacao: str):
        self.id = id
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor
        self.localizacao = localizacao

    @abstractmethod
    def fator_exposicao(self) -> float:
        """
        Fator de exposição do ativo (0 < f <= 1).

        Dica do enunciado: 'cada tipo de equipamento pode definir
        um fator de exposição que pondera o seu risco próprio'.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Serializa o objeto para JSON (inclui campo 'tipo')."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, nome={self.nome!r})"


class Notebook(Ativo):
    """Ativo do tipo Notebook. Exposição moderada (circula fora da empresa)."""

    def fator_exposicao(self) -> float:
        return 0.7

    def to_dict(self) -> dict:
        return {
            "tipo": "Notebook",
            "id": self.id,
            "nome": self.nome,
            "responsavel": self.responsavel,
            "setor": self.setor,
            "localizacao": self.localizacao,
        }


class Servidor(Ativo):
    """Ativo do tipo Servidor. Alta exposição (serviços públicos)."""

    def fator_exposicao(self) -> float:
        return 1.0

    def to_dict(self) -> dict:
        return {
            "tipo": "Servidor",
            "id": self.id,
            "nome": self.nome,
            "responsavel": self.responsavel,
            "setor": self.setor,
            "localizacao": self.localizacao,
        }


class Roteador(Ativo):
    """Ativo do tipo Roteador. Exposição controlada."""

    def fator_exposicao(self) -> float:
        return 0.5

    def to_dict(self) -> dict:
        return {
            "tipo": "Roteador",
            "id": self.id,
            "nome": self.nome,
            "responsavel": self.responsavel,
            "setor": self.setor,
            "localizacao": self.localizacao,
        }


# Mapa auxiliar usado pela fábrica (persistência → subclasse).
MAPA_TIPOS = {
    "Notebook": Notebook,
    "Servidor": Servidor,
    "Roteador": Roteador,
}


def ativo_from_dict(dados: dict) -> Ativo:
    """
    Fábrica: reconstrói a subclasse correta a partir do JSON.

    Usa o campo 'tipo' para escolher a classe. Se o tipo não existir,
    lança erro explícito (validação).
    """
    tipo = dados.get("tipo")
    if tipo not in MAPA_TIPOS:
        raise ValueError(f"Tipo de ativo desconhecido: {tipo!r}")

    dados_sem_tipo = {k: v for k, v in dados.items() if k != "tipo"}
    return MAPA_TIPOS[tipo](**dados_sem_tipo)