import os
import streamlit as st
import requests
from datetime import datetime
import json

class TrelloIntegrationError(Exception):
    """Custom exception for Trello integration errors"""
    pass

class TrelloIntegration:
    def __init__(self, api_key=None, token=None):
        """
        Initialize Trello Integration with more robust error handling
        
        :param api_key: Trello API Key
        :param token: Trello Authorization Token
        """
        # Use environment variables or Streamlit secrets as fallback
        self.api_key = api_key or os.environ.get('TRELLO_API_KEY') or st.secrets.get("TRELLO_API_KEY")
        self.token = token or os.environ.get('TRELLO_TOKEN') or st.secrets.get("TRELLO_TOKEN")
        
        if not self.api_key or not self.token:
            raise TrelloIntegrationError("Trello API Key and Token are required. Please set them in environment variables or Streamlit secrets.")
    
    def _make_trello_request(self, endpoint, method='GET', params=None):
        """
        Make a request to Trello API with error handling
        
        :param endpoint: Trello API endpoint
        :param method: HTTP method
        :param params: Additional parameters
        :return: JSON response
        """
        base_url = "https://api.trello.com/1"
        full_url = f"{base_url}{endpoint}"
        
        # Prepare request parameters
        request_params = {
            'key': self.api_key,
            'token': self.token
        }
        if params:
            request_params.update(params)
        
        try:
            if method == 'GET':
                response = requests.get(full_url, params=request_params)
            elif method == 'POST':
                response = requests.post(full_url, params=request_params, json=params)
            else:
                raise TrelloIntegrationError(f"Unsupported HTTP method: {method}")
            
            # Raise an exception for bad responses
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            st.error(f"Trello API Request Failed: {e}")
            raise TrelloIntegrationError(f"API Request Error: {e}")
    
    def get_boards(self):
        """
        Retrieve all accessible Trello boards
        
        :return: List of board names and IDs
        """
        try:
            boards = self._make_trello_request('/members/me/boards', params={'filter': 'all'})
            return [{"name": board['name'], "id": board['id']} for board in boards]
        except Exception as e:
            st.error(f"Failed to retrieve Trello boards: {e}")
            return []
    
    def get_board_lists(self, board_id):
        """
        Get lists from a specific Trello board
        
        :param board_id: Trello board ID
        :return: List of list names and IDs
        """
        try:
            lists = self._make_trello_request(f'/boards/{board_id}/lists')
            return [{"name": lst['name'], "id": lst['id']} for lst in lists]
        except Exception as e:
            st.error(f"Failed to retrieve lists for board {board_id}: {e}")
            return []
    
    def get_cards_from_list(self, list_id):
        """
        Retrieve cards from a specific Trello list
        
        :param list_id: Trello list ID
        :return: List of card details
        """
        try:
            cards = self._make_trello_request(f'/lists/{list_id}/cards')
            return [
                {
                    "name": card['name'], 
                    "desc": card.get('desc', ''), 
                    "id": card['id'],
                    "due_date": card.get('due'),
                    "complexity": self._extract_complexity(card.get('desc', ''))
                } 
                for card in cards
            ]
        except Exception as e:
            st.error(f"Failed to retrieve cards from list {list_id}: {e}")
            return []
    
    def _extract_complexity(self, description):
        """
        Extract task complexity from card description
        
        :param description: Card description
        :return: Complexity level
        """
        description = description.lower()
        if "hard" in description:
            return "hard"
        elif "medium" in description:
            return "medium"
        return "easy"
    
    def create_burndown_card(self, board_id, list_id, task_name, estimated_points, complexity):
        """
        Create a new card in Trello with burndown chart details
        
        :param board_id: Trello board ID
        :param list_id: Trello list ID
        :param task_name: Name of the task
        :param estimated_points: Estimated story points
        :param complexity: Task complexity
        :return: Created card details
        """
        description = f"""
        Burndown Chart Task Details:
        - Estimated Points: {estimated_points}
        - Complexity: {complexity}
        """
        
        try:
            card_data = {
                'name': task_name,
                'desc': description,
                'idList': list_id
            }
            card = self._make_trello_request('/cards', method='POST', params=card_data)
            
            return {
                "name": card['name'],
                "id": card['id'],
                "url": card['shortUrl']
            }
        except Exception as e:
            st.error(f"Failed to create Trello card: {e}")
            return None
    
    def update_card_progress(self, card_id, completed_points, status):
        """
        Update card progress in Trello
        
        :param card_id: Trello card ID
        :param completed_points: Points completed
        :param status: Current task status
        """
        try:
            # Fetch current card details
            card = self._make_trello_request(f'/cards/{card_id}')
            
            # Prepare updated description
            current_desc = card.get('desc', '')
            updated_desc = f"{current_desc}\n\nProgress Update:\n- Completed Points: {completed_points}\n- Status: {status}"
            
            # Update card description
            self._make_trello_request(f'/cards/{card_id}', method='PUT', params={'desc': updated_desc})
        except Exception as e:
            st.error(f"Failed to update Trello card progress: {e}")

def authenticate_trello():
    """
    Streamlit UI for Trello Authentication with improved error handling
    """
    st.sidebar.header("🔐 Trello Authentication")
    
    # Check for existing authentication
    if 'trello_integration' in st.session_state:
        return st.session_state.trello_integration
    
    # Input for API Key and Token
    api_key = st.sidebar.text_input("Trello API Key", type="password", key="trello_api_key")
    token = st.sidebar.text_input("Trello Token", type="password", key="trello_token")
    
    if st.sidebar.button("Connect to Trello"):
        try:
            # Attempt to create Trello integration
            trello_integration = TrelloIntegration(api_key, token)
            
            # Verify connection by fetching boards
            boards = trello_integration.get_boards()
            
            if not boards:
                st.sidebar.warning("Connected, but no boards found. Check your permissions.")
            else:
                st.sidebar.success("Successfully connected to Trello!")
                
                # Store credentials securely in session state
                st.session_state.trello_integration = trello_integration
                st.session_state.trello_boards = boards
            
            return trello_integration
        
        except TrelloIntegrationError as e:
            st.sidebar.error(f"Authentication failed: {e}")
            st.sidebar.info("Steps to resolve:\n1. Get API Key from trello.com/app-key\n2. Generate Token\n3. Ensure correct permissions")
        except Exception as e:
            st.sidebar.error(f"Unexpected error: {e}")
    
    return None

def main():
    """
    Example usage and testing of Trello Integration
    """
    st.title("Trello Burndown Chart Integration")
    
    # Authenticate with Trello
    trello_integration = authenticate_trello()
    
    if trello_integration and hasattr(st.session_state, 'trello_boards'):
        # Select Board
        board_id = st.selectbox(
            "Select Trello Board", 
            options=[board['id'] for board in st.session_state.trello_boards],
            format_func=lambda x: next(board['name'] for board in st.session_state.trello_boards if board['id'] == x)
        )
        
        # Get Lists in the Board
        lists = trello_integration.get_board_lists(board_id)
        list_id = st.selectbox(
            "Select List", 
            options=[lst['id'] for lst in lists],
            format_func=lambda x: next(lst['name'] for lst in lists if lst['id'] == x)
        )
        
        # Fetch and Display Cards
        cards = trello_integration.get_cards_from_list(list_id)
        st.write("Trello Cards:")
        st.dataframe(cards)

if __name__ == "__main__":
    main()
