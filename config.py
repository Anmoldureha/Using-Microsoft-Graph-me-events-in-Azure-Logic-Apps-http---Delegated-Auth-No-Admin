"""Configuration management for the attendance extraction application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Azure AD Configuration
    TENANT_ID = os.getenv('TENANT_ID', '')
    CLIENT_ID = os.getenv('CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', '')
    
    # User Credentials
    USERNAME = os.getenv('USERNAME', '')
    PASSWORD = os.getenv('PASSWORD', '')
    
    # OAuth Configuration
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'https://localhost')
    SCOPE = os.getenv('SCOPE', 'offline_access Calendars.Read').split()
    
    # Microsoft Graph API
    GRAPH_API_ENDPOINT = os.getenv('GRAPH_API_ENDPOINT', 'https://graph.microsoft.com/v1.0')
    
    # Authority URL
    @property
    def authority(self):
        return f"https://login.microsoftonline.com/{self.TENANT_ID}"
    
    # OAuth Authorization URL
    @property
    def authorization_url(self):
        scope_str = ' '.join(self.SCOPE)
        return (
            f"{self.authority}/oauth2/v2.0/authorize"
            f"?client_id={self.CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={self.REDIRECT_URI}"
            f"&response_mode=query"
            f"&scope={scope_str}"
            f"&prompt=consent"
        )

