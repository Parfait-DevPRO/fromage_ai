"""Supabase-native authentication service (Zero SQLite).

All user credentials, authentication tokens, and profile records are handled
exclusively through Supabase Auth (bcrypt) and the Supabase `public.users` table.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests

from config.settings import secret
from config.supabase_client import get_supabase_client, clean_supabase_url, clean_supabase_key


@dataclass
class LocalUser:
    id: str
    username: str
    display_name: str | None = None

    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.username


class AuthService:
    def __init__(self, *args, remote_client=None, require_remote: bool = True, **kwargs):
        self.client = remote_client or get_supabase_client()
        self.url = clean_supabase_url(secret("SUPABASE_URL"))
        self.key = clean_supabase_key(secret("SUPABASE_KEY"))
        if not self.url or not self.key or not self.client:
            raise RuntimeError(
                "Supabase n'est pas configuré. Veuillez vérifier SUPABASE_URL et SUPABASE_KEY dans .env ou .streamlit/secrets.toml."
            )
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    @staticmethod
    def _to_email(username_or_email: str) -> str:
        s = username_or_email.strip().lower()
        if "@" in s:
            return s
        return f"{s}@fromazy.app"

    @staticmethod
    def _validate(username: str, password: str) -> tuple[str, str]:
        username = username.strip()
        if not 3 <= len(username) <= 30 or not all(c.isalnum() or c in "_.-" for c in username):
            raise ValueError("Le nom d'utilisateur doit avoir 3 à 30 caractères (lettres, chiffres, _, . ou -).")
        if len(password) < 6:
            raise ValueError("Le mot de passe doit contenir au moins 6 caractères.")
        return username, password

    def sign_up(self, username: str, password: str, display_name: str | None = None) -> LocalUser:
        """Create a user account natively in Supabase Auth and public.users."""
        username, password = self._validate(username, password)
        display_name = (display_name or username).strip()

        # 1. Check if username is already taken in public.users
        try:
            existing = self.client.table("users").select("id").ilike("username", username).execute()
            if existing and existing.data and len(existing.data) > 0:
                raise ValueError("Ce nom d'utilisateur est déjà utilisé. Veuillez en choisir un autre.")
        except ValueError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Impossible de vérifier l'utilisateur dans Supabase: {exc}") from exc

        # 2. Register user in Supabase Auth via Admin API
        email = self._to_email(username)
        admin_url = f"{self.url}/auth/v1/admin/users"
        payload = {
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {
                "username": username,
                "display_name": display_name,
            },
        }

        try:
            resp = requests.post(admin_url, json=payload, headers=self.headers, timeout=12)
        except Exception as exc:
            raise RuntimeError(f"Impossible de joindre le serveur Supabase: {exc}") from exc

        user_id = None
        if resp.status_code in (200, 201):
            user_data = resp.json()
            user_id = user_data.get("id")
        elif resp.status_code == 422:
            # Email exists in auth.users. Check if it's an orphan or update it
            try:
                list_res = requests.get(admin_url, headers=self.headers, timeout=10)
                if list_res.status_code == 200:
                    for u in list_res.json().get("users", []):
                        if u.get("email") == email:
                            # Update existing auth user password
                            user_id = u.get("id")
                            requests.put(
                                f"{admin_url}/{user_id}",
                                json={"password": password, "user_metadata": {"username": username, "display_name": display_name}},
                                headers=self.headers,
                                timeout=10,
                            )
                            break
            except Exception:
                pass
            if not user_id:
                raise ValueError("Ce nom d'utilisateur ou cet e-mail est déjà utilisé.")
        else:
            err_msg = resp.text
            try:
                err_data = resp.json()
                err_msg = err_data.get("msg") or err_data.get("message") or err_msg
            except Exception:
                pass
            raise RuntimeError(f"Erreur d'inscription Supabase : {err_msg}")

        # 3. Create or update profile in public.users
        try:
            self.client.table("users").upsert(
                {
                    "id": user_id,
                    "username": username,
                    "display_name": display_name,
                },
                on_conflict="id",
            ).execute()
        except Exception as exc:
            # Rollback auth user creation if public.users fails
            try:
                requests.delete(f"{admin_url}/{user_id}", headers=self.headers, timeout=5)
            except Exception:
                pass
            raise RuntimeError(f"Impossible de synchroniser le profil dans public.users : {exc}") from exc

        return LocalUser(id=user_id, username=username, display_name=display_name)

    def sign_in(self, username: str, password: str) -> LocalUser:
        """Authenticate user natively via Supabase Auth and fetch profile from public.users."""
        username = username.strip()
        if not username or not password:
            raise ValueError("Veuillez renseigner un nom d'utilisateur et un mot de passe.")

        email = self._to_email(username)
        login_url = f"{self.url}/auth/v1/token?grant_type=password"

        try:
            resp = requests.post(
                login_url,
                json={"email": email, "password": password},
                headers=self.headers,
                timeout=12,
            )
        except Exception as exc:
            raise RuntimeError(f"Impossible de joindre le serveur Supabase : {exc}") from exc

        if resp.status_code == 200:
            auth_data = resp.json()
            user_info = auth_data.get("user", {})
            user_id = user_info.get("id")

            # Fetch user profile from public.users
            try:
                profile_res = self.client.table("users").select("*").eq("id", user_id).execute()
                if profile_res and profile_res.data and len(profile_res.data) > 0:
                    row = profile_res.data[0]
                    return LocalUser(
                        id=row["id"],
                        username=row.get("username") or username,
                        display_name=row.get("display_name") or username,
                    )
            except Exception:
                pass

            # Fallback if profile row is not yet in public.users
            try:
                self.client.table("users").upsert(
                    {
                        "id": user_id,
                        "username": username,
                        "display_name": username,
                    },
                    on_conflict="id",
                ).execute()
            except Exception:
                pass
            return LocalUser(id=user_id, username=username, display_name=username)

        # In case the user signed up with an actual email that is stored in user_metadata or public.users
        try:
            user_search = self.client.table("users").select("id,username,display_name").ilike("username", username).execute()
            if user_search and user_search.data and len(user_search.data) > 0:
                uid = user_search.data[0]["id"]
                admin_res = requests.get(f"{self.url}/auth/v1/admin/users/{uid}", headers=self.headers, timeout=5)
                if admin_res.status_code == 200:
                    actual_email = admin_res.json().get("email")
                    if actual_email and actual_email != email:
                        retry_resp = requests.post(
                            login_url,
                            json={"email": actual_email, "password": password},
                            headers=self.headers,
                            timeout=12,
                        )
                        if retry_resp.status_code == 200:
                            u_row = user_search.data[0]
                            return LocalUser(
                                id=u_row["id"],
                                username=u_row.get("username") or username,
                                display_name=u_row.get("display_name") or username,
                            )
        except Exception:
            pass

        raise ValueError("Nom d'utilisateur ou mot de passe incorrect.")
