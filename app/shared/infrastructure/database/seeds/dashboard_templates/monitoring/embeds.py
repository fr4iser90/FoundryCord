"""Embed definitions for monitoring dashboard migration"""
from typing import Dict, Any

MONITORING_EMBEDS = {
    "system_status_embed": {
        "title": "🖥️ System Status",
        "description": "Current system metrics and status",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Hostname",
                "value": "{{hostname}}",
                "inline": True
            },
            {
                "name": "Platform",
                "value": "{{platform}}",
                "inline": True
            },
            {
                "name": "Uptime",
                "value": "{{uptime}}",
                "inline": True
            },
            {
                "name": "CPU Usage",
                "value": "{{cpu_percent}}%",
                "inline": True
            },
            {
                "name": "Memory Usage",
                "value": "{{memory_percent}}%",
                "inline": True
            },
            {
                "name": "Disk Usage",
                "value": "{{disk_percent}}%",
                "inline": True
            }
        ]
    },
    "cpu_details_embed": {
        "title": "📊 CPU Details",
        "description": "Detailed CPU metrics",
        "color": 0x3498db,
        "fields": [
            {
                "name": "CPU Model",
                "value": "{{cpu_model}}",
                "inline": False
            },
            {
                "name": "Cores",
                "value": "{{cpu_cores}} physical, {{cpu_logical}} logical",
                "inline": True
            },
            {
                "name": "Current Usage",
                "value": "{{cpu_percent}}%",
                "inline": True
            },
            {
                "name": "Load Average",
                "value": "{{load_avg}}",
                "inline": True
            }
        ]
    },
    "memory_details_embed": {
        "title": "🧠 Memory Details",
        "description": "Detailed memory metrics",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Total Memory",
                "value": "{{memory_total}} GB",
                "inline": True
            },
            {
                "name": "Available",
                "value": "{{memory_available}} GB",
                "inline": True
            },
            {
                "name": "Used",
                "value": "{{memory_used}} GB ({{memory_percent}}%)",
                "inline": True
            },
            {
                "name": "Swap Total",
                "value": "{{swap_total}} GB",
                "inline": True
            },
            {
                "name": "Swap Used",
                "value": "{{swap_used}} GB ({{swap_percent}}%)",
                "inline": True
            }
        ]
    },
    "disk_details_embed": {
        "title": "💾 Disk Details",
        "description": "Storage metrics for main partitions",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Partition",
                "value": "{{disk_partitions}}",
                "inline": False
            }
        ]
    },
    "network_details_embed": {
        "title": "🌐 Network Details",
        "description": "Network interface metrics",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Interfaces",
                "value": "{{network_interfaces}}",
                "inline": False
            },
            {
                "name": "Bytes Sent",
                "value": "{{bytes_sent}}",
                "inline": True
            },
            {
                "name": "Bytes Received",
                "value": "{{bytes_recv}}",
                "inline": True
            }
        ]
    },
    "processes_embed": {
        "title": "📝 Running Processes",
        "description": "Top processes by CPU and memory usage",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Top CPU",
                "value": "```{{top_cpu_processes}}```",
                "inline": False
            },
            {
                "name": "Top Memory",
                "value": "```{{top_memory_processes}}```",
                "inline": False
            }
        ]
    },
    "docker_services_embed": {
        "title": "🐳 Docker Containers",
        "description": "Status of running Docker containers",
        "color": 0x3498db,
        "fields": [
            {
                "name": "Running Containers",
                "value": "{{docker_containers}}",
                "inline": False
            }
        ]
    }
}
