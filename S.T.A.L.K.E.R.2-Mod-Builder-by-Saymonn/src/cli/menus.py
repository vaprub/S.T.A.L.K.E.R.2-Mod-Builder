"""Menu system for CLI interface"""

import os
from typing import List

class MenuSystem:
    """Handles menu display and selection"""
    
    @staticmethod
    def clear_screen():
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self, title: str, options: List[str], clear: bool = True) -> str:
        """Display a menu and get user selection"""
        if clear:
            self.clear_screen()
        
        print("=" * 50)
        print(f"    {title}")
        print("=" * 50)
        print()
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        print()
        choice = input(f"Select option (1-{len(options)}): ").strip()
        
        return choice
    
    def show_submenu(self, title: str, items: List[tuple], clear: bool = True) -> str:
        """Display a submenu with detailed items"""
        if clear:
            self.clear_screen()
        
        print("=" * 50)
        print(f"    {title}")
        print("=" * 50)
        print()
        
        for i, (name, description) in enumerate(items, 1):
            print(f"{i}. {name}")
            if description:
                print(f"   {description}")
            print()
        
        print("0. Back")
        print()
        
        choice = input(f"Select option (0-{len(items)}): ").strip()
        
        return choice