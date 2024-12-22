import os
import streamlit as st
from trello import TrelloClient
from datetime import datetime
import requests

class TrelloIntegration:
    def __init__(self, api_key=None, token=None):
        """
        Initialize Trello Integration
        
        :param api_key: Trello API Key
        :param token: Trello Authorization Token
        """
        self.api_key = api_key or st.secrets.get("TRELLO_API_KEY")
        self.token = token or st.secrets.get("TRELLO_TOKEN")
        
        if not self.api_key or not self.token:
            raise ValueError("Trello API Key and Token are required")
        
        self.client = TrelloClient(
            api_key=self.api_key,
            token=self.token
        )
    
    def get_boards(self):
        """
        Retrieve all accessible Trello boards
        
        :return: List of board names and IDs
        """
        boards = self.client.list_boards()
        return [{"name": board.name, "id": board.id} for board in boards]
    
    def get_board_lists(self, board_id):
        """
        Get lists from a specific Trello board
        
        :param board_id: Trello board ID
        :return: List of list names and IDs
        """
        board = self.client.get_board(board_id)
        return [{"name": lst.name, "id": lst.id} for lst in board.list_lists()]
    
    def get_cards_from_list(self, list_id):
        """
        Retrieve cards from a specific Trello list
        
        :param list_id: Trello list ID
        :return: List of card details
        """
        trello_list = self.client.get_list(list_id)
        return [
            {
                "name": card.name, 
                "desc": card.desc, 
                "id": card.id,
                "due_date": card.due_date,
                "complexity": self._extract_complexity(card.desc)
            } 
            for card in trello_list.list_cards()
        ]
    
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
        
        board = self.client.get_board(board_id)
        trello_list = board.get_list(list_id)
        
        card = trello_list.add_card(
            name=task_name, 
            desc=description
        )
        
        return {
            "name": card.name,
            "id": card.id,
            "url": card.url
        }
    
    def update_card_progress(self, card_id, completed_points, status):
        """
        Update card progress in Trello
        
        :param card_id: Trello card ID
        :param completed_points: Points completed
        :param status: Current task status
        """
        card = self.client.get_card(card_id)
        
        # Update card description with progress
        current_desc = card.desc
        updated_desc = f"{current_desc}\n\nProgress Update:\n- Completed Points: {completed_points}\n- Status: {status}"
        
        card.set_description(updated_desc)
        
        # Optionally move card based on status
        if status == "Completed":
            # Move to "Done" list (you might want to customize this)
            done_lists = [lst for lst in self.client.get_board(card.board_id).list_lists() if lst.name.lower() == "done"]
            if done_lists:
                card.change_list(done_lists[0].id)

def authenticate_trello():
    """
    Streamlit UI for Trello Authentication
    """
    st.sidebar.header("🔐 Trello Authentication")
    
    # Input for API Key and Token
    api_key = st.sidebar.text_input("Trello API Key", type="password")
    token = st.sidebar.text_input("Trello Token", type="password")
    
    if st.sidebar.button("Connect to Trello"):
        try:
            trello_integration = TrelloIntegration(api_key, token)
            boards = trello_integration.get_boards()
            
            st.sidebar.success("Successfully connected to Trello!")
            
            # Store credentials securely
            st.session_state.trello_api_key = api_key
            st.session_state.trello_token = token
            st.session_state.trello_boards = boards
            
            return trello_integration
        except Exception as e:
            st.sidebar.error(f"Authentication failed: {e}")
            return None

def main():
    """
    Example usage and testing of Trello Integration
    """
    st.title("Trello Burndown Chart Integration")
    
    # Authenticate with Trello
    trello_integration = authenticate_trello()
    
    if trello_integration:
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
