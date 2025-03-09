from typing import List, Optional

class MiniGraph:
    """Helper for creating small Unicode block-based graphs for Discord"""
    
    @staticmethod
    def create_bar_graph(values: List[float], max_height: int = 8) -> str:
        """Creates a mini bar graph using Unicode block characters
        Example: [10, 30, 20, 50, 40] -> '▁▃▂▆▄'"""
        if not values:
            return "No data"
        
        max_value = max(values) if max(values) > 0 else 1
        normalized = [int((v / max_value) * max_height) for v in values]
        
        # Unicode block elements from lowest to highest
        blocks = " ▁▂▃▄▅▆▇█"
        return ''.join(blocks[min(n, max_height)] for n in normalized)
    
    @staticmethod
    def create_spark_line(values: List[float], width: int = 20) -> str:
        """Creates a spark line visualization of data"""
        if not values:
            return "No data"
            
        # If we have more values than width, downsample
        if len(values) > width:
            # Simple downsampling by averaging groups
            group_size = len(values) // width
            downsampled = []
            for i in range(0, width):
                start = i * group_size
                end = start + group_size
                group = values[start:end]
                downsampled.append(sum(group) / len(group))
            values = downsampled
            
        # If we have fewer values than width, pad with None
        elif len(values) < width:
            values = values + [None] * (width - len(values))
            
        # Create the spark line
        return MiniGraph.create_bar_graph(values)
