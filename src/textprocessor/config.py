"""Configuration management for TextProcessor."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration manager for TextProcessor."""
    
    DEFAULT_CONFIG = {
        "default_output_format": "text",
        "analysis": {
            "include_readability": True,
            "include_sentiment": False,
        },
        "transform": {
            "preserve_original": True,
            "backup_suffix": ".bak",
        },
    }
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration file. If None, looks for
                        .textprocessor.yaml in current directory.
        """
        self.config_path = config_path or Path(".textprocessor.yaml")
        self._config = self.DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                if user_config:
                    self._merge_config(self._config, user_config)
            except (yaml.YAMLError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'analysis.include_readability')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'analysis.include_readability')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
        except IOError as e:
            print(f"Error saving config file: {e}")
    
    @property
    def default_output_format(self) -> str:
        """Get default output format."""
        return self.get('default_output_format', 'text')
    
    @property
    def include_readability(self) -> bool:
        """Get whether to include readability analysis."""
        return self.get('analysis.include_readability', True)
    
    @property
    def include_sentiment(self) -> bool:
        """Get whether to include sentiment analysis."""
        return self.get('analysis.include_sentiment', False)
    
    @property
    def preserve_original(self) -> bool:
        """Get whether to preserve original files during transformation."""
        return self.get('transform.preserve_original', True)
    
    @property
    def backup_suffix(self) -> str:
        """Get backup file suffix."""
        return self.get('transform.backup_suffix', '.bak')