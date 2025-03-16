# Main web server application

class MockApp:
    """Mock application class for testing"""
    def __init__(self):
        self.routes = []
        
    def add_route(self, route):
        self.routes.append(route)

# Create app instance for tests to import
app = MockApp() 