# Since we moved auth to middleware, keep only business logic handlers
from .auth.Authhandler import auth_handler

# admin handlers
from .admin import master_kamus as admin_master_kamus

__all__ = [
    "auth_handler",
    "admin_master_kamus",
]