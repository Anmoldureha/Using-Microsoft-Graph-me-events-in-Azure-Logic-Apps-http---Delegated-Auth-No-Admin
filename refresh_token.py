"""Refresh access token using refresh token."""
import requests
import sys
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
TENANT_ID = os.getenv('TENANT_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPE = os.getenv('SCOPE', 'Calendars.Read')

# Validate required environment variables
if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
    print("Error: Missing required environment variables.", file=sys.stderr)
    print("Please set the following in your .env file:", file=sys.stderr)
    print("  - TENANT_ID", file=sys.stderr)
    print("  - CLIENT_ID", file=sys.stderr)
    print("  - CLIENT_SECRET", file=sys.stderr)
    sys.exit(1)

# Read refresh token from environment or credentials.txt
def get_refresh_token():
    # First try to get from environment variable
    refresh_token = os.getenv('REFRESH_TOKEN')
    if refresh_token:
        return refresh_token
    
    # Fallback to reading from credentials.txt
    try:
        with open('credentials.txt', 'r') as f:
            content = f.read()
            # Find the refresh token line
            for line in content.split('\n'):
                if 'refreshToken' in line and '\t' in line:
                    return line.split('\t')[1].strip()
            # If not found in tab format, try to find the full token section
            if 'FULL REFRESH TOKEN' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'FULL REFRESH TOKEN' in line:
                        # Get the next non-empty line after the separator
                        for j in range(i+1, len(lines)):
                            if lines[j].strip() and not lines[j].startswith('='):
                                return lines[j].strip()
    except FileNotFoundError:
        pass
    
    return None

def refresh_access_token(refresh_token):
    """Refresh access token using refresh token."""
    
    # Token endpoint URL
    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    # Request body parameters
    data = {
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'scope': SCOPE
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print("Requesting new access token...", file=sys.stderr)
    print(f"URL: {token_url}", file=sys.stderr)
    print(f"Body parameters:", file=sys.stderr)
    print(f"  grant_type: {data['grant_type']}", file=sys.stderr)
    print(f"  client_id: {data['client_id']}", file=sys.stderr)
    print(f"  client_secret: {data['client_secret']}", file=sys.stderr)
    print(f"  refresh_token: {refresh_token[:50]}...", file=sys.stderr)
    print(f"  scope: {data['scope']}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Make the request
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        if 'access_token' in result:
            access_token = result['access_token']
            new_refresh_token = result.get('refresh_token', refresh_token)  # May get new refresh token
            
            print("=" * 80)
            print("SUCCESS - NEW ACCESS TOKEN OBTAINED")
            print("=" * 80)
            print(f"\nBearer Token: {access_token}")
            print(f"\nToken Type: {result.get('token_type', 'Bearer')}")
            print(f"Expires In: {result.get('expires_in', 'N/A')} seconds")
            
            if 'refresh_token' in result:
                print(f"\nNew Refresh Token: {new_refresh_token}")
            
            # Save to file
            output = {
                'access_token': access_token,
                'token_type': result.get('token_type', 'Bearer'),
                'expires_in': result.get('expires_in'),
                'refresh_token': new_refresh_token,
                'scope': result.get('scope', SCOPE)
            }
            
            with open('access_token.txt', 'w') as f:
                f.write(f"Bearer Token: {access_token}\n")
                f.write(f"Token Type: {output['token_type']}\n")
                f.write(f"Expires In: {output['expires_in']} seconds\n")
                f.write(f"\nRefresh Token: {new_refresh_token}\n")
            
            print(f"\n✓ Token saved to: access_token.txt", file=sys.stderr)
            
            return result
        else:
            print("Error: No access_token in response", file=sys.stderr)
            print(f"Response: {json.dumps(result, indent=2)}", file=sys.stderr)
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        try:
            error_detail = e.response.json()
            print(f"Error details: {json.dumps(error_detail, indent=2)}", file=sys.stderr)
        except:
            print(f"Response text: {e.response.text}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None

def main():
    refresh_token = get_refresh_token()
    
    if not refresh_token:
        print("Error: Could not find refresh token.", file=sys.stderr)
        print("Please set REFRESH_TOKEN in your .env file or run get_credentials_simple.py first.", file=sys.stderr)
        sys.exit(1)
    
    result = refresh_access_token(refresh_token)
    
    if result:
        print("\n" + "=" * 80)
        print("You can now use this bearer token for Microsoft Graph API calls")
        print("=" * 80)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

