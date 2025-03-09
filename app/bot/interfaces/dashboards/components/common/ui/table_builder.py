from typing import List, Dict, Any, Optional, Union

class UnicodeTableBuilder:
    """Helper for creating Discord-friendly tables with Unicode box characters"""
    
    def __init__(self, title: Optional[str] = None, width: int = 40):
        self.rows = []
        self.title = title
        self.width = width
    
    def add_header_row(self, *cells):
        """Add a header row with multiple cells"""
        self.rows.append({"type": "header", "cells": cells})
        return self
    
    def add_row(self, *cells):
        """Add a standard row with multiple cells"""
        self.rows.append({"type": "row", "cells": cells})
        return self
    
    def add_divider(self):
        """Add a divider row"""
        self.rows.append({"type": "divider"})
        return self
    
    def build(self):
        """Build the table string"""
        result = []
        
        # Title bar if provided
        if self.title:
            title_padding = (self.width - len(self.title) - 2) // 2
            result.append(f"┌{'─' * title_padding} {self.title} {'─' * title_padding}┐")
        else:
            result.append(f"┌{'─' * self.width}┐")
        
        # Process rows
        for i, row in enumerate(self.rows):
            if row["type"] == "divider":
                result.append(f"├{'─' * self.width}┤")
            elif row["type"] == "header":
                content = " │ ".join(str(cell) for cell in row["cells"])
                result.append(f"│ {content:{self.width-4}} │")
                result.append(f"├{'─' * self.width}┤")
            else:
                content = " │ ".join(str(cell) for cell in row["cells"])
                result.append(f"│ {content:{self.width-4}} │")
        
        # Close the table
        result.append(f"└{'─' * self.width}┘")
        
        return "```\n" + "\n".join(result) + "\n```"
