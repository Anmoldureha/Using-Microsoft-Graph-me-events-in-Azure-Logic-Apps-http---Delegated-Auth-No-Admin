"""Main application to extract attendance reports from Microsoft Teams meetings."""
import json
import os
from datetime import datetime
from auth import GraphAuth
from email_parser import EmailParser
from graph_client import GraphClient

def save_attendance_report(meeting_info: dict, attendance_data: dict, output_dir: str = "attendance_reports"):
    """Save attendance report to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    meeting_id_clean = meeting_info.get('meeting_id', 'unknown').replace(' ', '_')
    filename = f"{output_dir}/attendance_{meeting_id_clean}_{timestamp}.json"
    
    report = {
        'meeting_info': meeting_info,
        'attendance_data': attendance_data,
        'extracted_at': datetime.now().isoformat()
    }
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Attendance report saved to: {filename}")
    return filename

def process_email_html(html_body: str, use_password_auth: bool = True):
    """
    Process HTML email body to extract meeting info and fetch attendance report.
    
    Args:
        html_body: HTML content of the email
        use_password_auth: If True, use password authentication; if False, use OAuth code flow
    """
    # Parse email to extract meeting information
    print("Parsing email HTML...")
    parser = EmailParser()
    meeting_info = parser.extract_meeting_info(html_body)
    
    print(f"Extracted meeting info:")
    print(json.dumps(meeting_info, indent=2))
    
    if not meeting_info.get('thread_id'):
        print("Warning: Could not extract meeting thread ID from email")
        return None
    
    # Authenticate with Microsoft Graph API
    print("\nAuthenticating with Microsoft Graph API...")
    auth = GraphAuth()
    
    try:
        if use_password_auth:
            access_token = auth.authenticate_with_password()
            print("✓ Authentication successful (password grant)")
        else:
            # For OAuth code flow, user needs to visit the authorization URL
            auth_url = auth.get_authorization_url()
            print(f"\nPlease visit this URL to authorize the application:")
            print(auth_url)
            print("\nAfter authorization, you'll be redirected to localhost with a code parameter.")
            print("Please provide the authorization code:")
            auth_code = input("Authorization code: ").strip()
            access_token = auth.authenticate_with_code(auth_code)
            print("✓ Authentication successful (authorization code grant)")
    except Exception as e:
        print(f"✗ Authentication failed: {str(e)}")
        return None
    
    # Create Graph API client
    client = GraphClient(auth)
    
    # Extract meeting ID from thread_id
    meeting_id = meeting_info.get('thread_id')
    
    # Fetch attendance report
    print(f"\nFetching attendance report for meeting: {meeting_id}")
    attendance_report = client.get_online_meeting_attendance_report(meeting_id)
    
    if attendance_report:
        print("✓ Attendance report retrieved successfully")
        
        # If there are multiple reports, get records for each
        reports = attendance_report.get('value', [])
        if reports:
            print(f"Found {len(reports)} attendance report(s)")
            
            all_records = []
            for report in reports:
                report_id = report.get('id')
                print(f"\nFetching records for report: {report_id}")
                records = client.get_meeting_attendance_records(meeting_id, report_id)
                if records:
                    all_records.extend(records)
                    print(f"  Found {len(records)} attendance record(s)")
            
            # Save the complete report
            full_report = {
                'reports': reports,
                'attendance_records': all_records
            }
            
            filename = save_attendance_report(meeting_info, full_report)
            
            # Print summary
            print(f"\n{'='*60}")
            print("ATTENDANCE SUMMARY")
            print(f"{'='*60}")
            print(f"Meeting ID: {meeting_info.get('meeting_id', 'N/A')}")
            print(f"Total Records: {len(all_records)}")
            
            if all_records:
                print("\nAttendees:")
                for i, record in enumerate(all_records, 1):
                    identity = record.get('identity', {})
                    email = identity.get('emailAddress', {}).get('address', 'N/A')
                    name = identity.get('emailAddress', {}).get('name', 'N/A')
                    join_time = record.get('joinDateTime', 'N/A')
                    leave_time = record.get('leaveDateTime', 'N/A')
                    duration = record.get('totalAttendanceInSeconds', 0)
                    
                    print(f"  {i}. {name} ({email})")
                    print(f"     Joined: {join_time}, Left: {leave_time}")
                    print(f"     Duration: {duration} seconds")
            
            return filename
        else:
            print("No attendance reports found in the response")
            return None
    else:
        print("✗ Could not retrieve attendance report")
        print("\nPossible reasons:")
        print("  1. The meeting hasn't ended yet (attendance reports are only available after the meeting)")
        print("  2. You don't have permission to access this meeting's attendance")
        print("  3. The meeting ID format might be incorrect")
        return None

def main():
    """Main entry point."""
    # Example HTML email body (generic example - replace with your actual email HTML)
    example_html = """<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
