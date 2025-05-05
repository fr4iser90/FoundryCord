"""
Static files extension module for handling static file serving and verification.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class StaticExtension:
    def __init__(self):
        self._static_dir: Path = None
        self._required_paths: Dict[str, Path] = {}
        self._mounted = False
        self._initialized = False
        
    def __call__(self):
        """Make the extension callable for consistency"""
        if not self._initialized:
            # Default to web/static directory if not initialized
            self._static_dir = Path(__file__).parent.parent.parent / "static"
            self._initialize_static()
        return self
        
    def _initialize_static(self):
        """Initialize static files if not already done"""
        if self._initialized:
            return
            
        if not self._static_dir.exists():
            logger.error(f"Static directory not found: {self._static_dir}")
            raise FileNotFoundError(f"Static directory not found: {self._static_dir}")
            
        # Verify critical paths
        self.verify_paths()
        
        self._initialized = True
            
    def init_app(self, app: FastAPI, static_dir: Path = None):
        """Initialize static files for the application"""
        if static_dir:
            self._static_dir = static_dir
        else:
            # Default to web/static directory
            self._static_dir = Path(__file__).parent.parent.parent / "static"
            
        logger.debug(f"Static directory absolute path: {self._static_dir}")
        
        self._initialize_static()
        
        # Mount static files
        if not self._mounted:
            app.mount("/static", StaticFiles(directory=str(self._static_dir)), name="static")
            self._mounted = True
            logger.info("Static files mounted successfully")
        
    def verify_paths(self) -> Dict[str, bool]:
        """Verify existence of critical static files"""
        paths_to_check = {
            "css_base": self._static_dir / "css" / "core" / "base.css",
            "css_theme_dark": self._static_dir / "css" / "themes" / "dark.css",
            "css_theme_light": self._static_dir / "css" / "themes" / "light.css",
            "css_components": self._static_dir / "css" / "components",
            "css_views": self._static_dir / "css" / "views",
            "js_main": self._static_dir / "js" / "core" / "main.js",
            "js_theme": self._static_dir / "js" / "core" / "theme.js"
        }
        
        results = {}
        for name, path in paths_to_check.items():
            exists = path.exists()
            results[name] = exists
            logger.debug(f"{name}: {path} exists: {exists}")
            
        return results
        
    def get_static_url(self, path: str) -> str:
        """Get URL for a static file"""
        if not self._initialized:
            self._initialize_static()
        return f"/static/{path}"
        
    def list_files(self, subdir: str = None) -> List[Path]:
        """List files in static directory or subdirectory"""
        if not self._initialized:
            self._initialize_static()
            
        target_dir = self._static_dir
        if subdir:
            target_dir = target_dir / subdir
            
        if not target_dir.exists():
            return []
            
        return list(target_dir.rglob("*"))
        
    @property
    def static_dir(self) -> Path:
        """Get the static files directory"""
        if not self._initialized:
            self._initialize_static()
        return self._static_dir

# Global instance
static_extension = StaticExtension() 