"""
Helper utilities for QTI XML generation and image handling.
"""

import re
from pathlib import Path


class QTIImageExtractor:
    """Utility class for extracting and managing images in QTI content"""
    
    # Pattern to extract image references from HTML
    IMG_URI_PATTERN = r'<img[^>]+title="([^"]+)"'
    IMG_SRC_PATTERN = r'src=["\']([^"\']+)["\']'
    
    @staticmethod
    def extract_image_uris(text: str) -> list:
        """
        Extract image URI references from text.
        
        Args:
            text: Text containing image references
            
        Returns:
            List of image URIs found in the text
        """
        if not text:
            return []
        return re.findall(QTIImageExtractor.IMG_URI_PATTERN, text)
    
    @staticmethod
    def extract_image_sources(text: str) -> list:
        """
        Extract image source paths from text.
        
        Args:
            text: Text containing image references
            
        Returns:
            List of image source paths found in the text
        """
        if not text:
            return []
        return re.findall(QTIImageExtractor.IMG_SRC_PATTERN, text)
    
    @staticmethod
    def collect_all_images_from_question(question) -> set:
        """
        Collect all unique image URIs from a question.
        
        Args:
            question: A Question object (McqSAQuestion, McqMAQuestion, etc.)
            
        Returns:
            Set of unique image URI filenames
        """
        img_sources = set()
        
        # Extract images from problem statement
        problem_statement = question.get_problem_statement()
        img_sources.update(QTIImageExtractor.extract_image_uris(problem_statement))
        
        # Extract images from options
        options = question.get_options() or []
        for opt in options:
            opt_text = opt if isinstance(opt, str) else opt.get('text', '')
            img_sources.update(QTIImageExtractor.extract_image_uris(opt_text))
        
        return img_sources


class QTIImageLocator:
    """Utility class for locating image files in the file system"""
    
    @staticmethod
    def find_image(image_filename: str, search_start_dir: Path) -> Path:
        """
        Find an image file by searching in the current directory and parent directories.
        
        Args:
            image_filename: Name of the image file to find
            search_start_dir: Starting directory for the search
            
        Returns:
            Path to the image file if found, None otherwise
        """
        # Check in the current directory
        current_path = search_start_dir / image_filename
        if current_path.exists():
            return current_path
        
        # Search recursively in parent directories
        for parent in search_start_dir.iterdir():
            if parent.is_dir():
                recursive_path = parent / image_filename
                if recursive_path.exists():
                    return recursive_path
        
        return None
    
    @staticmethod
    def locate_images(image_filenames: set, search_dir: Path) -> dict:
        """
        Locate multiple image files.
        
        Args:
            image_filenames: Set of image filenames to locate
            search_dir: Starting directory for the search
            
        Returns:
            Dictionary mapping found image names to their Path objects,
            and a set of missing image names
        """
        found = {}
        missing = set()
        
        for img_name in image_filenames:
            img_path = QTIImageLocator.find_image(img_name, search_dir)
            if img_path:
                found[img_name] = img_path
            else:
                missing.add(img_name)
        
        return found, missing
