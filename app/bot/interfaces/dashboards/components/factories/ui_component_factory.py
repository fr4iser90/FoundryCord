from typing import Dict, Any, Optional
from interfaces.dashboards.components.ui.table_builder import UnicodeTableBuilder
from interfaces.dashboards.components.ui.mini_graph import MiniGraph

class UIComponentFactory:
    """Factory for creating UI components following the factory pattern"""
    
    @staticmethod
    def create_table(title: Optional[str] = None, width: int = 40) -> UnicodeTableBuilder:
        """Creates a new UnicodeTableBuilder instance"""
        return UnicodeTableBuilder(title=title, width=width)
    
    @staticmethod
    def create_mini_graph(values: list, max_height: int = 8) -> str:
        """Creates a mini bar graph for visualization"""
        return MiniGraph.create_bar_graph(values, max_height)
    
    @staticmethod
    def create_spark_line(values: list, width: int = 20) -> str:
        """Creates a spark line visualization"""
        return MiniGraph.create_spark_line(values, width)
    
    @staticmethod
    def format_cpu_details(metrics: Dict[str, Any]) -> str:
        """Creates a formatted CPU details display"""
        cpu_table = UnicodeTableBuilder("CPU Details", width=50)
        cpu_table.add_header_row("Property", "Value")
        cpu_table.add_row("Model", metrics.get('cpu_model', 'Unknown'))
        cpu_table.add_row("Cores/Threads", f"{metrics.get('cpu_cores', '?')}/{metrics.get('cpu_threads', '?')}")
        cpu_table.add_row("Current Usage", f"{metrics.get('cpu_usage', 0)}%")
        cpu_table.add_row("Temperature", f"{metrics.get('cpu_temp', 0)}°C")
        
        return cpu_table.build()
    
    @staticmethod
    def format_memory_details(metrics: Dict[str, Any]) -> str:
        """Creates a formatted memory details display"""
        memory_table = UnicodeTableBuilder("Memory Details", width=45)
        memory_table.add_header_row("Property", "Value")
        memory_table.add_row("Used", f"{metrics.get('memory_used', 0)}%")
        memory_table.add_row("Total", f"{metrics.get('memory_total', 0)} GB")
        
        # Add swap if available
        if 'swap_used' in metrics and 'swap_total' in metrics:
            memory_table.add_divider()
            memory_table.add_row("Swap Used", f"{metrics.get('swap_used', 0)} GB")
            memory_table.add_row("Swap Total", f"{metrics.get('swap_total', 0)} GB")
            memory_table.add_row("Swap Percent", f"{metrics.get('swap_percent', 0)}%")
        
        return memory_table.build()
