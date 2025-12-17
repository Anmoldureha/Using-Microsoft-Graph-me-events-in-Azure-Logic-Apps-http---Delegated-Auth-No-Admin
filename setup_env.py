"""Helper script to set up environment variables from provided credentials."""
import os

def create_env_file():
    """Create .env file from user input or provided credentials."""
    
    print("Microsoft Teams Attendance Extractor - Environment Setup")
    print("=" * 60)
    
    # Get credentials from user
    tenant_id = input("Enter TENANT_ID: ").strip()
    client_id = input("Enter CLIENT_ID: ").strip()
    client_secret = input("Enter CLIENT_SECRET: ").strip()
    username = input("Enter USERNAME (email): ").strip()
    password = input("Enter PASSWORD: ").strip()
    
    redirect_uri = input("Enter REDIRECT_URI (default: https://localhost): ").strip() or "https://localhost"
    scope = input("Enter SCOPE (default: offline_access Calendars.Read): ").strip() or "offline_access Calendars.Read"
    
    # Create .env file content
    env_content = f"""# Microsoft Azure AD Configuration
TENANT_ID={tenant_id}
CLIENT_ID={client_id}
CLIENT_SECRET={client_secret}

# User Credentials (for Resource Owner Password Credentials Grant)
USERNAME={username}
PASSWORD={password}

# OAuth Configuration
REDIRECT_URI={redirect_uri}
SCOPE={scope}

# Microsoft Graph API
GRAPH_API_ENDPOINT=https://graph.microsoft.com/v1.0
"""
    
    # Write to .env file
    env_path = ".env"
    if os.path.exists(env_path):
        overwrite = input(f"\n.env file already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Cancelled. .env file not modified.")
            return
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n✓ .env file created successfully at {env_path}")
    print("\n⚠️  IMPORTANT: Make sure .env is in .gitignore and never commit it to version control!")

if __name__ == "__main__":
    create_env_file()

