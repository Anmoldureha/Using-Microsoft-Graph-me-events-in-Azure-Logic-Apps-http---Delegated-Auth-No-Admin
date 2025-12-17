"""Simple script to get credentials using Resource Owner Password Credentials Grant."""
import msal
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
TENANT_ID = os.getenv('TENANT_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
SCOPE = os.getenv('SCOPE', 'Calendars.Read').split()

# Validate required environment variables
if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD]):
    print("Error: Missing required environment variables.", file=sys.stderr)
    print("Please set the following in your .env file:", file=sys.stderr)
    print("  - TENANT_ID", file=sys.stderr)
    print("  - CLIENT_ID", file=sys.stderr)
    print("  - CLIENT_SECRET", file=sys.stderr)
    print("  - USERNAME", file=sys.stderr)
    print("  - PASSWORD", file=sys.stderr)
    sys.exit(1)

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

def main():
    print("Authenticating with Resource Owner Password Credentials Grant...", file=sys.stderr)
    
    # Use ConfidentialClientApplication with client secret
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY
    )
    
    # Authenticate using username and password
    result = app.acquire_token_by_username_password(
        username=USERNAME,
        password=PASSWORD,
        scopes=SCOPE
    )
    
    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "Unknown error"))
        print(f"Failed to authenticate: {error}", file=sys.stderr)
        import json
        print(f"Full response: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)
    
    # Extract refresh token
    refresh_token = result.get('refresh_token', '')
    access_token = result.get('access_token', '')
    
    # Prepare output
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("CREDENTIALS")
    output_lines.append("=" * 80)
    output_lines.append("Name\tValue")
    output_lines.append(f"tenantId\t{TENANT_ID}")
    output_lines.append(f"clientId\t{CLIENT_ID}")
    output_lines.append(f"clientSecret\t{CLIENT_SECRET}")
    output_lines.append(f"refreshToken\t{refresh_token}")
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("FULL REFRESH TOKEN (for easy copying):")
    output_lines.append("=" * 80)
    output_lines.append(refresh_token)
    output_lines.append("=" * 80)
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("ACCESS TOKEN INFO:")
    output_lines.append("=" * 80)
    output_lines.append(f"Access Token (first 50 chars): {access_token[:50]}...")
    output_lines.append(f"Token Type: {result.get('token_type', 'N/A')}")
    output_lines.append(f"Expires In: {result.get('expires_in', 'N/A')} seconds")
    output_lines.append("=" * 80)
    
    # Print to console
    output_text = "\n".join(output_lines)
    print("\n" + output_text)
    
    # Save to file
    filename = "credentials.txt"
    with open(filename, 'w') as f:
        f.write(output_text)
    
    print(f"\n✓ Credentials saved to: {filename}", file=sys.stderr)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

