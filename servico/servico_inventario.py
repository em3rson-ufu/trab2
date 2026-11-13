"""
============================================================
MÓDULO: servicos/servico_inventario.py
============================================================
Camada de serviço: orquestra operações do domínio e da
persistência. O main.py não precisa conhecer detalhes de
JSON nem de álgebra linear.
============================================================
"""

from dominio.ativo import MAPA_TIPOS
from dominio.dependencia import Dependencia
from dominio.risco import ModeloRisco
from dominio.vulnerabilidade import Vulnerabilidade
from persistencia.repositorio_json import RepositorioJSON


class ServicoInventario:
    def __init__(self, repositorio: RepositorioJSON):
        self.repo = repositorio
        self.ativos = self.repo.carregar_ativos()
        self.vulnerabilidades = self.repo.carregar_vulnerabilidades()
        self.dependencias = self.repo.carregar_dependencias()

    # ---------- ativos ----------
    def _proximo_id_ativo(self) -> int:
        return max((a.id for a in self.ativos), default=0) + 1

    def cadastrar_ativo(self, tipo: str, nome: str, responsavel: str,
                        setor: str, localizacao: str):
        if tipo not in MAPA_TIPOS:
            raise ValueError(f"Tipo inválido: {tipo}")
        cls = MAPA_TIPOS[tipo]
        novo = cls(
            id=self._proximo_id_ativo(),
            nome=nome,
            responsavel=responsavel,
            setor=setor,
            localizacao=localizacao,
        )
        self.ativos.append(novo)
        self.repo.salvar_ativos(self.ativos)
        return novo

    def buscar_ativo(self, id_ativo: int):
        return next((a for a in self.ativos if a.id == id_ativo), None)

    # ---------- vulnerabilidades ----------
    def _proximo_id_vuln(self) -> int:
        return max((v.id for v in self.vulnerabilidades), default=0) + 1

    def cadastrar_vulnerabilidade(self, cve: str, descricao: str,
                                   severidade: float, ids_ativos: list):
        nova = Vulnerabilidade(
            id=self._proximo_id_vuln(),
            cve=cve,
            descricao=descricao,
            severidade=severidade,
            ativos_afetados=list(ids_ativos),
        )
        self.vulnerabilidades.append(nova)
        self.repo.salvar_vulnerabilidades(self.vulnerabilidades)
        return nova

    # ---------- dependências ----------
    def cadastrar_dependencia(self, origem: int, destino: int, peso: float):
        dep = Dependencia(origem=origem, destino=destino, peso=peso)

        soma_atual = sum(d.peso for d in self.dependencias
                         if d.destino == destino and d.origem != origem)
        if soma_atual + peso >= 1.0:
            raise ValueError(
                f"Soma das dependências do ativo {destino} ficaria "
                f"em {soma_atual + peso:.2f} ≥ 1 (dominância diagonal)."
            )
        self.dependencias.append(dep)
        self.repo.salvar_dependencias(self.dependencias)
        return dep

    # ---------- risco ----------
    def gerar_relatorio_risco(self) -> str:
        modelo = ModeloRisco(self.ativos, self.vulnerabilidades,
                             self.dependencias)
        return modelo.relatorio()