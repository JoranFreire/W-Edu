"""Row Level Security no PostgreSQL: segunda barreira do isolamento por instituicao.

Cada tabela com ``TenantMixin`` recebe a politica ``tenant_isolation``, que so
deixa ler e gravar linhas de ``current_setting('app.institution_id')``. A
configuracao vale para a transacao e e definida quando a sessao vincula uma
instituicao (``bind_institution``) e no inicio de cada nova transacao.

Sem instituicao vinculada (worker, webhooks, rotas publicas) a configuracao
fica vazia e a politica libera tudo, como o filtro do ORM. Consultas
``UNSCOPED`` tambem passam pela politica. Superusuarios do PostgreSQL ignoram RLS:
a aplicacao deve conectar com um usuario comum (o dono das tabelas e coberto por
``FORCE ROW LEVEL SECURITY``).
"""

from sqlalchemy import Table, event, text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import ORMExecuteState, Session

from app.core.tenancy import SKIP_TENANT_FILTER, TenantMixin, bound_institution_id, on_bind

SETTING = "app.institution_id"
POLICY = "tenant_isolation"
_CURRENT = f"nullif(current_setting('{SETTING}', true), '')"
_CONDITION = f"{_CURRENT} IS NULL OR institution_id = {_CURRENT}::int"
_SET = text("SELECT set_config(:name, :value, true)")


def policy_statements(table: str) -> list[str]:
    return [
        f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY",
        f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY",
        f"DROP POLICY IF EXISTS {POLICY} ON {table}",
        f"CREATE POLICY {POLICY} ON {table} USING ({_CONDITION}) WITH CHECK ({_CONDITION})",
    ]


def drop_policy_statements(table: str) -> list[str]:
    return [
        f"DROP POLICY IF EXISTS {POLICY} ON {table}",
        f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY",
        f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY",
    ]


def _is_postgres(connection: Connection) -> bool:
    return connection.dialect.name == "postgresql"


def _set_setting(connection: Connection, institution_id: int | None) -> None:
    connection.execute(_SET, {"name": SETTING, "value": "" if institution_id is None else str(institution_id)})


@on_bind
def _apply_on_bind(session: Session, institution_id: int | None) -> None:
    # A transacao ja aberta (ex.: consulta do usuario autenticado) precisa da configuracao agora.
    if session.in_transaction():
        connection = session.connection()
        if _is_postgres(connection):
            _set_setting(connection, institution_id)


@event.listens_for(Session, "after_begin")
def _apply_on_begin(session: Session, transaction, connection: Connection) -> None:
    institution_id = bound_institution_id(session)
    if institution_id is not None and _is_postgres(connection):
        _set_setting(connection, institution_id)


@event.listens_for(Session, "do_orm_execute")
def _bypass_for_unscoped(state: ORMExecuteState):
    """Consulta global deliberada (UNSCOPED): suspende a politica so durante a instrucao."""
    institution_id = bound_institution_id(state.session)
    if institution_id is None or not state.execution_options.get(SKIP_TENANT_FILTER):
        return None
    connection = state.session.connection()
    if not _is_postgres(connection):
        return None
    _set_setting(connection, None)
    try:
        return state.invoke_statement()
    finally:
        _set_setting(connection, institution_id)


def install_create_hooks(tables: list[Table]) -> None:
    """Cria as politicas junto com as tabelas no `metadata.create_all` (usado pelos scripts de teste)."""
    for table in tables:
        event.listen(table, "after_create", _create_policies)


def _create_policies(target: Table, connection: Connection, **_kw) -> None:
    if _is_postgres(connection):
        for statement in policy_statements(target.name):
            connection.exec_driver_sql(statement)


def tenant_tables(base) -> list[Table]:
    return [mapper.class_.__table__ for mapper in base.registry.mappers if issubclass(mapper.class_, TenantMixin)]
