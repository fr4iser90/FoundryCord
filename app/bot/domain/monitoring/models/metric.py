class Metric:
    def __init__(self, name, value, unit=None, timestamp=None, metadata=None):
        self.name = name
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def is_critical(self, threshold):
        """Check if metric exceeds critical threshold"""
        # Implementation depends on the metric type
        return False