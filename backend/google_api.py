import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Optional, Tuple

# Matches academic group names like "КН-2/1", "ФБС-2/1, ОП-2/1"
_ACADEMIC_NAME_RE = re.compile(
    r'^[А-ЯІЇЄҐ]{1,5}-\d+/\d+(,\s*[А-ЯІЇЄҐ]{1,5}-\d+/\d+)*$'
)
_DOMAIN = "rcit.ukr.education"

class GoogleAdminService:
    def __init__(self):
        self.credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/api/elective-disciplines-login-4f76699c1b32.json")
        self.scopes = [
            "https://www.googleapis.com/auth/admin.directory.user.readonly",
            "https://www.googleapis.com/auth/admin.directory.group.readonly",
        ]
        self.service = None
        self._academic_group_emails: Optional[dict] = None  # {email: group_name} cache

    def _get_service(self):
        if self.service:
            return self.service

        if not os.path.exists(self.credentials_file):
            print(f"Error: {self.credentials_file} not found.")
            return None

        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.scopes,
            )
            self.service = build("admin", "directory_v1", credentials=credentials, cache_discovery=False)
            return self.service
        except Exception as e:
            print(f"Failed to initialize Google Admin Service: {e}")
            return None

    def _load_academic_groups(self) -> dict:
        """Build {group_email: group_name} map for all academic groups. Cached for process lifetime."""
        if self._academic_group_emails is not None:
            return self._academic_group_emails

        service = self._get_service()
        if not service:
            return {}

        try:
            result = {}
            page_token = None
            while True:
                resp = service.groups().list(
                    domain=_DOMAIN, maxResults=200, pageToken=page_token
                ).execute()
                for g in resp.get("groups", []):
                    if _ACADEMIC_NAME_RE.match(g['name']):
                        result[g['email']] = g['name']
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break
            self._academic_group_emails = result
            print(f"Loaded {len(result)} academic groups from Google")
            return result
        except Exception as e:
            print(f"Error loading academic groups: {e}")
            return {}

    def _get_group_from_memberships(self, email: str) -> Optional[str]:
        """Return the academic group name for a user based on their Google Group memberships."""
        service = self._get_service()
        if not service:
            return None

        academic_map = self._load_academic_groups()
        if not academic_map:
            return None

        try:
            resp = service.groups().list(
                domain=_DOMAIN, userKey=email, maxResults=50
            ).execute()
            matched = [
                academic_map[g['email']]
                for g in resp.get("groups", [])
                if g['email'] in academic_map
            ]
            if not matched:
                return None
            # Prefer combined groups (longer name) when a student belongs to multiple
            return max(matched, key=len)
        except Exception as e:
            print(f"Error fetching group memberships for {email}: {e}")
            return None

    def get_user_info(self, email: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Returns (full_name, group_name, org_unit_path).
        group_name is resolved from Google Group memberships (authoritative source).
        Falls back to orgUnitPath if no academic group membership found.
        """
        service = self._get_service()
        if not service:
            return None, None, None

        try:
            print(f"Fetching Google profile for: {email}...")
            user = service.users().get(
                userKey=email,
                projection="full",
                viewType="admin_view",
            ).execute()

            full_name = user.get("name", {}).get("fullName")
            org_unit_path = user.get("orgUnitPath")

            group_name = self._get_group_from_memberships(email)
            return full_name, group_name, org_unit_path
        except Exception as e:
            print(f"Error fetching user info from Google for {email}: {e}")
            return None, None, None


# Singleton instance
google_admin = GoogleAdminService()
