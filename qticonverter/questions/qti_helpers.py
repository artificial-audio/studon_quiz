"""Helper utilities for QTI XML generation and image handling.

This module provides small helpers to extract image references from
HTML fragments and to locate image files on disk. The utilities are
kept intentionally simple and are used by the question classes when
building QTI packages.
"""

# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import re
from pathlib import Path


class QTIImageExtractor:
    """Utility class for extracting and managing images in QTI content.

    The extractor provides functions to parse `<img>` tag attributes and
    to collect image references from question objects.
    """
    
    # Pattern to extract image references from HTML
    IMG_URI_PATTERN = r'<img[^>]+title="([^"]+)"'
    IMG_SRC_PATTERN = r'src=["\']([^"\']+)["\']'
    IMG_TAG_PATTERN = r'<img[^>]+>'
    
    @staticmethod
    def extract_image_uris(text: str) -> list:
        """Extract image `title` values from HTML `<img>` tags.

        Args:
            text: HTML text containing one or more `<img>` tags.

        Returns:
            list[str]: List of values extracted from the `title` attribute of
                matching `<img>` tags. Returns an empty list when `text` is
                falsy or no matches are found.
        """
        if not text:
            return []
        return re.findall(QTIImageExtractor.IMG_URI_PATTERN, text)
    
    @staticmethod
    def extract_image_sources(text: str) -> list:
        """Extract the `src` attribute values from `<img>` tags.

        Args:
            text: HTML text containing one or more `<img>` tags.

        Returns:
            list[str]: List of `src` attribute values. Returns an empty list when
                `text` is falsy or no matches are found.
        """
        if not text:
            return []
        return re.findall(QTIImageExtractor.IMG_SRC_PATTERN, text)
    
    @staticmethod
    def extract_image_with_dimensions(img_tag: str) -> dict:
        """Parse a single `<img>` tag and extract common attributes.

        Args:
            img_tag: HTML snippet containing an `<img .../>` tag.

        Returns:
            dict: Dictionary with keys: ``src``, ``filename`` (from the
                `title` attribute), ``width`` and ``height``. Values are
                strings or ``None`` when an attribute is missing.
        """
        img_data = {'src': None, 'filename': None, 'width': None, 'height': None}
        
        # Extract src attribute
        src_pattern = r'src=["\']([^"\']+)["\']'
        src_match = re.search(src_pattern, img_tag)
        if src_match:
            img_data['src'] = src_match.group(1)
        
        # Extract title attribute (filename)
        title_pattern = r'title=["\']([^"\']+)["\']'
        title_match = re.search(title_pattern, img_tag)
        if title_match:
            img_data['filename'] = title_match.group(1)
        
        # Extract width attribute
        width_pattern = r'width=["\']([^"\']+)["\']'
        width_match = re.search(width_pattern, img_tag)
        if width_match:
            img_data['width'] = width_match.group(1)
        
        # Extract height attribute
        height_pattern = r'height=["\']([^"\']+)["\']'
        height_match = re.search(height_pattern, img_tag)
        if height_match:
            img_data['height'] = height_match.group(1)
        
        return img_data
    
    @staticmethod
    def collect_all_images_from_question(question) -> set:
        """Collect unique image `title` references used in a question.

        The function inspects the problem statement and each option to
        gather image `title` values (as produced by
        :func:`extract_image_uris`).

        Args:
            question: Question-like object exposing `get_problem_statement()` and
                `get_options()` methods.

        Returns:
            set[str]: Set of unique image title strings referenced by the
                question.
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
    """Utility class for locating image files in the file system.

    The locator implements naive search strategies to find an image file
    starting from a directory. It is not intended to be exhaustive but
    is sufficient for locating image files bundled alongside the source
    markdown files in this project.
    """
    
    @staticmethod
    def find_image(image_filename: str, search_start_dir: Path) -> Path:
        """Search for `image_filename` starting at `search_start_dir`.

        The function first checks `search_start_dir` directly and then
        inspects its immediate children directories. It returns the first
        matching `Path` found or ``None`` when the file cannot be
        located.

        Args:
            image_filename: File name of the image to search for.
            search_start_dir: Directory from which to begin the search.

        Returns:
            pathlib.Path | None: Path to the found image file, or ``None`` if not found.
        """
        # Check in the current directory
        current_path = search_start_dir / image_filename
        if current_path.exists():
            return current_path

        # Search in immediate subdirectories
        for parent in search_start_dir.iterdir():
            if parent.is_dir():
                recursive_path = parent / image_filename
                if recursive_path.exists():
                    return recursive_path

        return None
    
    @staticmethod
    def locate_images(image_filenames: set, search_dir: Path) -> dict:
        """Locate multiple image files under `search_dir`.

        Args:
            image_filenames: Set of image file names to search for.
            search_dir: Directory from which to begin the search for each file.

        Returns:
            tuple[dict, set]: A tuple `(found, missing)` where `found` is a mapping from
                image filename to its located `pathlib.Path`, and `missing` is
                a set of filenames that could not be found.
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
