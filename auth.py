"""Microsoft Graph API authentication handler."""
import msal
from config import Config

class GraphAuth:
    """Handles authentication with Microsoft Graph API."""
    
    def __init__(self):
        self.config = Config()
        self.app = msal.ConfidentialClientApplication(
            client_id=self.config.CLIENT_ID,
            client_credential=self.config.CLIENT_SECRET,
            authority=self.config.authority
        )
        self.access_token = None
    
    def authenticate_with_password(self):
        """
        Authenticate using Resource Owner Password Credentials Grant.
        This is useful for service accounts but less secure than authorization code flow.
        """
        try:
            result = self.app.acquire_token_by_username_password(
                username=self.config.USERNAME,
                password=self.config.PASSWORD,
                scopes=self.config.SCOPE
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                return self.access_token
            else:
                error = result.get("error_description", result.get("error", "Unknown error"))
                raise Exception(f"Authentication failed: {error}")
        except Exception as e:
            raise Exception(f"Failed to authenticate: {str(e)}")
    
    def get_authorization_url(self):
        """Get the authorization URL for OAuth code flow."""
        return self.config.authorization_url
    
    def authenticate_with_code(self, authorization_code):
        """
        Authenticate using authorization code from OAuth flow.
        This is the recommended approach for production applications.
        """
        try:
            result = self.app.acquire_token_by_authorization_code(
                code=authorization_code,
                scopes=self.config.SCOPE,
                redirect_uri=self.config.REDIRECT_URI
            )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                return self.access_token
            else:
                error = result.get("error_description", result.get("error", "Unknown error"))
                raise Exception(f"Authentication failed: {error}")
        except Exception as e:
            raise Exception(f"Failed to authenticate with code: {str(e)}")
    
    def get_access_token(self):
        """Get the current access token."""
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate_with_password() or authenticate_with_code() first.")
        return self.access_token