Dear User, You have been invited to a Microsoft Teams meeting. Please join using the link below.
<br>
<div class="me-email-text" lang="en-US" style="max-width:1024px; color:#242424; font-family:'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif">
<div aria-hidden="true" style="margin-bottom:24px; overflow:hidden; white-space:nowrap">
________________________________________________________________________________</div>
<div style="margin-bottom:12px"><span class="me-email-text" style="font-size:24px; font-weight:700; margin-right:12px">Microsoft Teams</span>
<a href="https://aka.ms/JoinTeamsMeeting?omkt=en-US" id="meet_invite_block.action.help" class="me-email-link" style="font-size:14px; text-decoration:underline; color:#5B5FC7">
Need help?</a> </div>
<div style="margin-bottom:6px"><a href="https://teams.microsoft.com/l/meetup-join/19%3ameeting_EXAMPLE_MEETING_ID%40thread.v2/0?context=%7b%22Tid%22%3a%22YOUR_TENANT_ID%22%2c%22Oid%22%3a%22YOUR_ORGANIZER_ID%22%7d" id="meet_invite_block.action.join_link" title="Meeting join link" class="me-email-headline" style="font-size:20px; font-weight:600; text-decoration:underline; color:#5B5FC7">Join
 the meeting now</a> </div>
<div style="margin-bottom:6px"><span class="me-email-text-secondary" style="font-size:14px; color:#616161">Meeting ID:
</span><span class="me-email-text" style="font-size:14px; color:#242424">123 456 789 012 34</span>
</div>
<div style="margin-bottom:32px"><span class="me-email-text-secondary" style="font-size:14px; color:#616161">Passcode:
</span><span class="me-email-text" style="font-size:14px; color:#242424">EXAMPLE</span>
</div>
<div style="margin-bottom:12px; max-width:1024px">
<hr style="border:0; background:#616161; height:1px">
</div>
<div><span class="me-email-text-secondary" style="font-size:14px; color:#616161">For organizers:
</span><a href="https://teams.microsoft.com/meetingOptions/?organizerId=YOUR_ORGANIZER_ID&amp;tenantId=YOUR_TENANT_ID&amp;threadId=19_meeting_EXAMPLE_MEETING_ID@thread.v2&amp;messageId=0&amp;language=en-US" id="meet_invite_block.action.organizer_meet_options" class="me-email-link" style="font-size:14px; text-decoration:underline; color:#5B5FC7">Meeting
 options</a> </div>
<div style="margin-top:24px; margin-bottom:6px"></div>
<div style="margin-bottom:24px"></div>
<div aria-hidden="true" style="margin-bottom:24px; overflow:hidden; white-space:nowrap">
________________________________________________________________________________</div>
</div>
</body>
</html>"""
    
    print("Microsoft Teams Attendance Report Extractor")
    print("=" * 60)
    
    # Check if user wants to use example or provide their own HTML
    use_example = input("\nUse example HTML? (y/n): ").strip().lower()
    
    if use_example == 'y':
        html_body = example_html
    else:
        print("\nPaste the HTML email body (press Ctrl+D or Ctrl+Z when done):")
        html_body = ""
        try:
            while True:
                line = input()
                html_body += line + "\n"
        except EOFError:
            pass
    
    # Choose authentication method
    auth_method = input("\nAuthentication method:\n1. Password (Resource Owner Password Credentials)\n2. OAuth Code Flow\nChoice (1/2): ").strip()
    use_password_auth = (auth_method == '1')
    
    # Process the email
    result = process_email_html(html_body, use_password_auth=use_password_auth)
    
    if result:
        print(f"\n✓ Success! Report saved to: {result}")
    else:
        print("\n✗ Failed to extract attendance report")

if __name__ == "__main__":
    main()

