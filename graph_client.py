"""Microsoft Graph API client for fetching attendance reports."""
import requests
from typing import Dict, List, Optional
from auth import GraphAuth

class GraphClient:
    """Client for interacting with Microsoft Graph API."""
    
    def __init__(self, auth: GraphAuth):
        self.auth = auth
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {self.auth.get_access_token()}',
            'Content-Type': 'application/json'
        }
    
    def _refresh_headers(self):
        """Refresh headers with current access token."""
        self.headers['Authorization'] = f'Bearer {self.auth.get_access_token()}'
    
    def get_online_meeting_attendance_report(self, meeting_id: str) -> Optional[Dict]:
        """
        Get attendance report for an online meeting.
        
        Args:
            meeting_id: The online meeting ID (e.g., "19:meeting_...")
        
        Returns:
            Attendance report data or None if not found
        """
        self._refresh_headers()
        
        # The endpoint format is: /me/onlineMeetings/{meeting-id}/attendanceReports
        # But we need to get the meeting first, then attendance reports
        
        try:
            # First, try to get the meeting by ID
            url = f"{self.base_url}/me/onlineMeetings/{meeting_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                # Try alternative endpoint format
                url = f"{self.base_url}/me/onlineMeetings('{meeting_id}')"
                response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                meeting_data = response.json()
                
                # Now get attendance reports
                attendance_url = f"{self.base_url}/me/onlineMeetings/{meeting_id}/attendanceReports"
                attendance_response = requests.get(attendance_url, headers=self.headers)
                
                if attendance_response.status_code == 200:
                    return attendance_response.json()
                elif attendance_response.status_code == 404:
                    print(f"No attendance reports found for meeting {meeting_id}")
                    return None
                else:
                    print(f"Error fetching attendance: {attendance_response.status_code}")
                    print(attendance_response.text)
                    return None
            else:
                print(f"Error fetching meeting: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"Exception while fetching attendance report: {str(e)}")
            return None
    
    def get_meeting_attendance_records(self, meeting_id: str, report_id: str) -> Optional[List[Dict]]:
        """
        Get attendance records for a specific attendance report.
        
        Args:
            meeting_id: The online meeting ID
            report_id: The attendance report ID
        
        Returns:
            List of attendance records
        """
        self._refresh_headers()
        
        try:
            url = f"{self.base_url}/me/onlineMeetings/{meeting_id}/attendanceReports/{report_id}/attendanceRecords"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('value', [])
            else:
                print(f"Error fetching attendance records: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"Exception while fetching attendance records: {str(e)}")
            return None
    
    def list_online_meetings(self, filter_query: Optional[str] = None) -> Optional[List[Dict]]:
        """
        List online meetings for the authenticated user.
        
        Args:
            filter_query: Optional OData filter query (e.g., "startDateTime ge 2024-01-01T00:00:00Z")
        
        Returns:
            List of online meetings
        """
        self._refresh_headers()
        
        try:
            url = f"{self.base_url}/me/onlineMeetings"
            params = {}
            if filter_query:
                params['$filter'] = filter_query
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('value', [])
            else:
                print(f"Error listing meetings: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"Exception while listing meetings: {str(e)}")
            return None

