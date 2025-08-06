"""Tests for TextTransformer class."""

import pytest
from pathlib import Path
from textprocessor.transformer import TextTransformer


class TestTextTransformer:
    """Test cases for TextTransformer."""
    
    @pytest.fixture
    def transformer(self):
        """Create a TextTransformer instance."""
        return TextTransformer()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for testing."""
        return """This is a Test Document.
        
    It has   multiple    spaces and lines.
Some WORDS are in UPPERCASE.
    
Others are in lowercase.
The document contains numbers: 123, 456.
And punctuation marks: !@#$%^&*()

Line 1
Line 2
Line 3"""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a temporary sample file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("This is a TEST file.\nWith Multiple Lines.\nFor testing transformations.")
        return str(file_path)
    
    def test_to_upper(self, transformer):
        """Test uppercase transformation."""
        text = "Hello World"
        result = transformer.transform_text(text, 'upper')
        assert result == "HELLO WORLD"
    
    def test_to_lower(self, transformer):
        """Test lowercase transformation."""
        text = "Hello World"
        result = transformer.transform_text(text, 'lower')
        assert result == "hello world"
    
    def test_to_title(self, transformer):
        """Test title case transformation."""
        text = "hello world"
        result = transformer.transform_text(text, 'title')
        assert result == "Hello World"
    
    def test_to_sentence_case(self, transformer):
        """Test sentence case transformation."""
        text = "hELLO wORLD"
        result = transformer.transform_text(text, 'sentence')
        assert result == "Hello world"
    
    def test_to_sentence_case_empty(self, transformer):
        """Test sentence case with empty string."""
        result = transformer.transform_text("", 'sentence')
        assert result == ""
    
    def test_clean_whitespace_default(self, transformer, sample_text):
        """Test whitespace cleaning with default options."""
        result = transformer.transform_text(sample_text, 'clean')
        
        # Should not contain multiple spaces
        assert '  ' not in result
        # Should be stripped
        assert not result.startswith(' ')
        assert not result.endswith(' ')
    
    def test_clean_whitespace_remove_empty_lines(self, transformer):
        """Test whitespace cleaning with empty line removal."""
        text = "Line 1\n\nLine 2\n\n\nLine 3"
        result = transformer.transform_text(text, 'clean', remove_empty_lines=True)
        assert result == "Line 1\nLine 2\nLine 3"
    
    def test_normalize_text(self, transformer):
        """Test text normalization."""
        text = "Hello  world  !  This   is  a  test ."
        result = transformer.transform_text(text, 'normalize')
        
        # Should fix punctuation spacing
        assert result == "Hello world! This is a test."
    
    def test_normalize_quotes(self, transformer):
        """Test quote standardization."""
        text = '"Hello" and 'world' and `test`'
        result = transformer.transform_text(text, 'normalize', standardize_quotes=True)
        assert '"' in result
        assert ''' not in result
        assert '`' not in result
    
    def test_remove_punctuation(self, transformer):
        """Test punctuation removal."""
        text = "Hello, world! How are you?"
        result = transformer.transform_text(text, 'remove_punctuation')
        assert result == "Hello world How are you"
    
    def test_remove_punctuation_keep_periods(self, transformer):
        """Test punctuation removal keeping periods."""
        text = "Hello, world! How are you?"
        result = transformer.transform_text(text, 'remove_punctuation', keep_periods=True)
        assert "." in result
        assert "," not in result
        assert "!" not in result
    
    def test_remove_numbers(self, transformer):
        """Test number removal."""
        text = "I have 123 apples and 45 oranges."
        result = transformer.transform_text(text, 'remove_numbers')
        assert "123" not in result
        assert "45" not in result
        assert "apples" in result
    
    def test_remove_numbers_keep_years(self, transformer):
        """Test number removal keeping years."""
        text = "In 2023, I had 123 apples and was born in 1990."
        result = transformer.transform_text(text, 'remove_numbers', keep_years=True)
        assert "2023" in result
        assert "1990" in result
        assert "123" not in result
    
    def test_reverse_text(self, transformer):
        """Test text reversal."""
        text = "Hello World"
        result = transformer.transform_text(text, 'reverse')
        assert result == "dlroW olleH"
    
    def test_reverse_by_words(self, transformer):
        """Test word order reversal."""
        text = "Hello World Test"
        result = transformer.transform_text(text, 'reverse', by_words=True)
        assert result == "Test World Hello"
    
    def test_reverse_by_lines(self, transformer):
        """Test line order reversal."""
        text = "Line 1\nLine 2\nLine 3"
        result = transformer.transform_text(text, 'reverse', by_lines=True)
        assert result == "Line 3\nLine 2\nLine 1"
    
    def test_sort_lines(self, transformer):
        """Test line sorting."""
        text = "Zebra\nApple\nBanana"
        result = transformer.transform_text(text, 'sort_lines')
        assert result == "Apple\nBanana\nZebra"
    
    def test_sort_lines_reverse(self, transformer):
        """Test reverse line sorting."""
        text = "Apple\nBanana\nZebra"
        result = transformer.transform_text(text, 'sort_lines', reverse=True)
        assert result == "Zebra\nBanana\nApple"
    
    def test_sort_lines_ignore_case(self, transformer):
        """Test case-insensitive line sorting."""
        text = "apple\nBanana\nzebra"
        result = transformer.transform_text(text, 'sort_lines', ignore_case=True)
        assert result == "apple\nBanana\nzebra"
    
    def test_sort_lines_remove_duplicates(self, transformer):
        """Test line sorting with duplicate removal."""
        text = "Apple\nBanana\nApple\nZebra"
        result = transformer.transform_text(text, 'sort_lines', remove_duplicates=True)
        assert result == "Apple\nBanana\nZebra"
    
    def test_remove_empty_lines(self, transformer):
        """Test empty line removal."""
        text = "Line 1\n\nLine 2\n\n\nLine 3\n"
        result = transformer.transform_text(text, 'remove_empty_lines')
        assert result == "Line 1\nLine 2\nLine 3"
    
    def test_add_line_numbers(self, transformer):
        """Test adding line numbers."""
        text = "First line\nSecond line\nThird line"
        result = transformer.transform_text(text, 'add_line_numbers')
        
        lines = result.split('\n')
        assert lines[0].startswith('1: ')
        assert lines[1].startswith('2: ')
        assert lines[2].startswith('3: ')
    
    def test_add_line_numbers_custom_start(self, transformer):
        """Test adding line numbers with custom start."""
        text = "First line\nSecond line"
        result = transformer.transform_text(text, 'add_line_numbers', start=10)
        
        lines = result.split('\n')
        assert lines[0].startswith('10: ')
        assert lines[1].startswith('11: ')
    
    def test_add_line_numbers_custom_separator(self, transformer):
        """Test adding line numbers with custom separator."""
        text = "First line"
        result = transformer.transform_text(text, 'add_line_numbers', separator=' - ')
        assert '1 - First line' in result
    
    def test_unknown_operation(self, transformer):
        """Test unknown operation raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            transformer.transform_text("test", 'unknown_operation')
        
        assert "Unknown operation 'unknown_operation'" in str(excinfo.value)
        assert "Available:" in str(excinfo.value)
    
    def test_transform_file_no_output(self, transformer, sample_file):
        """Test file transformation without output path."""
        original_content = Path(sample_file).read_text()
        
        # Transform to uppercase
        result_path = transformer.transform_file(sample_file, 'upper')
        
        assert result_path == Path(sample_file)
        new_content = Path(sample_file).read_text()
        assert new_content == original_content.upper()
        
        # Check backup was created
        backup_path = Path(sample_file).with_suffix('.txt.bak')
        assert backup_path.exists()
        assert backup_path.read_text() == original_content
    
    def test_transform_file_with_output(self, transformer, sample_file, tmp_path):
        """Test file transformation with output path."""
        output_path = tmp_path / "output.txt"
        original_content = Path(sample_file).read_text()
        
        result_path = transformer.transform_file(sample_file, 'upper', str(output_path))
        
        assert result_path == output_path
        assert output_path.exists()
        assert output_path.read_text() == original_content.upper()
        
        # Original should be unchanged
        assert Path(sample_file).read_text() == original_content
    
    def test_transform_file_no_backup(self, transformer, sample_file):
        """Test file transformation without backup."""
        transformer.preserve_original = False
        original_content = Path(sample_file).read_text()
        
        transformer.transform_file(sample_file, 'upper')
        
        # Check no backup was created
        backup_path = Path(sample_file).with_suffix('.txt.bak')
        assert not backup_path.exists()
        
        # File should be transformed
        assert Path(sample_file).read_text() == original_content.upper()
    
    def test_custom_backup_suffix(self, transformer, sample_file):
        """Test custom backup suffix."""
        transformer.backup_suffix = '.backup'
        original_content = Path(sample_file).read_text()
        
        transformer.transform_file(sample_file, 'upper')
        
        # Check custom backup was created
        backup_path = Path(sample_file).with_suffix('.txt.backup')
        assert backup_path.exists()
        assert backup_path.read_text() == original_content