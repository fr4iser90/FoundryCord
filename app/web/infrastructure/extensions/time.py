"""
Time extension module for handling time-related functionality.
Provides configurable timezone and format support.
"""
from datetime import datetime
import pytz
from typing import Optional, Union

class TimeExtension:
    def __init__(self):
        self._timezone = 'Europe/Berlin'  # Default timezone
        self._date_format = '%Y-%m-%d %H:%M:%S'  # Default format
        self._time_ago_enabled = True  # Enable/disable time ago format
        self._initialized = False
        
    def __call__(self):
        """Make the extension callable for consistency"""
        if not self._initialized:
            self._initialize()
        return self
        
    def _initialize(self):
        """Initialize time extension if not already done"""
        if self._initialized:
            return
            
        # Validate timezone
        if self._timezone not in pytz.all_timezones:
            self._timezone = 'UTC'
            
        # Validate date format
        try:
            datetime.now().strftime(self._date_format)
        except ValueError:
            self._date_format = '%Y-%m-%d %H:%M:%S'
            
        self._initialized = True
        
    @property
    def timezone(self) -> str:
        if not self._initialized:
            self._initialize()
        return self._timezone
    
    @timezone.setter
    def timezone(self, value: str):
        if value not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {value}")
        self._timezone = value
        
    @property
    def date_format(self) -> str:
        if not self._initialized:
            self._initialize()
        return self._date_format
    
    @date_format.setter
    def date_format(self, value: str):
        # Validate format string
        try:
            datetime.now().strftime(value)
            self._date_format = value
        except ValueError as e:
            raise ValueError(f"Invalid date format: {value}") from e
            
    @property
    def time_ago_enabled(self) -> bool:
        if not self._initialized:
            self._initialize()
        return self._time_ago_enabled
    
    @time_ago_enabled.setter
    def time_ago_enabled(self, value: bool):
        self._time_ago_enabled = bool(value)

    def format_time(self, timestamp: Union[datetime, str, None], use_time_ago: Optional[bool] = None) -> Optional[str]:
        """
        Format a timestamp according to current settings
        
        Args:
            timestamp: The timestamp to format (string, datetime, or None)
            use_time_ago: Override the global time_ago setting
            
        Returns:
            Formatted timestamp string or None if input is None
        """
        if not self._initialized:
            self._initialize()
            
        if timestamp is None:
            return None
            
        if isinstance(timestamp, str):
            try:
                # Try ISO format first
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Try standard format
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return timestamp  # Return original string if parsing fails

        # Ensure timestamp has timezone info
        if isinstance(timestamp, datetime):
            if timestamp.tzinfo is None:
                timestamp = pytz.UTC.localize(timestamp)
                
            # Convert to configured timezone
            tz = pytz.timezone(self._timezone)
            timestamp = timestamp.astimezone(tz)
            
            # Use time ago if enabled and requested
            should_use_time_ago = self._time_ago_enabled if use_time_ago is None else use_time_ago
            if should_use_time_ago:
                return self._format_time_ago(timestamp)
                
            # Otherwise use configured date format
            return timestamp.strftime(self._date_format)
            
        return str(timestamp)  # Fallback for unknown types
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as relative time"""
        now = datetime.now(timestamp.tzinfo)
        diff = now - timestamp
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 2592000:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"

# Global instance
time_extension = TimeExtension() 