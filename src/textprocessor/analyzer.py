"""Text analysis functionality for TextProcessor."""

import re
from typing import Dict, Any, List
from pathlib import Path

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

from .utils import read_text_file


class TextAnalyzer:
    """Comprehensive text analysis tool."""
    
    def __init__(self) -> None:
        """Initialize the text analyzer."""
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self) -> None:
        """Ensure required NLTK data is downloaded."""
        if NLTK_AVAILABLE:
            try:
                # Try to use the data, download if not available
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('corpora/stopwords')
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                print("Downloading required NLTK data...")
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
    
    def analyze_text(self, text: str, include_readability: bool = True) -> Dict[str, Any]:
        """Analyze text and return comprehensive statistics.
        
        Args:
            text: Text to analyze
            include_readability: Whether to include readability metrics
            
        Returns:
            Dictionary containing analysis results
        """
        results = {
            "basic_stats": self._get_basic_stats(text),
            "word_analysis": self._analyze_words(text),
            "sentence_analysis": self._analyze_sentences(text),
            "character_analysis": self._analyze_characters(text),
        }
        
        if include_readability and TEXTSTAT_AVAILABLE:
            results["readability"] = self._get_readability_scores(text)
        
        if NLTK_AVAILABLE:
            results["linguistic_analysis"] = self._get_linguistic_analysis(text)
        
        return results
    
    def analyze_file(self, file_path: str, include_readability: bool = True) -> Dict[str, Any]:
        """Analyze a text file.
        
        Args:
            file_path: Path to text file
            include_readability: Whether to include readability metrics
            
        Returns:
            Dictionary containing analysis results
        """
        text = read_text_file(file_path)
        results = self.analyze_text(text, include_readability)
        results["file_info"] = self._get_file_info(file_path)
        return results
    
    def _get_basic_stats(self, text: str) -> Dict[str, int]:
        """Get basic text statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with basic statistics
        """
        lines = text.split('\n')
        words = text.split()
        
        # Count paragraphs (separated by blank lines)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        return {
            "character_count": len(text),
            "character_count_no_spaces": len(text.replace(' ', '')),
            "word_count": len(words),
            "line_count": len(lines),
            "paragraph_count": len(paragraphs),
            "blank_lines": len([line for line in lines if not line.strip()]),
        }
    
    def _analyze_words(self, text: str) -> Dict[str, Any]:
        """Analyze word-level statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with word analysis
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {
                "unique_words": 0,
                "average_word_length": 0.0,
                "longest_word": "",
                "shortest_word": "",
                "word_frequency": {},
            }
        
        word_lengths = [len(word) for word in words]
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 most frequent words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "unique_words": len(set(words)),
            "average_word_length": sum(word_lengths) / len(word_lengths),
            "longest_word": max(words, key=len),
            "shortest_word": min(words, key=len),
            "word_frequency": dict(top_words),
        }
    
    def _analyze_sentences(self, text: str) -> Dict[str, Any]:
        """Analyze sentence-level statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentence analysis
        """
        if NLTK_AVAILABLE:
            sentences = sent_tokenize(text)
        else:
            # Simple sentence splitting
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not sentences:
            return {
                "sentence_count": 0,
                "average_sentence_length": 0.0,
                "longest_sentence": "",
                "shortest_sentence": "",
            }
        
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        
        return {
            "sentence_count": len(sentences),
            "average_sentence_length": sum(sentence_lengths) / len(sentence_lengths),
            "longest_sentence": max(sentences, key=lambda x: len(x.split())),
            "shortest_sentence": min(sentences, key=lambda x: len(x.split())),
        }
    
    def _analyze_characters(self, text: str) -> Dict[str, Any]:
        """Analyze character-level statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with character analysis
        """
        char_counts = {
            "uppercase_letters": sum(1 for c in text if c.isupper()),
            "lowercase_letters": sum(1 for c in text if c.islower()),
            "digits": sum(1 for c in text if c.isdigit()),
            "spaces": sum(1 for c in text if c.isspace()),
            "punctuation": sum(1 for c in text if c in '.,!?;:"()[]{}'),
            "special_characters": sum(1 for c in text if not c.isalnum() and not c.isspace()),
        }
        
        return char_counts
    
    def _get_readability_scores(self, text: str) -> Dict[str, float]:
        """Get readability scores using textstat.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with readability scores
        """
        if not TEXTSTAT_AVAILABLE:
            return {}
        
        return {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "gunning_fog": textstat.gunning_fog(text),
            "automated_readability_index": textstat.automated_readability_index(text),
            "coleman_liau_index": textstat.coleman_liau_index(text),
            "linsear_write_formula": textstat.linsear_write_formula(text),
            "dale_chall_readability_score": textstat.dale_chall_readability_score(text),
        }
    
    def _get_linguistic_analysis(self, text: str) -> Dict[str, Any]:
        """Get linguistic analysis using NLTK.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with linguistic analysis
        """
        if not NLTK_AVAILABLE:
            return {}
        
        # Tokenize words and get POS tags
        words = word_tokenize(text.lower())
        pos_tags = pos_tag(words)
        
        # Count POS tags
        pos_counts = {}
        for word, pos in pos_tags:
            pos_counts[pos] = pos_counts.get(pos, 0) + 1
        
        # Get stopwords
        try:
            stop_words = set(stopwords.words('english'))
            stopword_count = sum(1 for word in words if word in stop_words)
        except LookupError:
            stopword_count = 0
        
        return {
            "pos_tag_counts": pos_counts,
            "stopword_count": stopword_count,
            "lexical_diversity": len(set(words)) / len(words) if words else 0,
        }
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        return {
            "filename": path.name,
            "file_size_bytes": path.stat().st_size,
            "file_extension": path.suffix,
            "absolute_path": str(path.absolute()),
        }