"""
TextProcessor - A powerful command-line tool for text processing operations.

This package provides text analysis and transformation capabilities through
a user-friendly CLI interface.
"""

__version__ = "1.0.0"
__author__ = "Sample Project"
__email__ = "contact@example.com"

from .analyzer import TextAnalyzer
from .transformer import TextTransformer
from .config import Config

__all__ = ["TextAnalyzer", "TextTransformer", "Config"]