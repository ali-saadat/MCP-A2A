import os
import json
import uuid
from pathlib import Path

class PersistenceManager:
    """
    Manages persistence of data between Streamlit sessions
    """
    
    def __init__(self, storage_dir):
        """
        Initialize the persistence manager
        
        Args:
            storage_dir (str): Directory to store persistence files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def get_user_data_path(self, session_id):
        """
        Get the path to the user data file
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            Path: Path to the user data file
        """
        return self.storage_dir / f"user_data_{session_id}.json"
    
    def save_user_data(self, session_id, data):
        """
        Save user data to persistent storage
        
        Args:
            session_id (str): Unique session identifier
            data (dict): User data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self.get_user_data_path(session_id)
            with open(file_path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    def load_user_data(self, session_id):
        """
        Load user data from persistent storage
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            dict: User data if found, empty dict otherwise
        """
        file_path = self.get_user_data_path(session_id)
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading user data: {e}")
                return {}
        return {}
    
    def get_or_create_session_id(self, existing_session_id=None):
        """
        Get existing session ID or create a new one
        
        Args:
            existing_session_id (str, optional): Existing session ID
            
        Returns:
            str: Session ID (existing or new)
        """
        if existing_session_id:
            # Check if session data exists
            file_path = self.get_user_data_path(existing_session_id)
            if file_path.exists():
                return existing_session_id
                
        # Create new session ID
        return str(uuid.uuid4())
    
    def get_all_sessions(self):
        """
        Get all session IDs
        
        Returns:
            list: List of session IDs
        """
        sessions = []
        for file in self.storage_dir.glob("user_data_*.json"):
            session_id = file.stem.replace("user_data_", "")
            sessions.append(session_id)
        return sessions
    
    def delete_session(self, session_id):
        """
        Delete a session
        
        Args:
            session_id (str): Session ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self.get_user_data_path(session_id)
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
