"""Integration-only identities cannot authenticate or become staff."""
from app.core.exceptions import ForbiddenError

def reject_integration_user(user):
    if user.integration_identity or user.email.lower().endswith("@integration.example.com"):
        raise ForbiddenError("Identidade de integração protegida.")
