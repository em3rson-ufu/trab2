"""
============================================================
MÓDULO: dominio/risco.py
============================================================
REQUISITO 4 do Trabalho 2:
    Modelo de análise de risco baseado em álgebra linear.

Modelo:
    M ∈ {0,1}^(n×m)  matriz de incidência
    v ∈ R^m          vetor de severidade (CVSS)
    b = M v          risco próprio
    A ∈ R^(n×n)      matriz de dependências (A_ii = 0)
    x = b + A x  ⟺  (I − A) x = b   → risco efetivo

Decisões numéricas (dicas do enunciado):
    • Tolerância 1e-12 para considerar det(I − A) como zero.
    • Dominância diagonal estrita imposta no cadastro de A.
    • np.linalg.solve em vez de inv @ b (mais preciso).
    • np.linalg.cond reportado ao usuário.
============================================================
"""

import numpy as np

TOL_DET = 1e-12


class ModeloRisco:
    """
    Encapsula o modelo linear (I − A) x = b.
    """

    def __init__(self, ativos: list, vulnerabilidades: list,
                 dependencias: list = None):
        self.ativos = ativos
        self.vulnerabilidades = vulnerabilidades
        self.dependencias = dependencias or []

        self.idx_ativo = {a.id: i for i, a in enumerate(ativos)}
        self.idx_vuln = {v.id: j for j, v in enumerate(vulnerabilidades)}

        self.M = self._montar_matriz_incidencia()
        self.v = self._montar_vetor_severidade()
        self.A = self._montar_matriz_dependencias()
        self.b = self.M @ self.v

    def _montar_matriz_incidencia(self) -> np.ndarray:
        """M[i, j] = 1 se ativo i é afetado pela vulnerabilidade j."""
        n, m = len(self.ativos), len(self.vulnerabilidades)
        M = np.zeros((n, m), dtype=float)
        for j, vuln in enumerate(self.vulnerabilidades):
            for id_ativo in vuln.ativos_afetados:
                if id_ativo in self.idx_ativo:
                    M[self.idx_ativo[id_ativo], j] = 1.0
        return M

    def _montar_vetor_severidade(self) -> np.ndarray:
        """v[j] = severidade (CVSS) da vulnerabilidade j."""
        return np.array([v.severidade for v in self.vulnerabilidades], dtype=float)

    def _montar_matriz_dependencias(self) -> np.ndarray:
        """A[i, j] = fração do risco de j transmitida a i."""
        n = len(self.ativos)
        A = np.zeros((n, n), dtype=float)

        for dep in self.dependencias:
            if dep.origem not in self.idx_ativo:
                raise ValueError(
                    f"Dependência referencia origem inexistente: {dep.origem}."
                )
            if dep.destino not in self.idx_ativo:
                raise ValueError(
                    f"Dependência referencia destino inexistente: {dep.destino}."
                )
            i = self.idx_ativo[dep.destino]
            j = self.idx_ativo[dep.origem]
            A[i, j] += dep.peso

        np.fill_diagonal(A, 0.0)

        somas = A.sum(axis=1)
        if np.any(somas >= 1.0):
            linhas_invalidas = np.where(somas >= 1.0)[0].tolist()
            raise ValueError(
                f"Soma das linhas {linhas_invalidas} ≥ 1. "
                "I − A pode ser singular (dominância diagonal estrita)."
            )
        return A

    def verificar_invertibilidade(self) -> tuple:
        """Retorna (invertivel, det)."""
        n = len(self.ativos)
        B = np.eye(n) - self.A
        det = np.linalg.det(B)
        return (abs(det) >= TOL_DET, det)

    def calcular_risco_efetivo(self):
        """Resolve (I − A) x = b. Retorna (x, cond)."""
        n = len(self.ativos)
        B = np.eye(n) - self.A

        invertivel, det = self.verificar_invertibilidade()
        if not invertivel:
            raise ValueError(
                f"(I − A) é singular (det = {det:.3e}). "
                "Revise as dependências cadastradas."
            )

        x = np.linalg.solve(B, self.b)
        cond = np.linalg.cond(B)
        return x, cond

    def relatorio(self) -> str:
        """Gera relatório legível com risco próprio e efetivo."""
        linhas = ["=" * 66, "RELATÓRIO DE RISCO", "=" * 66]

        invertivel, det = self.verificar_invertibilidade()
        linhas.append(f"det(I − A) = {det:.6e}  →  "
                      f"{'invertível' if invertivel else 'SINGULAR'}")
        if not invertivel:
            linhas.append("Não é possível calcular o risco efetivo.")
            return "\n".join(linhas)

        x, cond = self.calcular_risco_efetivo()
        linhas.append(f"Número de condição: {cond:.4e}")
        linhas.append("-" * 66)
        linhas.append(f"{'Ativo':<18}{'Tipo':<11}{'f':>4}"
                      f"{'b':>10}{'b_pond':>11}{'x':>10}")
        linhas.append("-" * 66)

        for i, ativo in enumerate(self.ativos):
            fator = ativo.fator_exposicao()
            b_pond = self.b[i] * fator
            linhas.append(
                f"{ativo.nome:<18}{ativo.__class__.__name__:<11}{fator:>4.2f}"
                f"{self.b[i]:>10.3f}{b_pond:>11.3f}{x[i]:>10.3f}"
            )
        linhas.append("=" * 66)
        return "\n".join(linhas)