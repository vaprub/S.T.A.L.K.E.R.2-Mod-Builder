"""User input prompts and validation"""

from typing import Optional

class UserPrompts:
    """Handles user input prompts"""
    
    @staticmethod
    def confirm(message: str) -> bool:
        """Get yes/no confirmation from user"""
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    @staticmethod
    def get_string(prompt: str, allow_empty: bool = True) -> Optional[str]:
        """Get string input from user"""
        value = input(prompt).strip()
        
        if not value and not allow_empty:
            print("Value cannot be empty")
            return None
        
        return value if value else None
    
    @staticmethod
    def get_integer(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
        """Get integer input from user with validation"""
        try:
            value = int(input(prompt).strip())
            
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                return None
            
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                return None
            
            return value
            
        except ValueError:
            print("Please enter a valid number")
            return None
    
    @staticmethod
    def get_float(prompt: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[float]:
        """Get float input from user with validation"""
        try:
            value = float(input(prompt).strip())
            
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                return None
            
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                return None
            
            return value
            
        except ValueError:
            print("Please enter a valid number")
            return None
    
    @staticmethod
    def show_message(message: str, wait: bool = True):
        """Display a message to user"""
        print(message)
        if wait:
            input("Press Enter to continue...")
    
    @staticmethod
    def show_error(message: str, wait: bool = True):
        """Display an error message"""
        print(f"❌ Error: {message}")
        if wait:
            input("Press Enter to continue...")
    
    @staticmethod
    def show_success(message: str, wait: bool = True):
        """Display a success message"""
        print(f"✓ Success: {message}")
        if wait:
            input("Press Enter to continue...")
    
    @staticmethod
    def show_warning(message: str, wait: bool = True):
        """Display a warning message"""
        print(f"⚠ Warning: {message}")
        if wait:
            input("Press Enter to continue...")