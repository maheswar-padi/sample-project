"""Text transformation functionality for TextProcessor."""

import re
from pathlib import Path
from typing import Union, Optional

from .utils import read_text_file, write_text_file, create_backup


class TextTransformer:
    """Text transformation operations."""
    
    def __init__(self, preserve_original: bool = True, backup_suffix: str = '.bak') -> None:
        """Initialize the text transformer.
        
        Args:
            preserve_original: Whether to create backups before transforming files
            backup_suffix: Suffix for backup files
        """
        self.preserve_original = preserve_original
        self.backup_suffix = backup_suffix
    
    def transform_text(self, text: str, operation: str, **kwargs) -> str:
        """Apply transformation operation to text.
        
        Args:
            text: Input text
            operation: Transformation operation name
            **kwargs: Additional parameters for specific operations
            
        Returns:
            Transformed text
            
        Raises:
            ValueError: If operation is not supported
        """
        operations = {
            'upper': self._to_upper,
            'lower': self._to_lower,
            'title': self._to_title,
            'sentence': self._to_sentence_case,
            'clean': self._clean_whitespace,
            'normalize': self._normalize_text,
            'remove_punctuation': self._remove_punctuation,
            'remove_numbers': self._remove_numbers,
            'reverse': self._reverse_text,
            'sort_lines': self._sort_lines,
            'remove_empty_lines': self._remove_empty_lines,
            'add_line_numbers': self._add_line_numbers,
        }
        
        if operation not in operations:
            available = ', '.join(operations.keys())
            raise ValueError(f"Unknown operation '{operation}'. Available: {available}")
        
        return operations[operation](text, **kwargs)
    
    def transform_file(self, file_path: Union[str, Path], operation: str, 
                      output_path: Optional[Union[str, Path]] = None, **kwargs) -> Path:
        """Apply transformation to a file.
        
        Args:
            file_path: Input file path
            operation: Transformation operation name
            output_path: Output file path (if None, overwrites original)
            **kwargs: Additional parameters for specific operations
            
        Returns:
            Path to the transformed file
        """
        input_path = Path(file_path)
        
        # Read original text
        text = read_text_file(input_path)
        
        # Apply transformation
        transformed_text = self.transform_text(text, operation, **kwargs)
        
        # Determine output path
        if output_path is None:
            output_path = input_path
        else:
            output_path = Path(output_path)
        
        # Create backup if preserving original and overwriting
        if self.preserve_original and output_path == input_path:
            create_backup(input_path, self.backup_suffix)
        
        # Write transformed text
        write_text_file(output_path, transformed_text)
        
        return output_path
    
    def _to_upper(self, text: str, **kwargs) -> str:
        """Convert text to uppercase."""
        return text.upper()
    
    def _to_lower(self, text: str, **kwargs) -> str:
        """Convert text to lowercase."""
        return text.lower()
    
    def _to_title(self, text: str, **kwargs) -> str:
        """Convert text to title case."""
        return text.title()
    
    def _to_sentence_case(self, text: str, **kwargs) -> str:
        """Convert text to sentence case (first letter uppercase, rest lowercase)."""
        if not text:
            return text
        return text[0].upper() + text[1:].lower()
    
    def _clean_whitespace(self, text: str, **kwargs) -> str:
        """Clean extra whitespace from text.
        
        Args:
            text: Input text
            **kwargs: Additional options:
                - normalize_spaces: Replace multiple spaces with single space
                - strip_lines: Strip whitespace from line ends
                - remove_empty_lines: Remove blank lines
        """
        result = text
        
        # Strip whitespace from line ends
        if kwargs.get('strip_lines', True):
            lines = result.split('\n')
            result = '\n'.join(line.rstrip() for line in lines)
        
        # Replace multiple spaces with single space
        if kwargs.get('normalize_spaces', True):
            result = re.sub(r' +', ' ', result)
        
        # Remove empty lines
        if kwargs.get('remove_empty_lines', False):
            lines = result.split('\n')
            result = '\n'.join(line for line in lines if line.strip())
        
        return result.strip()
    
    def _normalize_text(self, text: str, **kwargs) -> str:
        """Normalize text by cleaning whitespace and standardizing format.
        
        Args:
            text: Input text
            **kwargs: Additional options:
                - fix_punctuation: Fix spacing around punctuation
                - standardize_quotes: Convert quotes to standard format
        """
        result = self._clean_whitespace(text, **kwargs)
        
        # Fix punctuation spacing
        if kwargs.get('fix_punctuation', True):
            # Remove spaces before punctuation
            result = re.sub(r' +([,.!?;:])', r'\1', result)
            # Ensure space after punctuation
            result = re.sub(r'([,.!?;:])([^\s\n])', r'\1 \2', result)
        
        # Standardize quotes
        if kwargs.get('standardize_quotes', True):
            # Convert various quote types to standard double quotes
            result = re.sub(r'[""''`]', '"', result)
        
        return result
    
    def _remove_punctuation(self, text: str, **kwargs) -> str:
        """Remove punctuation from text.
        
        Args:
            text: Input text
            **kwargs: Additional options:
                - keep_periods: Keep sentence-ending periods
                - keep_apostrophes: Keep apostrophes in contractions
        """
        # Define punctuation to remove
        punctuation = r'[^\w\s'
        
        if kwargs.get('keep_periods', False):
            punctuation += '.'
        
        if kwargs.get('keep_apostrophes', False):
            punctuation += "'"
        
        punctuation += ']'
        
        return re.sub(punctuation, '', text)
    
    def _remove_numbers(self, text: str, **kwargs) -> str:
        """Remove numbers from text.
        
        Args:
            text: Input text
            **kwargs: Additional options:
                - keep_years: Keep 4-digit years
        """
        if kwargs.get('keep_years', False):
            # Remove numbers but keep 4-digit years
            result = re.sub(r'\b(?<!\d)\d{1,3}(?!\d)\b', '', text)
            result = re.sub(r'\b\d{5,}\b', '', result)
        else:
            # Remove all numbers
            result = re.sub(r'\d+', '', text)
        
        # Clean up extra spaces
        return re.sub(r' +', ' ', result).strip()
    
    def _reverse_text(self, text: str, **kwargs) -> str:
        """Reverse text.
        
        Args:
            text: Input text
            **kwargs: Additional options:
                - by_words: Reverse word order instead of character order
                - by_lines: Reverse line order
        """
        if kwargs.get('by_lines', False):
            lines = text.split('\n')
            return '\n'.join(reversed(lines))
        elif kwargs.get('by_words', False):
            words = text.split()
            return ' '.join(reversed(words))
        else:
            return text[::-1]
    
    def _sort_lines(self, text: str, **kwargs) -> str:
        """Sort lines in text.
        
        Args:
            text: Input text
            **kwargs: Additional options:
                - reverse: Sort in descending order
                - ignore_case: Case-insensitive sorting
                - remove_duplicates: Remove duplicate lines
        """
        lines = text.split('\n')
        
        # Remove duplicates if requested
        if kwargs.get('remove_duplicates', False):
            lines = list(dict.fromkeys(lines))  # Preserves order while removing duplicates
        
        # Sort lines
        if kwargs.get('ignore_case', False):
            lines.sort(key=str.lower, reverse=kwargs.get('reverse', False))
        else:
            lines.sort(reverse=kwargs.get('reverse', False))
        
        return '\n'.join(lines)
    
    def _remove_empty_lines(self, text: str, **kwargs) -> str:
        """Remove empty lines from text."""
        lines = text.split('\n')
        return '\n'.join(line for line in lines if line.strip())
    
    def _add_line_numbers(self, text: str, **kwargs) -> str:
        """Add line numbers to text.
        
        Args:
            text: Input text
            **kwargs: Additional options:
                - start: Starting line number (default: 1)
                - width: Width of line number field (default: auto)
                - separator: Separator between number and text (default: ': ')
        """
        lines = text.split('\n')
        start = kwargs.get('start', 1)
        separator = kwargs.get('separator', ': ')
        
        # Calculate width if not specified
        width = kwargs.get('width', len(str(len(lines) + start - 1)))
        
        numbered_lines = []
        for i, line in enumerate(lines, start=start):
            line_num = str(i).rjust(width)
            numbered_lines.append(f"{line_num}{separator}{line}")
        
        return '\n'.join(numbered_lines)