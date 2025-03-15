from typing import Dict, Any, Optional
from app.bot.infrastructure.factories.base.base_factory import BaseFactory
from app.bot.interfaces.dashboards.components.ui.table_builder import UnicodeTableBuilder
from app.bot.interfaces.dashboards.components.ui.mini_graph import MiniGraph

class UIComponentFactory(BaseFactory):
    """Factory for creating UI components following the factory pattern"""
    
    def __init__(self, bot):
        super().__init__(bot)
    
    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        component_type = kwargs.get('component_type', 'table')
        
        if component_type == 'table':
            component = self.create_table(
                title=kwargs.get('title'),
                width=kwargs.get('width', 40)
            )
        elif component_type == 'mini_graph':
            component = self.create_mini_graph(
                values=kwargs.get('values', []),
                max_height=kwargs.get('max_height', 8)
            )
        elif component_type == 'spark_line':
            component = self.create_spark_line(
                values=kwargs.get('values', []),
                width=kwargs.get('width', 20)
            )
        else:
            raise ValueError(f"Unknown UI component type: {component_type}")
            
        return {
            'name': name,
            'component': component,
            'type': 'ui_component',
            'config': kwargs
        }
    
    def create_table(self, title: Optional[str] = None, width: int = 40) -> UnicodeTableBuilder:
        """Creates a new UnicodeTableBuilder instance"""
        return UnicodeTableBuilder(title=title, width=width)
    
    def create_mini_graph(self, values: list, max_height: int = 8) -> str:
        """Creates a mini bar graph for visualization"""
        return MiniGraph.create_bar_graph(values, max_height)
    
    def create_spark_line(self, values: list, width: int = 20) -> str:
        """Creates a spark line visualization"""
        return MiniGraph.create_spark_line(values, width)
    
    def format_cpu_details(self, metrics: Dict[str, Any]) -> str:
        """Creates a formatted CPU details display"""
        cpu_table = UnicodeTableBuilder("CPU Details", width=50)
        cpu_table.add_header_row("Property", "Value")
        cpu_table.add_row("Model", metrics.get('cpu_model', 'Unknown'))
        cpu_table.add_row("Cores/Threads", f"{metrics.get('cpu_cores', '?')}/{metrics.get('cpu_threads', '?')}")
        cpu_table.add_row("Current Usage", f"{metrics.get('cpu_usage', 0)}%")
        cpu_table.add_row("Temperature", f"{metrics.get('cpu_temp', 0)}°C")
        
        return cpu_table.build()
    
    def format_memory_details(self, metrics: Dict[str, Any]) -> str:
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
