from typing import List, Dict, Any, Optional, Union

class UnicodeTableBuilder:
    """Helper for creating Discord-friendly tables with Unicode box characters"""
    
    def __init__(self, title: Optional[str] = None, width: int = 60):
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
        
        # Calculate column widths based on content
        column_widths = self._calculate_column_widths()
        
        # Create the horizontal divider lines with proper characters
        top_segments = ['─' * (width + 2) for width in column_widths]
        top_line = '┌' + '┬'.join(top_segments) + '┐'
        
        mid_segments = ['─' * (width + 2) for width in column_widths]
        mid_line = '├' + '┼'.join(mid_segments) + '┤'
        
        bottom_segments = ['─' * (width + 2) for width in column_widths]
        bottom_line = '└' + '┴'.join(bottom_segments) + '┘'
        
        # Title bar if provided
        if self.title:
            # Center the title in the available width
            total_width = sum(column_widths) + (3 * len(column_widths)) - 1
            title_padding_left = (total_width - len(self.title) - 2) // 2
            title_padding_right = total_width - len(self.title) - 2 - title_padding_left
            result.append(f"┌{'─' * title_padding_left} {self.title} {'─' * title_padding_right}┐")
        else:
            result.append(top_line)
        
        # Process rows
        for i, row in enumerate(self.rows):
            if row["type"] == "divider":
                result.append(mid_line)
            elif row["type"] == "header" or row["type"] == "row":
                # Format cells with proper spacing based on calculated widths
                formatted_cells = []
                for idx, cell in enumerate(row["cells"]):
                    cell_text = str(cell)
                    if idx < len(column_widths):
                        cell_width = column_widths[idx]
                        # Truncate if necessary and add ellipsis
                        if len(cell_text) > cell_width:
                            cell_text = cell_text[:cell_width-1] + "…"
                        # Left-align the cell content within its allocated width
                        formatted_cells.append(cell_text.ljust(cell_width))
                    else:
                        formatted_cells.append(cell_text)
                
                # Add the row with proper border and column separators
                result.append(f"│ {' │ '.join(formatted_cells)} │")
                
                # Add a divider after header
                if row["type"] == "header":
                    result.append(mid_line)
        
        # Close the table
        result.append(bottom_line)
        
        return "```\n" + "\n".join(result) + "\n```"
    
    def _calculate_column_widths(self):
        """Calculate optimal width for each column"""
        # Find the maximum number of columns in any row
        max_columns = 0
        for row in self.rows:
            if row["type"] in ["header", "row"]:
                max_columns = max(max_columns, len(row["cells"]))
        
        # Initialize column widths with zeros
        widths = [0] * max_columns
        
        # Calculate the maximum width needed for each column
        for row in self.rows:
            if row["type"] in ["header", "row"]:
                for i, cell in enumerate(row["cells"]):
                    if i < max_columns:
                        widths[i] = max(widths[i], min(len(str(cell)), 30))  # Cap at 30 to prevent excessive width
        
        # Calculate available space after accounting for borders and separators
        # Border characters: 4 (│ at start, │ at end with spaces)
        # Column separators: 3 * (max_columns - 1)
        separators_width = 3 * (max_columns - 1) if max_columns > 1 else 0
        border_width = 4
        fixed_width = border_width + separators_width
        available_width = self.width - fixed_width
        
        # Distribute minimum width to all columns
        min_width = 3
        total_min_width = min_width * max_columns
        
        if available_width < total_min_width:
            # Table is too narrow, set all columns to minimum
            return [min_width] * max_columns
        
        # Calculate initial column distribution
        total_content_width = sum(widths)
        
        if total_content_width <= available_width:
            # We have enough space, distribute extra space proportionally
            extra_space = available_width - total_content_width
            if extra_space > 0 and max_columns > 0 and total_content_width > 0:
                for i in range(max_columns):
                    widths[i] += int((widths[i] / total_content_width) * extra_space)
        else:
            # Scale down columns, ensuring minimum width
            scale_factor = available_width / total_content_width
            for i in range(max_columns):
                widths[i] = max(min_width, int(widths[i] * scale_factor))
        
        return widths