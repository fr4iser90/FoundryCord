import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.bot.interfaces.web.server import app
from app.bot.interfaces.web.models.user import User
from app.bot.interfaces.web.models.database import Dashboard, DashboardComponent
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id="123456789",
        username="test_user",
        email="test@example.com",
        avatar_url="avatar_hash",
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )

@pytest.fixture
def mock_dashboard():
    return Dashboard(
        id=1,
        title="Test Dashboard",
        description="This is a test dashboard",
        dashboard_type="system",
        layout="{}",
        is_public=False,
        user_id="123456789",
        server_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

@pytest.fixture
def mock_components():
    return [
        DashboardComponent(
            id=1,
            title="CPU Usage",
            component_type="chart",
            grid_col=1,
            grid_row=1,
            grid_col_span=6,
            grid_row_span=4,
            data_source="system_cpu",
            config="{\"chart_type\": \"line\"}",
            dashboard_id=1
        ),
        DashboardComponent(
            id=2,
            title="Memory Usage",
            component_type="chart",
            grid_col=7,
            grid_row=1,
            grid_col_span=6,
            grid_row_span=4,
            data_source="system_memory",
            config="{\"chart_type\": \"pie\"}",
            dashboard_id=1
        )
    ]

@pytest.fixture
def mock_auth_dependency():
    with patch('interfaces.web.routes.dashboard.get_current_user') as mock:
        mock.return_value = User(
            id="123456789",
            username="test_user",
            email="test@example.com"
        )
        yield mock

@pytest.fixture
def mock_dashboard_service():
    with patch('interfaces.web.routes.dashboard.DashboardService') as MockDashboardService:
        dashboard_service_instance = MockDashboardService.return_value
        dashboard_service_instance.get_dashboards_by_user.return_value = [
            Dashboard(
                id=1,
                title="Test Dashboard",
                description="This is a test dashboard",
                dashboard_type="system",
                layout="{}",
                is_public=False,
                user_id="123456789",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        dashboard_service_instance.get_dashboard_by_id.return_value = Dashboard(
            id=1,
            title="Test Dashboard",
            description="This is a test dashboard",
            dashboard_type="system",
            layout="{}",
            is_public=False,
            user_id="123456789",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        dashboard_service_instance.create_dashboard.return_value = Dashboard(
            id=2,
            title="New Dashboard",
            description="This is a new dashboard",
            dashboard_type="custom",
            layout="{}",
            is_public=True,
            user_id="123456789",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        dashboard_service_instance.get_dashboard_components.return_value = [
            DashboardComponent(
                id=1,
                title="CPU Usage",
                component_type="chart",
                grid_col=1,
                grid_row=1,
                grid_col_span=6,
                grid_row_span=4,
                data_source="system_cpu",
                config="{\"chart_type\": \"line\"}",
                dashboard_id=1
            )
        ]
        dashboard_service_instance.update_dashboard.return_value = True
        dashboard_service_instance.delete_dashboard.return_value = True
        yield dashboard_service_instance

@pytest.fixture
def mock_db():
    with patch('interfaces.web.routes.dashboard.get_db') as mock:
        yield mock

# Test listing dashboards
def test_list_dashboards(mock_auth_dependency, mock_dashboard_service, mock_db):
    with patch('interfaces.web.routes.dashboard.templates') as mock_templates:
        mock_templates.TemplateResponse.return_value = {}
        response = client.get("/dashboard")
        assert response.status_code == 200
        mock_dashboard_service.get_dashboards_by_user.assert_called_once_with("123456789")
        mock_templates.TemplateResponse.assert_called_once()

# Test viewing a dashboard
def test_view_dashboard(mock_auth_dependency, mock_dashboard_service, mock_db):
    with patch('interfaces.web.routes.dashboard.templates') as mock_templates:
        mock_templates.TemplateResponse.return_value = {}
        response = client.get("/dashboard/1")
        assert response.status_code == 200
        mock_dashboard_service.get_dashboard_by_id.assert_called_once_with(1)
        mock_dashboard_service.get_dashboard_components.assert_called_once_with(1)
        mock_templates.TemplateResponse.assert_called_once()

# Test creating a dashboard form
def test_create_dashboard_form(mock_auth_dependency):
    with patch('interfaces.web.routes.dashboard.templates') as mock_templates:
        mock_templates.TemplateResponse.return_value = {}
        response = client.get("/dashboard/create")
        assert response.status_code == 200
        mock_templates.TemplateResponse.assert_called_once()

# Test creating a dashboard
def test_create_dashboard(mock_auth_dependency, mock_dashboard_service, mock_db):
    data = {
        "title": "New Dashboard",
        "description": "This is a new dashboard",
        "dashboard_type": "custom",
        "is_public": "on"
    }
    response = client.post("/dashboard/create", data=data, allow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard/2"
    mock_dashboard_service.create_dashboard.assert_called_once() 