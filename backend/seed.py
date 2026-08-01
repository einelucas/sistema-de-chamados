"""Script de seed: cria o usuario administrador inicial e dados minimos.

Uso:
    python seed.py
"""
from app.core.security import hash_password
from app.database.session import SessionLocal
from app.core.config import settings
from app.models.enums import UserRole
from app.models.user import User


def run_seed() -> None:
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing_admin:
            print(f"Usuario administrador '{settings.ADMIN_EMAIL}' ja existe. Nenhuma acao necessaria.")
            return

        admin = User(
            name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Usuario administrador criado com sucesso: {settings.ADMIN_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
