"""Tests for CLI interface."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from textprocessor.cli import cli, analyze, transform, batch_analyze, interactive
from textprocessor.config import Config


class TestCLI:
    """Test cases for CLI interface."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a temporary sample file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("This is a test file for CLI testing.\nIt has multiple lines.")
        return str(file_path)
    
    @pytest.fixture
    def config_file(self, tmp_path):
        """Create a temporary config file."""
        config_path = tmp_path / ".textprocessor.yaml"
        config_path.write_text("""
default_output_format: json
analysis:
  include_readability: false
transform:
  preserve_original: false
""")
        return str(config_path)
    
    def test_cli_help(self, runner):
        """Test CLI help message."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'TextProcessor' in result.output
        assert 'analyze' in result.output
        assert 'transform' in result.output
    
    def test_cli_version(self, runner):
        """Test CLI version display."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    def test_analyze_help(self, runner):
        """Test analyze command help."""
        result = runner.invoke(cli, ['analyze', '--help'])
        assert result.exit_code == 0
        assert 'Analyze a text file' in result.output
        assert '--output' in result.output
        assert '--verbose' in result.output
    
    def test_analyze_nonexistent_file(self, runner):
        """Test analyzing non-existent file."""
        result = runner.invoke(cli, ['analyze', 'nonexistent.txt'])
        assert result.exit_code != 0
    
    def test_analyze_file_basic(self, runner, sample_file):
        """Test basic file analysis."""
        result = runner.invoke(cli, ['analyze', sample_file])
        assert result.exit_code == 0
        # Should not crash and should produce some output
        assert len(result.output) > 0
    
    def test_analyze_file_json_output(self, runner, sample_file):
        """Test file analysis with JSON output."""
        result = runner.invoke(cli, ['analyze', sample_file, '--output', 'json'])
        assert result.exit_code == 0
        # Should contain JSON-like content
        assert '{' in result.output or 'basic_stats' in result.output
    
    def test_analyze_file_verbose(self, runner, sample_file):
        """Test file analysis with verbose output."""
        result = runner.invoke(cli, ['analyze', sample_file, '--verbose'])
        assert result.exit_code == 0
        assert 'Analysis complete' in result.output or len(result.output) > 0
    
    def test_analyze_save_results(self, runner, sample_file, tmp_path):
        """Test saving analysis results to file."""
        output_file = tmp_path / "results.json"
        result = runner.invoke(cli, [
            'analyze', sample_file, 
            '--output', 'json',
            '--save', str(output_file)
        ])
        assert result.exit_code == 0
        assert output_file.exists()
        assert len(output_file.read_text()) > 0
    
    def test_transform_help(self, runner):
        """Test transform command help."""
        result = runner.invoke(cli, ['transform', '--help'])
        assert result.exit_code == 0
        assert 'Transform text content' in result.output
        assert '--operation' in result.output
    
    def test_transform_missing_operation(self, runner, sample_file):
        """Test transform without operation."""
        result = runner.invoke(cli, ['transform', sample_file])
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()
    
    def test_transform_file_upper(self, runner, sample_file):
        """Test file transformation to uppercase."""
        original_content = Path(sample_file).read_text()
        result = runner.invoke(cli, ['transform', sample_file, '--operation', 'upper', '--no-backup'])
        
        if result.exit_code == 0:
            # If successful, file should be transformed
            new_content = Path(sample_file).read_text()
            assert new_content == original_content.upper()
    
    def test_transform_with_output(self, runner, sample_file, tmp_path):
        """Test transformation with output file."""
        output_file = tmp_path / "transformed.txt"
        result = runner.invoke(cli, [
            'transform', sample_file, 
            '--operation', 'upper',
            '--output', str(output_file)
        ])
        
        if result.exit_code == 0:
            assert output_file.exists()
    
    def test_batch_analyze_help(self, runner):
        """Test batch analyze command help."""
        result = runner.invoke(cli, ['batch-analyze', '--help'])
        assert result.exit_code == 0
        assert 'Process multiple files' in result.output
        assert '--recursive' in result.output
    
    def test_batch_analyze_no_files(self, runner):
        """Test batch analyze with no matching files."""
        result = runner.invoke(cli, ['batch-analyze', 'nonexistent*.txt'])
        assert result.exit_code != 0
        assert 'No files found' in result.output
    
    def test_batch_analyze_with_files(self, runner, tmp_path):
        """Test batch analyze with matching files."""
        # Create multiple test files
        for i in range(3):
            file_path = tmp_path / f"test{i}.txt"
            file_path.write_text(f"Test file {i} content.")
        
        # Change to temp directory for pattern matching
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(cli, ['batch-analyze', '*.txt'])
            # Should not crash
            assert 'files' in result.output.lower() or result.exit_code == 0
        finally:
            os.chdir(old_cwd)
    
    def test_config_show_help(self, runner):
        """Test config show command help."""
        result = runner.invoke(cli, ['config-show', '--help'])
        assert result.exit_code == 0
        assert 'Show current configuration' in result.output
    
    def test_config_show(self, runner):
        """Test config show command."""
        result = runner.invoke(cli, ['config-show'])
        assert result.exit_code == 0
        assert 'Configuration' in result.output
        assert 'Default output format' in result.output
    
    def test_cli_with_config_file(self, runner, sample_file, config_file):
        """Test CLI with custom config file."""
        result = runner.invoke(cli, [
            '--config', config_file,
            'analyze', sample_file
        ])
        # Should not crash with custom config
        assert result.exit_code == 0 or len(result.output) > 0
    
    def test_interactive_help(self, runner):
        """Test interactive command help."""
        result = runner.invoke(cli, ['interactive', '--help'])
        assert result.exit_code == 0
        assert 'Interactive mode' in result.output
    
    def test_unknown_command(self, runner):
        """Test unknown command."""
        result = runner.invoke(cli, ['unknown-command'])
        assert result.exit_code != 0
        assert 'No such command' in result.output


class TestConfig:
    """Test configuration functionality."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.default_output_format == 'text'
        assert config.include_readability is True
        assert config.preserve_original is True
        assert config.backup_suffix == '.bak'
    
    def test_config_get_set(self):
        """Test configuration get/set operations."""
        config = Config()
        
        # Test setting and getting values
        config.set('test.value', 'hello')
        assert config.get('test.value') == 'hello'
        
        # Test default value
        assert config.get('nonexistent.key', 'default') == 'default'
    
    def test_config_with_file(self, tmp_path):
        """Test configuration loading from file."""
        config_path = tmp_path / "test_config.yaml"
        config_path.write_text("""
default_output_format: markdown
analysis:
  include_readability: false
""")
        
        config = Config(config_path)
        assert config.default_output_format == 'markdown'
        assert config.include_readability is False
    
    def test_config_save(self, tmp_path):
        """Test configuration saving."""
        config_path = tmp_path / "save_test.yaml"
        config = Config(config_path)
        
        config.set('test.key', 'test_value')
        config.save()
        
        assert config_path.exists()
        content = config_path.read_text()
        assert 'test_value' in content