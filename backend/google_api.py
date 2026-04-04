import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from typing import Optional, Tuple

class GoogleAdminService:
    def __init__(self):
        self.credentials_file = "/app/api/elective-disciplines-login-4f76699c1b32.json"
        self.scopes = ["https://www.googleapis.com/auth/admin.directory.user.readonly"]
        self.service = None

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

    def get_user_info(self, email: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Fetches the full name, department (group), and orgUnitPath for a given user email.
        Returns (full_name, department, org_unit_path)
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
            
            department = None
            orgs = user.get("organizations", [])
            if orgs:
                department = orgs[0].get("department")

            org_unit_path = user.get("orgUnitPath")
            return full_name, department, org_unit_path
        except Exception as e:
            print(f"Error fetching user info from Google for {email}: {e}")
            return None, None, None

# Singleton instance
google_admin = GoogleAdminService()
