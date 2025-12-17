# Microsoft Teams Attendance Report Extractor

A comprehensive solution for extracting attendance reports from Microsoft Teams meetings using Microsoft Graph API. This project provides tools for OAuth authentication, token management, and attendance data extraction.

## 🎯 Problem Statement

### The Challenge

Microsoft Teams attendance reports are only accessible through the Microsoft Graph API, which requires:
1. **OAuth 2.0 Authentication** - Complex authentication flows with multiple grant types
2. **Token Management** - Access tokens expire frequently (typically every hour)
3. **Refresh Token Flow** - Need to refresh tokens without user interaction
4. **Azure Logic Apps Integration** - Serverless workflows need reliable token refresh mechanisms

### Common Issues This Solves

- **Token Expiration**: Access tokens expire quickly, breaking automated workflows
- **Logic Apps Connector Limitations**: Built-in connectors don't support all Graph API endpoints
- **Logic Apps Inline Code Limitations**: Can't make HTTP requests directly
- **Token Refresh Complexity**: Difficult to implement refresh pattern in Logic Apps

### What This Solution Addresses

✅ **Works around Logic Apps connector limitations** - Access any Graph API endpoint via HTTP actions  
✅ **Solves token expiration issues** - Automatic token refresh pattern  
✅ **Simplifies authentication** - Clear patterns for service account authentication  
✅ **Handles Logic Apps constraints** - HTTP Action + Inline Code pattern that works within limitations  

⚠️ **Important**: This solution does NOT bypass required permissions. You still need proper Azure AD app registration, required API permissions granted, and valid credentials.

## 💡 Solution Overview

This project provides:
1. **Python Scripts** for initial authentication and token generation
2. **Token Refresh Mechanism** for automated token renewal
3. **Azure Logic Apps Integration** patterns for serverless workflows
4. **Email Parsing** to extract meeting information from Teams invitations

## 🚀 Use Cases

- **Automated Attendance Tracking** - Track attendance for recurring meetings, training sessions, or interviews
- **Compliance and Reporting** - Generate attendance reports for compliance audits or HR requirements
- **Interview Scheduling and Tracking** - Track candidate attendance, identify no-shows
- **Training Session Management** - Monitor training session attendance and engagement
- **Meeting Analytics** - Analyze meeting participation patterns
- **Automated Workflows in Logic Apps** - Integrate attendance data into business processes

## 📋 Architecture

```
Email Parser → OAuth Flow → Token Refresh → Graph API → Attendance Reports
```

## 🔧 Components

### Core Scripts
- `get_credentials_simple.py` - Get initial credentials using Resource Owner Password Credentials Grant
- `refresh_token.py` - Refresh access tokens using refresh token
- `main.py` - Complete workflow orchestrator for attendance extraction
- `setup_env.py` - Interactive script to set up environment variables

### Supporting Modules
- `auth.py` - OAuth authentication handler
- `config.py` - Configuration management
- `email_parser.py` - Parse HTML emails to extract meeting information
- `graph_client.py` - Microsoft Graph API client for fetching attendance

### Logic Apps Integration
- `logic_app_refresh_token_clean.js` - Inline code for formatting bearer tokens (use after HTTP action)

## 📖 Quick Start

### Step 1: Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Azure AD credentials:
   ```env
   TENANT_ID=your_tenant_id
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   USERNAME=your_username@domain.com
   PASSWORD=your_password
   REDIRECT_URI=http://localhost:4200
   SCOPE=Calendars.Read
   ```

### Step 2: Get Initial Credentials

```bash
python get_credentials_simple.py
```

This generates and saves:
- `tenantId`
- `clientId`
- `clientSecret`
- `refreshToken`

The refresh token will be saved to `credentials.txt` and can be added to `.env` as `REFRESH_TOKEN`.

### Step 3: Refresh Token (Python)

```bash
python refresh_token.py
```

### Step 4: Use in Logic Apps

See "Azure Logic Apps Integration" section below for detailed steps.

## 🛠️ Azure Logic Apps Integration

### The Problem

- Logic Apps inline code cannot make HTTP requests directly
- Access tokens expire after ~1 hour, breaking workflows
- Built-in connectors don't support all Graph API endpoints

### The Solution: HTTP Action + Inline Code Pattern

**Step 1: Configure HTTP Action for Token Refresh**

**Action Name**: `Refresh_Access_Token`

**Method**: `POST`

**URI**: 
```
https://login.microsoftonline.com/@{variables('TenantId')}/oauth2/v2.0/token
```

**Headers**:
```
Content-Type: application/x-www-form-urlencoded
```

**Body** (raw):
```
grant_type=refresh_token&client_id=@{variables('ClientId')}&client_secret=@{variables('ClientSecret')}&refresh_token=@{variables('RefreshToken')}&scope=Calendars.Read
```

**Step 2: Add Inline Code to Format Bearer Token**

**Action Name**: `Format_Bearer_Token`

**Code**:
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

**Step 3: Use Bearer Token in Graph API Calls**

**Action Name**: `Get_Attendance_Report`

**Method**: `GET`

**URI**: 
```
https://graph.microsoft.com/v1.0/me/onlineMeetings/{meetingId}/attendanceReports
```

**Headers**:
```
Authorization: @{body('Format_Bearer_Token')}
Content-Type: application/json
```

### Logic App Variables Setup

1. Go to Logic App → Variables
2. Add variables:
   - `TenantId`: Your Azure AD tenant ID
   - `ClientId`: Your app registration client ID
   - `ClientSecret`: Your app registration client secret
   - `RefreshToken`: Your refresh token (update when it expires)

**Alternative**: Use Azure Key Vault for production environments.

### Why This Pattern Works

1. **Logic Apps Limitation**: Inline code can't make HTTP requests directly
2. **Solution**: Use HTTP action + inline code to format result
3. **Benefit**: Clean separation, easy to maintain, reusable pattern

## 🔐 Security Best Practices

- **Never commit credentials** - Use environment variables or Azure Key Vault
- **Never hardcode credentials** in Logic App definitions
- **Rotate secrets regularly** - Update client secrets periodically
- **Use managed identities** - When possible, use Azure Managed Identity
- **Store tokens securely** - Use Azure Key Vault or secure variables in Logic Apps

## 📊 Output Format

Attendance reports are saved as JSON with:
- Meeting information (ID, passcode, join link)
- Attendance records (participants, join/leave times, duration)
- Metadata (extraction timestamp, meeting organizer)

## 🔄 Token Lifecycle

1. **Initial Authentication**: Get refresh token (long-lived, ~90 days)
2. **Token Refresh**: Use refresh token to get new access token (short-lived, ~1 hour)
3. **Automatic Renewal**: Refresh token before expiration in automated workflows

## 📝 Requirements

- Python 3.8+
- Microsoft Azure AD App Registration
- Required permissions: `Calendars.Read`, `offline_access`
- Azure Logic Apps (for serverless integration)

## 🔗 Related Resources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/onlinemeeting)
- [OAuth 2.0 in Azure AD](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Azure Logic Apps Documentation](https://learn.microsoft.com/en-us/azure/logic-apps/)

## 📄 License

MIT License
