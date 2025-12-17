"""HTML email parser to extract Microsoft Teams meeting information."""
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional

class EmailParser:
    """Parses HTML emails to extract Microsoft Teams meeting information."""
    
    @staticmethod
    def extract_meeting_info(html_body: str) -> Dict[str, Optional[str]]:
        """
        Extract meeting information from HTML email body.
        
        Returns:
            Dictionary containing:
            - meeting_id: Teams meeting ID
            - passcode: Meeting passcode
            - join_link: Meeting join URL
            - thread_id: Meeting thread ID (from join link)
            - organizer_id: Organizer ID (from join link)
            - tenant_id: Tenant ID (from join link)
        """
        soup = BeautifulSoup(html_body, 'html.parser')
        
        meeting_info = {
            'meeting_id': None,
            'passcode': None,
            'join_link': None,
            'thread_id': None,
            'organizer_id': None,
            'tenant_id': None
        }
        
        # Extract Meeting ID
        meeting_id_elem = soup.find('span', string=re.compile(r'Meeting ID:'))
        if meeting_id_elem:
            meeting_id_text = meeting_id_elem.find_next_sibling('span')
            if meeting_id_text:
                meeting_info['meeting_id'] = meeting_id_text.get_text(strip=True).replace(' ', '')
        
        # Extract Passcode
        passcode_elem = soup.find('span', string=re.compile(r'Passcode:'))
        if passcode_elem:
            passcode_text = passcode_elem.find_next_sibling('span')
            if passcode_text:
                meeting_info['passcode'] = passcode_text.get_text(strip=True)
        
        # Extract Join Link
        join_link_elem = soup.find('a', id='meet_invite_block.action.join_link')
        if join_link_elem:
            meeting_info['join_link'] = join_link_elem.get('href', '')
            
            # Parse join link to extract IDs
            join_link = meeting_info['join_link']
            
            # Extract thread_id (meeting ID from URL)
            thread_match = re.search(r'19%3ameeting_([^%]+)', join_link)
            if thread_match:
                meeting_info['thread_id'] = f"19:meeting_{thread_match.group(1)}"
            
            # Extract tenant_id and organizer_id from context
            context_match = re.search(r'context=%7b%22Tid%22%3a%22([^"]+)%22', join_link)
            if context_match:
                meeting_info['tenant_id'] = context_match.group(1)
            
            oid_match = re.search(r'%22Oid%22%3a%22([^"]+)%22', join_link)
            if oid_match:
                meeting_info['organizer_id'] = oid_match.group(1)
        
        return meeting_info
    
    @staticmethod
    def extract_meeting_id_from_url(join_url: str) -> Optional[str]:
        """
        Extract the online meeting ID from a Teams join URL.
        This is needed for Graph API calls.
        """
        # Decode URL-encoded string
        import urllib.parse
        decoded = urllib.parse.unquote(join_url)
        
        # Extract meeting ID pattern: 19:meeting_...
        match = re.search(r'19:meeting_([^@]+)', decoded)
        if match:
            return f"19:meeting_{match.group(1)}"
        
        return None

