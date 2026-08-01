"""Testes de integracao contra um PostgreSQL real (nao SQLite).

Cobrem comportamentos especificos do PostgreSQL que os testes unitarios (SQLite em memoria)
nao conseguem validar: enums nativos, constraints de unicidade e chave estrangeira aplicadas
pelo banco, e o ciclo completo de migrations do Alembic.

Sao pulados automaticamente se a variavel de ambiente TEST_POSTGRES_URL nao estiver definida
ou se o banco nao estiver acessivel -- nao dependem do banco de desenvolvimento/producao.
"""
import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

TEST_POSTGRES_URL = os.environ.get(
    "TEST_POSTGRES_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/central_solicitacoes_test"
)


def _postgres_available() -> bool:
    try:
        engine = create_engine(TEST_POSTGRES_URL)
        with engine.connect():
            return True
    except OperationalError:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(), reason="PostgreSQL de teste indisponivel (defina TEST_POSTGRES_URL)"
)


@pytest.fixture(scope="module")
def pg_engine():
    import subprocess

    engine = create_engine(TEST_POSTGRES_URL)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))

    # app/alembic/env.py sempre le a URL de app.core.config.settings.DATABASE_URL (para que o
    # `alembic upgrade head` da CLI use as mesmas variaveis de ambiente da aplicacao), entao a
    # forma correta de apontar para o banco de teste e via variavel de ambiente, nao via
    # Config.set_main_option (que seria sobrescrito).
    env = os.environ.copy()
    env["DATABASE_URL"] = TEST_POSTGRES_URL
    result = subprocess.run(
        ["alembic", "upgrade", "head"], cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env, capture_output=True, text=True,
    )
    assert result.returncode == 0, f"alembic upgrade head falhou:\n{result.stdout}\n{result.stderr}"

    yield engine

    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))


@pytest.fixture()
def pg_session(pg_engine):
    Session = sessionmaker(bind=pg_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_migrations_criam_todas_as_tabelas(pg_engine):
    with pg_engine.connect() as conn:
        tables = conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        ).scalars().all()
    expected = {"users", "requests", "comments", "request_history", "attachments", "alembic_version"}
    assert expected.issubset(set(tables))


def test_migration_adiciona_preferencia_de_tema(pg_engine):
    with pg_engine.connect() as conn:
        column = conn.execute(
            text(
                "SELECT column_name, column_default, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='users' "
                "AND column_name='theme_preference'"
            )
        ).mappings().one()

    assert column["column_name"] == "theme_preference"
    assert "light" in (column["column_default"] or "")
    assert column["is_nullable"] == "NO"


def test_enum_history_action_inclui_exclusao(pg_engine):
    with pg_engine.connect() as conn:
        values = conn.execute(
            text(
                "SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid "
                "WHERE t.typname = 'history_action'"
            )
        ).scalars().all()
    assert "EXCLUSAO" in values
    assert "CRIACAO" in values


def test_constraint_email_unico_no_banco(pg_session):
    from app.core.security import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    user1 = User(name="A", email="duplicado@example.com", hashed_password=hash_password("x"), role=UserRole.USER)
    pg_session.add(user1)
    pg_session.commit()

    user2 = User(name="B", email="duplicado@example.com", hashed_password=hash_password("y"), role=UserRole.USER)
    pg_session.add(user2)
    with pytest.raises(IntegrityError):
        pg_session.commit()


def test_constraint_fk_impede_solicitacao_orfa(pg_session):
    from app.models.enums import RequestCategory
    from app.models.request import Request

    request = Request(
        title="Solicitacao orfa", description="Sem requester valido", category=RequestCategory.TI,
        requester_id=999999,
    )
    pg_session.add(request)
    with pytest.raises(IntegrityError):
        pg_session.commit()


def test_relacionamento_requester_e_assignee(pg_session):
    from app.core.security import hash_password
    from app.models.enums import RequestCategory, RequestPriority, UserRole
    from app.models.request import Request
    from app.models.user import User

    requester = User(name="Solicitante", email="solicitante.pg@example.com", hashed_password=hash_password("x"), role=UserRole.USER)
    assignee = User(name="Responsavel", email="responsavel.pg@example.com", hashed_password=hash_password("y"), role=UserRole.ANALYST)
    pg_session.add_all([requester, assignee])
    pg_session.commit()

    request = Request(
        title="Solicitacao com relacionamentos", description="Teste de relacionamento",
        category=RequestCategory.TI, priority=RequestPriority.ALTA,
        requester_id=requester.id, assignee_id=assignee.id,
    )
    pg_session.add(request)
    pg_session.commit()
    pg_session.refresh(request)

    assert request.requester.email == "solicitante.pg@example.com"
    assert request.assignee.email == "responsavel.pg@example.com"
