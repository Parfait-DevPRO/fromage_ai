"""Local username/password authentication, without e-mail, OTP or Google."""
from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from config.settings import BASE_DIR, secret
from config.supabase_client import get_supabase_client

DATABASE_PATH = BASE_DIR / "data" / "cheese_ai.db"
ITERATIONS = 310_000


@dataclass
class LocalUser:
    id: str
    username: str


class AuthService:
    def __init__(self, database_path: Path = DATABASE_PATH, remote_client=None, require_remote: bool = False):
        self.database_path = database_path
        # Keep standalone/local AuthService use isolated. The web controller opts
        # into mandatory Supabase explicitly, preventing accidental network calls.
        self.remote_client = remote_client if remote_client is not None else (
            self._make_remote_client() if require_remote else None
        )
        self.require_remote = require_remote
        self.remote_configured = bool(secret("SUPABASE_URL") and secret("SUPABASE_KEY"))
        self.remote_key = secret("SUPABASE_KEY")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as conn:
            conn.execute("""create table if not exists local_users (
                id text primary key, username text unique not null collate nocase,
                password_hash text not null, created_at text default current_timestamp
            )""")

    def _connection(self):
        return sqlite3.connect(self.database_path)

    @staticmethod
    def _make_remote_client():
        return get_supabase_client()

    def _sync_user(self, user: LocalUser) -> None:
        """Mirror the local identity in Supabase; no password is ever uploaded."""
        if not self.remote_client:
            if self.require_remote:
                if not self.remote_configured:
                    raise RuntimeError("Supabase n'est pas configuré. Renseignez SUPABASE_URL et SUPABASE_KEY dans .env ou les secrets Streamlit.")
                raise RuntimeError("Le client Supabase n'a pas pu être initialisé. Vérifiez l'URL et la clé du projet.")
            return
        if self.require_remote and self.remote_key.startswith("sb_publishable_"):
            raise RuntimeError("L'application écrit dans Supabase depuis son serveur. Utilisez une clé secrète sb_secret_ dans les secrets Streamlit, pas la clé publishable.")
        try:
            self.remote_client.table("users").upsert(
                {"id": user.id, "username": user.username, "display_name": user.username},
                on_conflict="id",
            ).execute()
        except Exception as exc:
            raise RuntimeError("Impossible d'enregistrer le compte dans Supabase. Vérifiez SUPABASE_URL, SUPABASE_KEY et le script SQL.") from exc

    @staticmethod
    def _validate(username: str, password: str) -> tuple[str, str]:
        username = username.strip()
        if not 3 <= len(username) <= 30 or not all(c.isalnum() or c in "_.-" for c in username):
            raise ValueError("Le nom d'utilisateur doit avoir 3 à 30 caractères (lettres, chiffres, _, . ou -).")
        if len(password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
        return username, password

    @staticmethod
    def _hash(password: str, salt: bytes | None = None) -> str:
        salt = salt or os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
        return f"{salt.hex()}${digest.hex()}"

    @staticmethod
    def _matches(password: str, stored: str) -> bool:
        try:
            salt_hex, expected = stored.split("$", 1)
            actual = AuthService._hash(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
            return hmac.compare_digest(actual, expected)
        except (ValueError, AttributeError):
            return False

    def sign_up(self, username: str, password: str) -> LocalUser:
        username, password = self._validate(username, password)
        user = LocalUser(str(uuid4()), username)
        try:
            with self._connection() as conn:
                conn.execute("insert into local_users (id, username, password_hash) values (?, ?, ?)",
                             (user.id, username, self._hash(password)))
        except sqlite3.IntegrityError as exc:
            raise ValueError("Ce nom d'utilisateur existe déjà.") from exc
        try:
            self._sync_user(user)
        except RuntimeError:
            with self._connection() as conn:
                conn.execute("delete from local_users where id = ?", (user.id,))
            raise
        return user

    def sign_in(self, username: str, password: str) -> LocalUser:
        username, password = self._validate(username, password)
        with self._connection() as conn:
            row = conn.execute("select id, username, password_hash from local_users where username = ?", (username,)).fetchone()
        if not row or not self._matches(password, row[2]):
            raise ValueError("Nom d'utilisateur ou mot de passe incorrect.")
        user = LocalUser(row[0], row[1])
        self._sync_user(user)
        return user
