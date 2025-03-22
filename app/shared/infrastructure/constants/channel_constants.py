CHANNELS = {
    # Allgemeine Channels
    'welcome': {
        'name': 'welcome',
        'topic': 'Welcome Information',
        'is_private': False
        },
    'gamehub': {
        'name': 'gamehub',
        'topic': 'Gameserver Overview',
        'is_private': False,
        'threads': [
            {'name': 'status-overview', 'is_private': False},
            {'name': 'announcements', 'is_private': False}
            ]
        },
    'services': {
        'name': 'services',
        'topic': 'Service Overview',
        'is_private': True,
        'threads': [
            {'name': 'status', 'is_private': True},
            {'name': 'maintenance', 'is_private': True}
            ]
        },
    'infrastructure': {
        'name': 'infrastructure',
        'topic': 'Infrastructure Management',
        'is_private': True,
        'threads': [
            {'name': 'network', 'is_private': True},
            {'name': 'hardware', 'is_private': True},
            {'name': 'updates', 'is_private': True}
            ]
        },
    'projects': {
        'name': 'projects',
        'topic': 'Project Management',
        'is_private': True,
        'threads': [
                {'name': 'planning', 'is_private': True},
                {'name': 'tasks', 'is_private': True},
            ]
        },
    'backups': {
        'name': 'backups',
        'topic': 'Backup Management',
        'is_private': True,
        'threads': [
                {'name': 'schedule', 'is_private': True},
                {'name': 'logs', 'is_private': True},
                {'name': 'status', 'is_private': True}
                ]
        },
    'server-management': {
        'name': 'server-management',
        'topic': 'Server Administration',
        'is_private': True,
        'threads': [
                {'name': 'commands', 'is_private': True},
                {'name': 'updates', 'is_private': True},
                {'name': 'maintenance', 'is_private': True}
            ]
        },
    'logs': {
        'name': 'logs',
        'topic': 'System Logs',
        'is_private': True,
        'threads': [
                {'name': 'system-logs', 'is_private': True},
                {'name': 'error-logs', 'is_private': True},
                {'name': 'access-logs', 'is_private': True}
            ]
        },
    'monitoring': {
        'name': 'monitoring',
        'topic': 'System Monitoring',
        'is_private': True,
        'threads': [
                {'name': 'system-status', 'is_private': False},
                {'name': 'performance', 'is_private': True},
                {'name': 'alerts', 'is_private': True}
            ]
        },
    'bot-control': {
        'name': 'bot-control',
        'topic': 'Bot Management',
        'is_private': True,
        'threads': [
                {'name': 'commands', 'is_private': True},
                {'name': 'logs', 'is_private': True},
                {'name': 'updates', 'is_private': True}
            ]
        },
    'alerts': {
        'name': 'alerts',
        'topic': 'System Alerts',
        'is_private': True,
        'threads': [
                {'name': 'critical', 'is_private': True},
                {'name': 'warnings', 'is_private': True},
                {'name': 'notifications', 'is_private': True}
            ]
        }
    }
