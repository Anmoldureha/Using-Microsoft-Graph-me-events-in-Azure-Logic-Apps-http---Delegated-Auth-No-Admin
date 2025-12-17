// Azure Logic Apps Inline Code - Token Refresh
// This code formats the bearer token from the HTTP response
// Use this AFTER an HTTP action that calls the Microsoft OAuth token endpoint

// Get access token from HTTP response
// Replace 'Get_Bearer_Token' with your HTTP action name
const accessToken = workflowContext.actions.Get_Bearer_Token.outputs.body.access_token;

// Validate token exists
if (!accessToken) {
    throw new Error('Failed to retrieve access token from token endpoint');
}

// Return formatted bearer token
return `Bearer ${accessToken}`;

