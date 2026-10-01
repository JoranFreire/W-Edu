"""Catalogo de permissoes e o que cada papel de usuario ja concede por padrao.

Os papeis da pessoa na instituicao (ela pode acumular varios) viram perfis padrao: cada um concede o conjunto
abaixo, igual ao comportamento anterior ao RBAC. Perfis personalizados da instituicao somam
permissoes a qualquer usuario. Plataforma (super admin) e portal do responsavel ficam fora do
catalogo: dependem da identidade, nao de permissao concedida.
"""

from dataclasses import dataclass

from app.models.student import ADMIN_ROLES, UserRole


@dataclass(frozen=True)
class Permission:
    key: str
    module: str
    label: str
    description: str


CATALOG: tuple[Permission, ...] = (
    Permission("institution.manage", "Instituição", "Administrar a instituição",
               "Configurações, usuários, exclusões, financeiro geral e demais ações administrativas."),
    Permission("access.manage", "Instituição", "Gerenciar perfis de acesso",
               "Criar perfis, escolher permissões e atribuí-los a usuários (só concede o que já possui)."),
    Permission("academic.manage", "Acadêmico", "Gerir estrutura acadêmica e cursos",
               "Programas, disciplinas, matrizes, turmas, encontros, certificados, comunicação e financiadores."),
    Permission("teaching.access", "Acadêmico", "Diário de classe e orientações",
               "Notas, chamada, resultados, estágio e TCC (o instrutor só nas turmas e orientações que são suas)."),
    Permission("secretariat.access", "Secretaria", "Secretaria acadêmica",
               "Matrículas, ficha do aluno, documentos, editais, contratos, janelas de matrícula e programas sociais."),
    Permission("school_life.access", "Secretaria", "Vida escolar e benefícios",
               "Ocorrências, agenda da turma, frequência e entrega de benefícios."),
    Permission("benefits.redeem", "Secretaria", "Validar benefícios (QR)",
               "Ler o QR do benefício liberado ao aluno e confirmar a retirada (ex.: cantina, entrega de kits)."),
    Permission("finance.access", "Financeiro", "Financeiro educacional",
               "Bolsas, descontos, extratos da matrícula e multa e juros."),
    Permission("warehouse.request", "Almoxarifado", "Requisitar materiais",
               "Pedir materiais do almoxarifado para aulas e atividades."),
    Permission("warehouse.manage", "Almoxarifado", "Operar o almoxarifado",
               "Cadastrar materiais, lançar entradas, aprovar requisições, registrar retiradas e devoluções."),
    Permission("warehouse.reports", "Almoxarifado", "Relatórios do almoxarifado",
               "Consumo por turma, professor e material; estoque baixo e empréstimos em atraso."),
)

KEYS = frozenset(permission.key for permission in CATALOG)

_COORDINATION = ADMIN_ROLES | {UserRole.coordinator}

# Papel -> permissoes que ele ja concede (mesmos conjuntos dos guards anteriores ao RBAC).
DEFAULT_GRANTS: dict[str, frozenset[UserRole]] = {
    "institution.manage": ADMIN_ROLES,
    "access.manage": ADMIN_ROLES,
    "academic.manage": _COORDINATION,
    "teaching.access": _COORDINATION | {UserRole.instructor},
    "secretariat.access": _COORDINATION | {UserRole.secretary},
    "school_life.access": _COORDINATION | {UserRole.instructor, UserRole.secretary},
    "benefits.redeem": _COORDINATION | {UserRole.instructor, UserRole.secretary},
    "finance.access": ADMIN_ROLES | {UserRole.secretary},
    "warehouse.request": _COORDINATION | {UserRole.instructor},
    "warehouse.manage": ADMIN_ROLES,
    "warehouse.reports": _COORDINATION,
}


def role_permissions(role: UserRole) -> frozenset[str]:
    return frozenset(key for key, roles in DEFAULT_GRANTS.items() if role in roles)
