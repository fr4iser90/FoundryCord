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
    'gameservers': {
        'dashboard_type': 'gameservers',
        'auto_create': True,
        'refresh_interval': 60
    },
}

DASHBOARD_SERVICES = {
    'welcome': 'WelcomeDashboardService',
    'project': 'ProjectDashboardService',
    'monitoring': 'MonitoringDashboardService',
    'gameservers': 'GameServerDashboardService',
}