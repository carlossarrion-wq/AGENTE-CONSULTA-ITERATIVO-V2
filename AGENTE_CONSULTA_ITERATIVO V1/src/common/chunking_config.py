"""
Centralized Chunking Configuration
Provides a single source of truth for chunking parameters across the application
"""

import os
import yaml
from typing import Dict, Any, Optional
from loguru import logger


class ChunkingConfig:
    """
    Centralized configuration for document chunking parameters.
    This class ensures consistent chunking parameters across different components.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize chunking configuration.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Default chunking parameters
        self.defaults = {
            # General text chunking
            'chunk_size': 1500,
            'chunk_overlap': 225,
            'min_chunk_size': 250,
            'separators': ["\n\n", "\n", " ", ""],
            
            # Table chunking
            'table_min_rows_per_chunk': 5,
            'table_max_rows_per_chunk': 20,
            
            # Excel optimization
            'excel_batch_size': 1000,
            'excel_max_rows_per_chunk': 50,
            'excel_min_rows_per_chunk': 10,
            'excel_include_headers': True,
            'excel_preserve_structure': True
        }
        
        # Load configuration from file if provided
        self.config = self.defaults.copy()
        if config_path:
            self._load_config(config_path)
        
        logger.info(f"ChunkingConfig initialized with chunk_size={self.chunk_size}, "
                   f"chunk_overlap={self.chunk_overlap}")
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                
                # Extract chunking parameters
                chunking = loaded_config.get('chunking', {})
                if chunking:
                    # Update config with loaded values
                    self.config.update({
                        'chunk_size': chunking.get('chunk_size', self.defaults['chunk_size']),
                        'chunk_overlap': chunking.get('chunk_overlap', self.defaults['chunk_overlap']),
                        'min_chunk_size': chunking.get('min_chunk_size', self.defaults['min_chunk_size']),
                        'separators': chunking.get('separators', self.defaults['separators']),
                        'table_min_rows_per_chunk': chunking.get('table_min_rows_per_chunk', 
                                                              self.defaults['table_min_rows_per_chunk']),
                        'table_max_rows_per_chunk': chunking.get('table_max_rows_per_chunk', 
                                                              self.defaults['table_max_rows_per_chunk'])
                    })
                
                # Extract Excel optimization parameters
                excel_opt = loaded_config.get('excel_optimization', {})
                if excel_opt:
                    batch_processing = excel_opt.get('batch_processing', {})
                    self.config.update({
                        'excel_batch_size': batch_processing.get('batch_size', 
                                                              self.defaults['excel_batch_size']),
                        'excel_max_rows_per_chunk': batch_processing.get('max_rows_per_chunk', 
                                                                      self.defaults['excel_max_rows_per_chunk']),
                        'excel_min_rows_per_chunk': batch_processing.get('min_rows_per_chunk', 
                                                                      self.defaults['excel_min_rows_per_chunk']),
                        'excel_include_headers': excel_opt.get('structure_preservation', {}).get(
                            'include_headers_in_chunks', self.defaults['excel_include_headers']),
                        'excel_preserve_structure': excel_opt.get('structure_preservation', {}).get(
                            'preserve_table_structure', self.defaults['excel_preserve_structure'])
                    })
                
                logger.info(f"Loaded chunking configuration from {config_path}")
            else:
                logger.warning(f"Configuration file not found: {config_path}, using defaults")
        except Exception as e:
            logger.error(f"Error loading chunking configuration: {e}")
            logger.info("Using default chunking parameters")
    
    def get_app_specific_config(self, app_name: str, config_path: str) -> 'ChunkingConfig':
        """
        Get application-specific chunking configuration.
        
        Args:
            app_name: Application name
            config_path: Path to configuration file
            
        Returns:
            Application-specific ChunkingConfig instance
        """
        try:
            # Create a copy of this config
            app_config = ChunkingConfig()
            app_config.config = self.config.copy()
            
            # Load application-specific overrides
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                
                # Check for application-specific settings
                apps_config = loaded_config.get('applications', {})
                app_specific = apps_config.get(app_name, {})
                
                if app_specific:
                    # Extract Excel optimization parameters for this app
                    excel_opt = app_specific.get('excel_optimization', {})
                    if excel_opt:
                        app_config.config.update({
                            'excel_batch_size': excel_opt.get('batch_size', app_config.excel_batch_size),
                            'excel_max_rows_per_chunk': excel_opt.get('max_rows_per_chunk', 
                                                                   app_config.excel_max_rows_per_chunk)
                        })
                    
                    # Extract chunking parameters for this app
                    chunking = app_specific.get('chunking', {})
                    if chunking:
                        app_config.config.update({
                            'chunk_size': chunking.get('chunk_size', app_config.chunk_size),
                            'chunk_overlap': chunking.get('chunk_overlap', app_config.chunk_overlap)
                        })
                    
                    logger.info(f"Loaded application-specific chunking config for {app_name}")
            
            return app_config
            
        except Exception as e:
            logger.error(f"Error loading app-specific chunking config: {e}")
            return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary with all configuration parameters
        """
        return self.config.copy()
    
    # Properties for easy access to configuration parameters
    @property
    def chunk_size(self) -> int:
        return self.config['chunk_size']
    
    @property
    def chunk_overlap(self) -> int:
        return self.config['chunk_overlap']
    
    @property
    def min_chunk_size(self) -> int:
        return self.config['min_chunk_size']
    
    @property
    def separators(self) -> list:
        return self.config['separators']
    
    @property
    def table_min_rows_per_chunk(self) -> int:
        return self.config['table_min_rows_per_chunk']
    
    @property
    def table_max_rows_per_chunk(self) -> int:
        return self.config['table_max_rows_per_chunk']
    
    @property
    def excel_batch_size(self) -> int:
        return self.config['excel_batch_size']
    
    @property
    def excel_max_rows_per_chunk(self) -> int:
        return self.config['excel_max_rows_per_chunk']
    
    @property
    def excel_min_rows_per_chunk(self) -> int:
        return self.config['excel_min_rows_per_chunk']
    
    @property
    def excel_include_headers(self) -> bool:
        return self.config['excel_include_headers']
    
    @property
    def excel_preserve_structure(self) -> bool:
        return self.config['excel_preserve_structure']


def get_default_chunking_config() -> ChunkingConfig:
    """
    Get default chunking configuration.
    
    Returns:
        Default ChunkingConfig instance
    """
    return ChunkingConfig()


def load_chunking_config(config_path: str = "config/excel_optimization_config.yaml") -> ChunkingConfig:
    """
    Load chunking configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ChunkingConfig instance
    """
    return ChunkingConfig(config_path)
