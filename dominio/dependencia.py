"""
============================================================
MÓDULO: dominio/dependencia.py
============================================================
Representa uma dependência entre dois equipamentos.

Interpretação (enunciado, Seção 2):
    A_ij ∈ [0, 1) é a FRAÇÃO do risco do equipamento j
    transmitida ao equipamento i.

    Se A_ij = 0.3, então 30% do risco de j 'contamina' i.

Regras impostas:
    • A_ii = 0  →  um equipamento não depende de si mesmo.
    • Peso ∈ [0, 1).
    • Soma de cada linha de A deve ser < 1 (dominância diagonal
      estrita), garantindo I − A invertível.
============================================================
"""


class Dependencia:
    """
    Dependência direcionada: destino HERDA risco de origem.

    Atributos:
        origem (int):  ID do equipamento de onde o risco vem (j).
        destino (int): ID do equipamento que herda o risco (i).
        peso (float):  fração do risco transmitida (A_ij).
    """

    def __init__(self, origem: int, destino: int, peso: float):
        if origem == destino:
            raise ValueError(
                "Um equipamento não pode depender de si mesmo (A_ii = 0)."
            )
        if not (0.0 <= peso < 1.0):
            raise ValueError(f"Peso deve estar em [0, 1). Recebido: {peso}.")
        self.origem = origem
        self.destino = destino
        self.peso = peso

    def to_dict(self) -> dict:
        return {
            "origem": self.origem,
            "destino": self.destino,
            "peso": self.peso,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Dependencia":
        return cls(
            origem=dados["origem"],
            destino=dados["destino"],
            peso=dados["peso"],
        )

    def __repr__(self):
        return f"Dependencia({self.origem} → {self.destino}, peso={self.peso})"