class Alert:
    def __init__(self, metric, message, severity, timestamp=None):
        self.metric = metric
        self.message = message
        self.severity = severity  # e.g., "warning", "critical"
        self.timestamp = timestamp or datetime.now()
        self.acknowledged = False