# Using Microsoft Graph /me/events in Azure Logic Apps (Delegated Auth, No Admin, Non-Prod)

This repository documents a working, non-production approach to call:

```
GET https://graph.microsoft.com/v1.0/me/events/{eventId}
```

from Azure Logic Apps, using delegated permissions and refresh tokens, **without admin consent**.

This is especially useful for PoCs, testing, and non-production systems, where admin access is unavailable.

## ❓ The Problem

Many developers run into this situation:

- They want to call Microsoft Graph `/me/events`
- They are using Azure Logic Apps
- They do **not** have admin consent
- They try:
  - username/password (ROPC)
  - browser tokens
  - Graph Explorer tokens
- Things work briefly… then break randomly

**Common errors:**
- `invalid_client`
- `invalid_grant`
- `AADSTS65001`
- `/me` works in Postman but not in Logic Apps

Microsoft documentation explains pieces of this — but not the full picture.

## 🧠 Root Cause (The Missing Mental Model)

### 1. `/me` requires delegated permissions
- Application permissions **cannot** call `/me`
- Logic Apps are non-interactive
- Delegated permissions require user consent

### 2. Logic Apps cannot trigger consent
- No UI
- No MFA handling
- No first-time login

### 3. ROPC (username/password) is deprecated
- Blocked by MFA
- Blocked by Conditional Access
- Unreliable and insecure

**So the real blocker is:**

> Delegated consent must happen **once, interactively**, before Logic Apps can work

## ✅ The Working Solution (Non-Prod / Testing)

The solution is:

1. Do **one interactive consent** as the user → capture a refresh token
2. Use that refresh token in Logic Apps

**No admin required** (as long as permissions allow user consent).

## 🧩 Prerequisites

- **Azure App Registration**
- **Delegated permissions:**
  - `Calendars.Read` or `Calendars.ReadWrite`
  - Permission must **not** require admin consent
- **A real Entra ID user** (example: `hiringautomation.user@company.com`)

## 🔑 Step 1 — One-Time Interactive Consent (Browser)

Open this URL in a browser (Incognito recommended):

```
https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize
?client_id={CLIENT_ID}
&response_type=code
&redirect_uri=https://localhost
&response_mode=query
&scope=offline_access Calendars.Read
&prompt=consent
```

1. Log in as the target user
2. Accept the consent screen
3. Copy the `code` from the redirect URL

## 🔄 Step 2 — Exchange Code for Tokens

Call the token endpoint:

```
POST https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded
```

**Body:**
```
client_id={CLIENT_ID}
&client_secret={CLIENT_SECRET}
&grant_type=authorization_code
&code={AUTH_CODE}
&redirect_uri=https://localhost
```

**Response includes:**
- `access_token`
- `refresh_token` ← **this is what Logic Apps will use**

### Quick Start: Get Credentials

We provide a Python script to automate this process:

```bash
# 1. Set up environment variables
cp .env.example .env
# Edit .env with your Azure AD credentials

# 2. Get initial credentials (includes refresh token)
python get_credentials_simple.py
```

This will output your `refresh_token` which you'll use in Logic Apps.

## ⚙️ Step 3 — Logic App: Refresh Access Token

Inside your Logic App:

### HTTP Action

**Method:** `POST`

**URI:**
```
https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token
```

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Body:**
```
grant_type=refresh_token
&client_id=@{variables('ClientId')}
&client_secret=@{variables('ClientSecret')}
&refresh_token=@{variables('RefreshToken')}
&scope=https://graph.microsoft.com/.default
```

This returns a fresh `access_token`.

### Format Bearer Token (Inline Code)

After the HTTP action, add an **Inline Code** action:

```javascript
// Get access token from HTTP response
const accessToken = workflowContext.actions.Refresh_Access_Token.outputs.body.access_token;

// Validate token exists
if (!accessToken) {
    throw new Error('Failed to retrieve access token from token endpoint');
}

// Return formatted bearer token
return `Bearer ${accessToken}`;
```

**Note:** Store credentials in Logic App variables or Azure Key Vault for security.

⚠️ **Refresh tokens may rotate.** For short-term testing, you can ignore this and reuse the same one.

## 📅 Step 4 — Call Microsoft Graph /me/events/{id}

Add another HTTP action:

**Method:** `GET`

**URI:**
```
https://graph.microsoft.com/v1.0/me/events/{EVENT_ID}
```

**Headers:**
```
Authorization: @{body('Format_Bearer_Token')}
Accept: application/json
```

This returns the event successfully.

## 🚨 Important Limitations

This approach is:

### ✅ Good for:
- PoCs
- Testing
- Non-production automation
- Short-lived workflows

### ❌ Not suitable for:
- Production
- MFA-protected users
- Long-running unattended automations

**Why?**
- Refresh tokens can be revoked
- MFA or password changes break it
- Logic Apps can't re-consent automatically

## 🟢 Production-Correct Alternative

For production systems, use:

```
GET /users/{userId}/events/{eventId}
```

With:
- **Application permissions**
- **Admin consent**

This is the only supported long-term approach.

## 🧠 Key Takeaways

- `/me` ⇒ delegated permissions only
- Logic Apps ⇒ non-interactive
- ROPC ⇒ deprecated and unreliable
- **One-time interactive consent is the missing link**
- Refresh tokens enable delegated auth in automation (temporarily)

## 📦 What's Included

This repository provides:

- **Python scripts** to get initial credentials and refresh tokens
- **Logic Apps integration patterns** (HTTP action + inline code)
- **Example code** for token refresh in Logic Apps
- **Complete documentation** of the authentication flow

### Files

- `get_credentials_simple.py` - Get initial credentials using Resource Owner Password Credentials Grant
- `refresh_token.py` - Refresh access tokens using refresh token
- `logic_app_refresh_token_clean.js` - Inline code for Logic Apps to format bearer tokens
- `main.py` - Example workflow for extracting attendance reports
- `auth.py`, `config.py`, `graph_client.py` - Supporting modules

## 📖 Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Get refresh token:**
   ```bash
   python get_credentials_simple.py
   ```

3. **Use in Logic Apps:**
   - Add HTTP action to refresh token (Step 3)
   - Add inline code to format bearer token
   - Call Graph API with bearer token (Step 4)

## 🔐 Security Best Practices

- **Never commit credentials** - Use environment variables or Azure Key Vault
- **Never hardcode credentials** in Logic App definitions
- **Rotate secrets regularly** - Update client secrets periodically
- **Use managed identities** - When possible, use Azure Managed Identity
- **Store tokens securely** - Use Azure Key Vault or secure variables in Logic Apps

## 📝 Requirements

- Python 3.8+
- Microsoft Azure AD App Registration
- Required permissions: `Calendars.Read`, `offline_access`
- Azure Logic Apps (for serverless integration)

## 🔗 Related Resources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/onlinemeeting)
- [OAuth 2.0 in Azure AD](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Azure Logic Apps Documentation](https://learn.microsoft.com/en-us/azure/logic-apps/)

## 📌 Why This Exists

This guide exists because:

- Microsoft docs don't explain this end-to-end
- Many teams hit this exact wall
- Errors are misleading
- The fix is simple once you understand the model

**If this helped you, consider ⭐ starring the repo so others can find it.**

## 📄 License

MIT License
