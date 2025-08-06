"""Tests for TextAnalyzer class."""

import pytest
from pathlib import Path
from textprocessor.analyzer import TextAnalyzer


class TestTextAnalyzer:
    """Test cases for TextAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a TextAnalyzer instance."""
        return TextAnalyzer()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for testing."""
        return """This is a test document.
        
It has multiple paragraphs and sentences.
Some words are repeated. Some words are unique.

The document contains 123 numbers and punctuation!
Testing readability and analysis features."""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a temporary sample file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("""This is a sample text file.
        
It contains multiple lines and paragraphs.
Perfect for testing file analysis functionality.

The file has exactly 25 words in this sentence here.
Numbers like 42 and symbols like @#$ are also present.""")
        return str(file_path)
    
    def test_basic_stats(self, analyzer, sample_text):
        """Test basic text statistics."""
        results = analyzer._get_basic_stats(sample_text)
        
        assert isinstance(results, dict)
        assert 'character_count' in results
        assert 'word_count' in results
        assert 'line_count' in results
        assert 'paragraph_count' in results
        
        assert results['character_count'] > 0
        assert results['word_count'] > 0
        assert results['line_count'] >= 1
        assert results['paragraph_count'] >= 1
    
    def test_word_analysis(self, analyzer, sample_text):
        """Test word-level analysis."""
        results = analyzer._analyze_words(sample_text)
        
        assert isinstance(results, dict)
        assert 'unique_words' in results
        assert 'average_word_length' in results
        assert 'longest_word' in results
        assert 'shortest_word' in results
        assert 'word_frequency' in results
        
        assert results['unique_words'] > 0
        assert results['average_word_length'] > 0
        assert len(results['longest_word']) > 0
        assert len(results['shortest_word']) > 0
        assert isinstance(results['word_frequency'], dict)
    
    def test_word_analysis_empty_text(self, analyzer):
        """Test word analysis with empty text."""
        results = analyzer._analyze_words("")
        
        assert results['unique_words'] == 0
        assert results['average_word_length'] == 0.0
        assert results['longest_word'] == ""
        assert results['shortest_word'] == ""
        assert results['word_frequency'] == {}
    
    def test_sentence_analysis(self, analyzer, sample_text):
        """Test sentence-level analysis."""
        results = analyzer._analyze_sentences(sample_text)
        
        assert isinstance(results, dict)
        assert 'sentence_count' in results
        assert 'average_sentence_length' in results
        assert 'longest_sentence' in results
        assert 'shortest_sentence' in results
        
        assert results['sentence_count'] > 0
        assert results['average_sentence_length'] > 0
    
    def test_character_analysis(self, analyzer, sample_text):
        """Test character-level analysis."""
        results = analyzer._analyze_characters(sample_text)
        
        assert isinstance(results, dict)
        expected_keys = [
            'uppercase_letters', 'lowercase_letters', 'digits',
            'spaces', 'punctuation', 'special_characters'
        ]
        
        for key in expected_keys:
            assert key in results
            assert isinstance(results[key], int)
            assert results[key] >= 0
    
    def test_analyze_text_complete(self, analyzer, sample_text):
        """Test complete text analysis."""
        results = analyzer.analyze_text(sample_text, include_readability=False)
        
        assert isinstance(results, dict)
        expected_sections = [
            'basic_stats', 'word_analysis', 
            'sentence_analysis', 'character_analysis'
        ]
        
        for section in expected_sections:
            assert section in results
            assert isinstance(results[section], dict)
    
    def test_analyze_file(self, analyzer, sample_file):
        """Test file analysis."""
        results = analyzer.analyze_file(sample_file, include_readability=False)
        
        assert isinstance(results, dict)
        assert 'file_info' in results
        
        file_info = results['file_info']
        assert 'filename' in file_info
        assert 'file_size_bytes' in file_info
        assert 'file_extension' in file_info
        assert 'absolute_path' in file_info
        
        assert file_info['filename'] == 'test.txt'
        assert file_info['file_size_bytes'] > 0
        assert file_info['file_extension'] == '.txt'
    
    def test_file_info(self, analyzer, sample_file):
        """Test file information extraction."""
        file_info = analyzer._get_file_info(sample_file)
        
        assert isinstance(file_info, dict)
        assert file_info['filename'] == Path(sample_file).name
        assert file_info['file_size_bytes'] > 0
        assert file_info['file_extension'] == Path(sample_file).suffix
        assert Path(file_info['absolute_path']).exists()
    
    def test_readability_scores_available(self, analyzer, sample_text):
        """Test readability scores when textstat is available."""
        try:
            import textstat
            results = analyzer._get_readability_scores(sample_text)
            
            if results:  # Only test if textstat is available
                assert isinstance(results, dict)
                expected_scores = [
                    'flesch_reading_ease', 'flesch_kincaid_grade',
                    'gunning_fog', 'automated_readability_index'
                ]
                
                for score in expected_scores:
                    if score in results:
                        assert isinstance(results[score], (int, float))
        except ImportError:
            # Skip if textstat not available
            results = analyzer._get_readability_scores(sample_text)
            assert results == {}
    
    def test_linguistic_analysis_available(self, analyzer, sample_text):
        """Test linguistic analysis when NLTK is available."""
        try:
            import nltk
            results = analyzer._get_linguistic_analysis(sample_text)
            
            if results:  # Only test if NLTK is available
                assert isinstance(results, dict)
                if 'pos_tag_counts' in results:
                    assert isinstance(results['pos_tag_counts'], dict)
                if 'lexical_diversity' in results:
                    assert isinstance(results['lexical_diversity'], float)
                    assert 0 <= results['lexical_diversity'] <= 1
        except ImportError:
            # Skip if NLTK not available
            results = analyzer._get_linguistic_analysis(sample_text)
            assert results == {}
    
    def test_analyze_nonexistent_file(self, analyzer):
        """Test analyzing a non-existent file."""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_file("nonexistent_file.txt")
    
    def test_empty_text_analysis(self, analyzer):
        """Test analysis of empty text."""
        results = analyzer.analyze_text("", include_readability=False)
        
        assert isinstance(results, dict)
        assert results['basic_stats']['character_count'] == 0
        assert results['basic_stats']['word_count'] == 0
        assert results['word_analysis']['unique_words'] == 0