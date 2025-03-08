DASHBOARD_MAPPINGS = {
    'welcome': {
        'dashboard_type': 'welcome',
        'auto_create': True,
        'refresh_interval': 300
    },
    'projects': {
        'dashboard_type': 'project',
        'auto_create': True,
        'refresh_interval': 300
    },
    'monitoring': {
        'dashboard_type': 'monitoring',
        'auto_create': True,
        'refresh_interval': 60
    },
    'general': {
        'dashboard_type': 'general',
        'auto_create': True,
        'refresh_interval': 300
    }
}

DASHBOARD_SERVICES = {
    'welcome': 'WelcomeDashboardService',
    'project': 'ProjectDashboardService',
    'monitoring': 'MonitoringDashboardService',
}
