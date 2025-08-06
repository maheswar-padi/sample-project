"""Command-line interface for TextProcessor."""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.progress import track

from .analyzer import TextAnalyzer
from .transformer import TextTransformer
from .config import Config
from .utils import format_output, display_rich_table, get_file_list, write_text_file

console = Console()


@click.group()
@click.version_option(version="1.0.0")
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
@click.pass_context
def cli(ctx: click.Context, config: Optional[str]) -> None:
    """TextProcessor - A powerful command-line tool for text processing operations."""
    # Initialize configuration
    config_path = Path(config) if config else None
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config_path)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Choice(['text', 'json', 'csv', 'markdown']), 
              help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Include detailed analysis')
@click.option('--save', type=click.Path(), help='Save results to file')
@click.option('--no-readability', is_flag=True, help='Skip readability analysis')
@click.pass_context
def analyze(ctx: click.Context, file_path: str, output: Optional[str], 
           verbose: bool, save: Optional[str], no_readability: bool) -> None:
    """Analyze a text file and generate detailed statistics."""
    config = ctx.obj['config']
    
    # Determine output format
    output_format = output or config.default_output_format
    include_readability = not no_readability and config.include_readability
    
    try:
        # Analyze the file
        analyzer = TextAnalyzer()
        with console.status(f"Analyzing {file_path}..."):
            results = analyzer.analyze_file(file_path, include_readability)
        
        if verbose:
            console.print(f"✅ Analysis complete for [bold]{file_path}[/bold]")
        
        # Format and display results
        if output_format == 'text' and not save:
            display_rich_table(results, f"Analysis Results: {Path(file_path).name}")
        else:
            formatted_output = format_output(results, output_format)
            
            if save:
                write_text_file(save, formatted_output)
                console.print(f"✅ Results saved to [bold]{save}[/bold]")
            else:
                console.print(formatted_output)
    
    except Exception as e:
        console.print(f"❌ Error analyzing file: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--operation', '-op', required=True,
              type=click.Choice([
                  'upper', 'lower', 'title', 'sentence', 'clean', 'normalize',
                  'remove_punctuation', 'remove_numbers', 'reverse', 'sort_lines',
                  'remove_empty_lines', 'add_line_numbers'
              ]), help='Transformation operation')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--no-backup', is_flag=True, help='Skip creating backup')
@click.pass_context
def transform(ctx: click.Context, file_path: str, operation: str, 
              output: Optional[str], no_backup: bool) -> None:
    """Transform text content with various operations."""
    config = ctx.obj['config']
    
    # Configure transformer
    preserve_original = not no_backup and config.preserve_original
    transformer = TextTransformer(preserve_original, config.backup_suffix)
    
    try:
        with console.status(f"Transforming {file_path}..."):
            output_path = transformer.transform_file(
                file_path, operation, output
            )
        
        console.print(f"✅ Transformation complete: [bold]{output_path}[/bold]")
        
        if preserve_original and not output:
            backup_path = Path(file_path).with_suffix(
                Path(file_path).suffix + config.backup_suffix
            )
            console.print(f"📁 Original backed up to: [dim]{backup_path}[/dim]")
    
    except Exception as e:
        console.print(f"❌ Error transforming file: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('pattern', default='*.txt')
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories')
@click.option('--output', '-o', type=click.Path(), help='Output file for combined results')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'markdown']),
              default='json', help='Output format for combined results')
