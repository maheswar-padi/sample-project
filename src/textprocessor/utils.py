"""Utility functions for TextProcessor."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from rich.console import Console
from rich.table import Table


def read_text_file(file_path: Union[str, Path]) -> str:
    """Read text from a file with error handling.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is not supported
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Try different encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise UnicodeDecodeError(f"Could not decode file {file_path} with any supported encoding")


def write_text_file(file_path: Union[str, Path], content: str) -> None:
    """Write text to a file.
    
    Args:
        file_path: Path to output file
        content: Text content to write
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def format_output(data: Dict[str, Any], format_type: str = 'text') -> str:
    """Format analysis results for output.
    
    Args:
        data: Analysis results dictionary
        format_type: Output format ('text', 'json', 'csv', 'markdown')
        
    Returns:
        Formatted output string
    """
    if format_type == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    elif format_type == 'csv':
        output = []
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Value'])
        
        # Write data recursively
        def write_dict(d: Dict[str, Any], prefix: str = '') -> None:
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    write_dict(value, full_key)
                else:
                    writer.writerow([full_key, str(value)])
        
        write_dict(data)
        return '\n'.join(output)
    
    elif format_type == 'markdown':
        lines = ['# Text Analysis Results', '']
        
        def format_dict(d: Dict[str, Any], level: int = 2) -> None:
            for key, value in d.items():
                if isinstance(value, dict):
                    lines.append(f"{'#' * level} {key.title()}")
                    lines.append('')
                    format_dict(value, level + 1)
                else:
                    lines.append(f"- **{key.title()}**: {value}")
            lines.append('')
        
        format_dict(data)
        return '\n'.join(lines)
    
    else:  # text format
        return format_text_output(data)


def format_text_output(data: Dict[str, Any], indent: int = 0) -> str:
    """Format data as human-readable text.
    
    Args:
        data: Data dictionary to format
        indent: Indentation level
        
    Returns:
        Formatted text string
    """
    lines = []
    prefix = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key.title()}:")
            lines.append(format_text_output(value, indent + 1))
        else:
            lines.append(f"{prefix}{key.title()}: {value}")
    
    return '\n'.join(lines)


def display_rich_table(data: Dict[str, Any], title: str = "Analysis Results") -> None:
    """Display data in a rich table format.
    
    Args:
        data: Data to display
        title: Table title
    """
    console = Console()
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    def add_rows(d: Dict[str, Any], prefix: str = '') -> None:
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                add_rows(value, full_key)
            else:
                table.add_row(full_key.title(), str(value))
    
    add_rows(data)
    console.print(table)


def get_file_list(pattern: str, recursive: bool = False) -> List[Path]:
    """Get list of files matching a pattern.
    
    Args:
        pattern: File pattern (glob style)
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    if recursive:
        return list(Path('.').rglob(pattern))
    else:
        return list(Path('.').glob(pattern))


def create_backup(file_path: Union[str, Path], suffix: str = '.bak') -> Path:
    """Create a backup of a file.
    
    Args:
        file_path: Original file path
        suffix: Backup file suffix
        
    Returns:
        Path to backup file
    """
    path = Path(file_path)
    backup_path = path.with_suffix(path.suffix + suffix)
    
    if path.exists():
        backup_path.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
    
    return backup_path