@click.option('--no-readability', is_flag=True, help='Skip readability analysis')
@click.pass_context
def batch_analyze(ctx: click.Context, pattern: str, recursive: bool, 
                 output: Optional[str], format: str, no_readability: bool) -> None:
    """Process multiple files at once."""
    config = ctx.obj['config']
    include_readability = not no_readability and config.include_readability
    
    try:
        # Get file list
        files = get_file_list(pattern, recursive)
        
        if not files:
            console.print(f"❌ No files found matching pattern: {pattern}", style="red")
            sys.exit(1)
        
        console.print(f"Found {len(files)} files to process")
        
        # Process files
        analyzer = TextAnalyzer()
        all_results = {}
        
        for file_path in track(files, description="Processing files..."):
            try:
                results = analyzer.analyze_file(str(file_path), include_readability)
                all_results[str(file_path)] = results
            except Exception as e:
                console.print(f"⚠️  Skipping {file_path}: {e}", style="yellow")
        
        # Output results
        if output:
            formatted_output = format_output(all_results, format)
            write_text_file(output, formatted_output)
            console.print(f"✅ Batch results saved to [bold]{output}[/bold]")
        else:
            # Display summary
            console.print(f"\n📊 Batch Analysis Summary ({len(all_results)} files)")
            
            total_words = sum(
                result['basic_stats']['word_count'] 
                for result in all_results.values()
            )
            total_chars = sum(
                result['basic_stats']['character_count'] 
                for result in all_results.values()
            )
            
            console.print(f"Total words: {total_words:,}")
            console.print(f"Total characters: {total_chars:,}")
            
            # Show per-file summary
            for file_path, results in all_results.items():
                stats = results['basic_stats']
                console.print(
                    f"  {Path(file_path).name}: "
                    f"{stats['word_count']:,} words, "
                    f"{stats['character_count']:,} chars"
                )
    
    except Exception as e:
        console.print(f"❌ Error in batch processing: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Interactive mode for step-by-step text processing."""
    config = ctx.obj['config']
    console.print("🚀 Welcome to TextProcessor Interactive Mode!")
    console.print("Type 'help' for available commands or 'quit' to exit.\n")
    
    analyzer = TextAnalyzer()
    transformer = TextTransformer(config.preserve_original, config.backup_suffix)
    
    while True:
        try:
            command = console.input("\n[bold cyan]textprocessor>[/bold cyan] ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                console.print("👋 Goodbye!")
                break
            
            elif command.lower() == 'help':
                console.print("""
[bold]Available Commands:[/bold]
  analyze <file>     - Analyze a text file
  transform <file>   - Transform a text file
  config             - Show current configuration
  help               - Show this help message
  quit/exit/q        - Exit interactive mode
                """)
            
            elif command.lower() == 'config':
                console.print(f"""
[bold]Current Configuration:[/bold]
  Default output format: {config.default_output_format}
  Include readability: {config.include_readability}
  Preserve original: {config.preserve_original}
  Backup suffix: {config.backup_suffix}
                """)
            
            elif command.startswith('analyze '):
                file_path = command[8:].strip()
                if Path(file_path).exists():
                    results = analyzer.analyze_file(file_path, config.include_readability)
                    display_rich_table(results, f"Analysis: {Path(file_path).name}")
                else:
                    console.print(f"❌ File not found: {file_path}", style="red")
            
            elif command.startswith('transform '):
                file_path = command[10:].strip()
                if Path(file_path).exists():
                    # Get transformation operation
                    operation = console.input("Enter transformation operation: ").strip()
                    try:
                        output_path = transformer.transform_file(file_path, operation)
                        console.print(f"✅ Transformed: {output_path}")
                    except ValueError as e:
                        console.print(f"❌ {e}", style="red")
                else:
                    console.print(f"❌ File not found: {file_path}", style="red")
            
            elif command:
                console.print(f"❌ Unknown command: {command}", style="red")
                console.print("Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
            break
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")


@cli.command()
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current configuration."""
    config = ctx.obj['config']
    
    console.print("[bold]TextProcessor Configuration[/bold]")
    console.print(f"Config file: {config.config_path}")
    console.print(f"Default output format: {config.default_output_format}")
    console.print(f"Include readability: {config.include_readability}")
    console.print(f"Include sentiment: {config.include_sentiment}")
    console.print(f"Preserve original: {config.preserve_original}")
    console.print(f"Backup suffix: {config.backup_suffix}")


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()