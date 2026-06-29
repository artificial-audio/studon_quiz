# Copyright (c) 2026 Friedrich-Alexander-Universität Erlangen-Nürnberg
# SPDX-License-Identifier: MIT

import re
import os
import random
from loguru import logger
import mistune
from typing import Any, Optional
from typing import Any, Dict, List

class MarkdownReader:
    """Utility for parsing Markdown files into structured text pieces.

    The class uses `mistune` to produce an AST for the input Markdown file
    and exposes convenience methods to extract common question fields used
    by the converter (attributes, headings, summary, problem statement,
    options, feedback and hint sections).

    Args:
        fname: Path to the markdown file to parse.
    """

    def __init__(self, fname: str) -> None:
        self._fname = fname
        self._ast_tree: List[Dict[str, Any]] | None = None
        try:
            with open(self._fname, "r", encoding='UTF-8') as f:
                self._content = f.read()
                # Enable table plugin for markdown table support
                md = mistune.create_markdown(renderer='ast', plugins=['table'])
                # Protect ALL LaTeX (both inline and display) from mistune parsing
                self._content_n = self.protect_latex(self._content)
                self._ast_tree = md(self._content_n)
            logger.debug(f"Successfully parsed markdown file: {self._fname}")
        except Exception as e:
            logger.error(f"Failed to read file '{self._fname}': {e}")
            raise RuntimeError(f"Failed to read file '{self._fname}': {e}") from e
    
    def protect_latex(self, content: str) -> str:
        """Protect all LaTeX (inline and display) from Markdown processing.

        This method protects LaTeX expressions from being parsed by mistune
        by replacing them with plaintext placeholders using double-brace format
        (e.g., {{QTILATEX_INLINE_0}}) which mistune won't special-case.

        LaTeX expressions are stored in a placeholder map and restored later
        by _ast_to_text when processing the AST.

        Args:
            content: Markdown content possibly containing LaTeX expressions.

        Returns:
            str: Content with LaTeX protected via placeholders.
        """
        placeholder_map = {}
        placeholder_idx = 0
        result = content
        
        # First protect display math ($$...$$) to avoid matching inside it when looking for inline math
        display_pattern = r'\$\$(.*?)\$\$'
        
        def replace_display(match):
            nonlocal placeholder_idx
            math_content = match.group(1)
            # Use double-brace placeholder that won't trigger Markdown parsing
            placeholder = f"{{{{QTILATEX_DISPLAY_{placeholder_idx}}}}}"
            placeholder_map[placeholder] = f"$${math_content}$$"
            placeholder_idx += 1
            return placeholder
        
        result = re.sub(display_pattern, replace_display, result, flags=re.DOTALL)
        
        # Then protect inline math ($...$), being careful not to match display math delimiters
        # Use negative lookbehind/lookahead for $ to avoid $$
        inline_pattern = r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)'
        
        def replace_inline(match):
            nonlocal placeholder_idx
            math_content = match.group(1)
            # Use double-brace placeholder that won't trigger Markdown parsing
            placeholder = f"{{{{QTILATEX_INLINE_{placeholder_idx}}}}}"
            placeholder_map[placeholder] = f'<span class="latex">{math_content}</span>'
            placeholder_idx += 1
            return placeholder
        
        result = re.sub(inline_pattern, replace_inline, result, flags=re.DOTALL)
        
        # Store placeholder map for later restoration
        self._latex_placeholder_map = placeholder_map
        
        return result
        return result

    def replace_latex(self, content: str) -> str:
        """Replace single-dollar LaTeX inline math with a span element.

        This converts `$math$` occurrences to
        `<span class="latex">math</span>` while avoiding display math
        (`$$...$$`). The function is a best-effort textual transform and
        does not perform LaTeX validation.

        Args:
            content: Markdown content possibly containing inline LaTeX.

        Returns:
            str: Transformed content with inline LaTeX wrapped in a span.
        """
        return re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$', r'<span class="latex">\1</span>', content)

    def get_attrs(self) -> Dict[str, str]:
        """Extract leading key:value attributes from the top of the file.

        The method walks the AST until the first heading and collects
        any paragraph lines formatted as `key: value` into a dictionary.

        Returns:
            Dict[str, str]: Mapping of attribute names to their string values.
        """
        attr: Dict[str, str] = {}
        for element in self._ast_tree:
            if element['type'] == 'heading':
                break
            if element['type'] == 'paragraph':
                for child in element['children']:
                    try:
                        attr_text = child['raw'].split(':')
                        if len(attr_text) == 2:
                            attr[attr_text[0].lstrip()] = attr_text[1].lstrip()
                    except Exception as e:
                        logger.debug(f"Failed to parse attribute: {e}")
        logger.debug(f"Extracted attributes: {attr}")
        return attr

    def get_headings(self, level: int) -> List[str]:
        """Return all headings at the given markdown level.

        Args:
            level: Heading level to filter (1 for '#', 2 for '##', etc.).

        Returns:
            List[str]: A list of heading text strings in document order.
        """
        headings: List[str] = []
        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level:
                headings.append(element['children'][0]['raw'])
        logger.debug(f"Found {len(headings)} headings at level {level}")
        return headings

    def get_description(self, level: int, offset: int) -> str:
        """Extract the paragraph/inline content that follows a heading.

        The function locates the `offset`-th heading at the given
        `level` and returns the textual content between that heading and
        the next heading of the same or higher level.

        Args:
            level: Heading level to search.
            offset: Zero-based index of the matching heading occurrence.

        Returns:
            str: Concatenated text content belonging to the heading section.
        """
        description: str = ""
        ctr = 0
        start_recording = False
        content = []

        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level and not start_recording:
                if ctr == offset:
                    start_recording = True
                    logger.debug(f"Started recording description at heading offset {offset}")
                ctr += 1
                continue
            elif element['type'] == 'heading' and start_recording:
                logger.debug("Stopped recording description")
                break
            if start_recording:
                try:
                    if element['type'] == 'blank_line':
                        # Skip blank lines between paragraphs - they're structural
                        pass
                    elif element['type'] == 'paragraph':
                        # Preserve paragraph as a separate element to maintain boundaries
                        content.append(element)
                    elif element['type'] == 'list':
                        # Append list node itself so it can be converted to HTML by _list_to_html()
                        content.append(element)
                    elif element['type'] == 'block_html':
                        # Append HTML blocks (e.g., protected display math) as raw content
                        content.append(element)
                    elif 'children' in element:
                        content.extend(element['children'])
                except Exception as e:
                    logger.debug(f"Failed to process element: {e}")
        description = self._ast_to_text(content)
        return description

    def _ast_to_text(self, ast_nodes: List[Dict[str, Any]]) -> str:
        """Convert a list of AST nodes into HTML text.

        Supports text nodes, line breaks, lists, paragraphs, emphasis/strong nodes,
        inline HTML, softbreaks, and raw content. Lists are converted to proper 
        <ul> or <ol> HTML tags to match ILIAS QTI format expectations.
        Paragraphs are wrapped in <p> tags to preserve paragraph boundaries.

        Strong and emphasis nodes that contain LaTeX placeholders are
        unwrapped (without markup) to restore the placeholder content.

        Restores display math from protected placeholder format ({{QTILATEX_*}}).

        Args:
            ast_nodes: A list of nodes produced by the `mistune` AST renderer.

        Returns:
            str: The joined HTML representation of the nodes.
        """
        retStr = ''
        for node in ast_nodes:
            if node['type'] == 'text':
                content = node['raw']
                # Restore LaTeX from placeholder format
                if hasattr(self, '_latex_placeholder_map'):
                    for placeholder, original in self._latex_placeholder_map.items():
                        content = content.replace(placeholder, original)
                retStr += content
            elif node['type'] == 'paragraph':
                # Wrap paragraph content in <p> tags to preserve paragraph boundaries
                if 'children' in node:
                    para_content = self._ast_to_text(node['children'])
                    retStr += f'<p>{para_content}</p>\n'
            elif node['type'] in ('strong', 'emphasis', 'em'):
                # Strong/emphasis nodes might contain LaTeX placeholders (when __text__ got escaped).
                # Just process their children without adding markup.
                if 'children' in node:
                    retStr += self._ast_to_text(node['children'])
            elif node['type'] == 'block_html':
                # Restore display math from placeholder format
                if hasattr(self, '_latex_placeholder_map'):
                    content = node['raw']
                    for placeholder, original in self._latex_placeholder_map.items():
                        content = content.replace(placeholder, original)
                    retStr += content
                else:
                    retStr += node.get('raw', '')
            elif node['type'] == 'linebreak':
                retStr += '\n'
            elif node['type'] == 'softbreak':
                # Softbreaks in inline content become spaces in HTML
                retStr += ' '
            elif node['type'] == 'list':
                # Convert list nodes to HTML <ul> or <ol> tags
                retStr += self._list_to_html(node)
            elif node['type'] == 'list_item':
                retStr += self._unwrap_list_to_text(node, 0)
            elif node['type'] == 'inline_html':
                content = node['raw']
                # Restore LaTeX from placeholder format
                if hasattr(self, '_latex_placeholder_map'):
                    for placeholder, original in self._latex_placeholder_map.items():
                        content = content.replace(placeholder, original)
                retStr += content
            elif node['type'] == 'blank_line':
                # Blank lines are structural; skip them in inline context
                pass
            elif node['type'] in ('block_code', 'code_block') or 'raw' in node:
                # Preserve raw content (including LaTeX with backslashes)
                retStr += node.get('raw', '')
        return retStr

    def _list_to_html(self, node: Dict[str, Any]) -> str:
        """Convert a list AST node to HTML <ul> or <ol> tags.

        Args:
            node: AST node of type 'list'.

        Returns:
            str: HTML string with <ul>/<ol> and <li> tags.
        """
        is_ordered = node.get('ordered', False)
        tag = 'ol' if is_ordered else 'ul'
        html = f'<{tag}>\n'
        
        for item in node['children']:
            if item['type'] == 'list_item':
                html += '<li>'
                # Process the list item content
                for child in item['children']:
                    if child['type'] == 'block_text':
                        # Recursively process block_text children to preserve LaTeX
                        html += self._ast_to_text(child['children'])
                    elif child['type'] == 'list':
                        # Handle nested lists
                        html += self._list_to_html(child)
                html += '</li>\n'
        
        html += f'</{tag}>\n'
        return html


    def _unwrap_list_to_text(self, node: Dict[str, Any], tabCount: int) -> str:
        """Recursively flatten list AST nodes into text with indentation.

        Args:
            node: AST node representing a list or list item.
            tabCount: Current indentation level (number of leading tabs).

        Returns:
            str: Flattened string representation of the list subtree.
        """
        retStr = ''
        for child in node['children']:
            if child['type'] == 'block_text':
                # Process all children of block_text (text, inline_html, etc.) to preserve LaTeX
                retStr += self._ast_to_text(child['children']) + '\n'
            elif child['type'] == 'list':
                tabCount += 1
                for sublist in child['children']:
                    retStr += '\t' * tabCount + self._unwrap_list_to_text(sublist, tabCount) + '\n'
            elif child['type'] == 'list_item':
                retStr += self._unwrap_list_to_text(child, tabCount)
        return retStr
    
    def get_q_type(self) -> str | None:
        """Return the `type` attribute declared at the top of the file.

        Returns:
            str | None: The value of the `type` attribute or None if not present.
        """
        attr = self.get_attrs()
        q_type = attr.get('type')
        if q_type:
            logger.debug(f"Question type: {q_type}")
        return q_type

    def get_title(self) -> str | None:
        """Return the first level-1 heading as the question title.

        Returns:
            str | None: Title string or None if no level-1 heading exists.
        """
        titles = self.get_headings(1)
        title = titles[0] if titles else None
        if title:
            logger.debug(f"Question title: {title}")
        return title

    def get_summary(self) -> str:
        """Return the top-level description (summary) following the title.

        Returns:
            str: Summary text for the question.
        """
        description = self.get_description(1, 0)
        logger.debug(f"Summary length: {len(description)} chars")
        return description

    def get_problem_statement(self) -> str:
        """Locate and return the problem statement under level-2 headings.

        The method searches level-2 headings for one that matches
        /quiz/i and returns its section text with Obsidian-style image
        links converted to inline `<img>` HTML.

        Returns:
            str: Problem statement text or empty string if not found.
        """
        titles = self.get_headings(2)
        pattern = r"quiz"
        index = next((i for i, s in enumerate(titles) if re.search(pattern, s, re.IGNORECASE)), None)
        if index is not None:
            statement = self.get_description(2, index)
            logger.debug(f"Problem statement found at index {index}")
            statement = replace_obsidian_images(statement)
            return statement
        logger.warning("No problem statement found")
        return ""

    def get_answer_params(self) -> Dict[str, Any]:
        """Extract numeric answer parameters from a level-2 'Answer' section.

        Parses list items formatted as ``Key: Value`` under the Answer
        heading and returns them as a dictionary with normalised keys.

        Returns:
            Dict[str, Any]: Mapping with possible keys: ``correct_answer``,
                ``tolerance``, ``points``, ``maxchars``.
        """
        level = 2
        pattern = r"answer"
        recording = False
        params: Dict[str, Any] = {}
        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level:
                if re.search(pattern, element['children'][0]['raw'], re.IGNORECASE) and not recording:
                    recording = True
                    logger.debug("Found answer section")
                    continue
                elif recording:
                    break
            if recording and element['type'] == 'list':
                for item in element['children']:
                    for child in item['children']:
                        if child['type'] in ('block_text', 'paragraph'):
                            raw = ''.join(c.get('raw', '') for c in child['children'])
                            parts = raw.split(':', 1)
                            if len(parts) == 2:
                                key = parts[0].strip().lower().replace(' ', '_')
                                val = parts[1].strip()
                                # Map friendly names to internal keys
                                key_map = {
                                    'correct_answer': 'correct_answer',
                                    'tolerance': 'tolerance',
                                    'points': 'points',
                                    'max_characters': 'maxchars',
                                }
                                mapped = key_map.get(key, key)
                                params[mapped] = val
        logger.debug(f"Extracted answer params: {params}")
        return params

    def get_essay_params(self) -> Dict[str, Any]:
        """Extract essay-specific parameters from a level-2 'Settings' section.

        Parses list items formatted as ``Key: Value`` under the Settings
        heading and returns a dict mapping parameter names to their values.

        Returns:
            Dict[str, Any]: Mapping with possible keys: ``maxpoints``,
                ``maxchars``.
        """
        level = 2
        pattern = r"settings"
        recording = False
        params: Dict[str, Any] = {}
        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level:
                if re.search(pattern, element['children'][0]['raw'], re.IGNORECASE) and not recording:
                    recording = True
                    logger.debug("Found essay settings section")
                    continue
                elif recording:
                    break
            if recording and element['type'] == 'list':
                for item in element['children']:
                    for child in item['children']:
                        if child['type'] in ('block_text', 'paragraph'):
                            raw = ''.join(c.get('raw', '') for c in child['children'])
                            parts = raw.split(':', 1)
                            if len(parts) == 2:
                                key = parts[0].strip().lower().replace(' ', '_')
                                val = parts[1].strip()
                                # Map friendly names to internal keys
                                key_map = {
                                    'max_points': 'maxpoints',
                                    'max_characters': 'maxchars',
                                }
                                mapped = key_map.get(key, key)
                                params[mapped] = val
        logger.debug(f"Extracted essay params: {params}")
        return params

    def get_options(self) -> List[Dict[str, Any]]:
        """Extract the options block from the markdown as a list of dicts.

        The function searches for a level-2 heading containing the word
        "options" and then parses either a list or table into option
        dictionaries. Each option dictionary may contain answer text and
        additional key/value attributes (score, feedback, etc).

        Returns:
            List[Dict[str, Any]]: List of option dictionaries.
        """
        level = 2
        pattern = r"options"
        options = []
        found_options = False
        
        for i, element in enumerate(self._ast_tree):
            if element['type'] == 'heading' and element['attrs']['level'] == level and re.search(pattern, element['children'][0]['raw'], re.IGNORECASE):
                found_options = True
                logger.debug("Found options section")
                # Skip blank lines and find table or list
                j = i + 1
                while j < len(self._ast_tree) and self._ast_tree[j]['type'] == 'blank_line':
                    j += 1
                
                if j < len(self._ast_tree):
                    next_elem = self._ast_tree[j]
                    if next_elem['type'] == 'table':
                        # Parse table format
                        options = self._parse_options_table(next_elem)
                    elif next_elem['type'] == 'list':
                        # Parse list format (legacy)
                        for option in next_elem['children']:
                            options.append(self._get_option_dict(option, 0))
                break
            elif found_options and element['type'] == 'heading':
                break
                
        logger.debug(f"Extracted {len(options)} options")
        return options

    def _parse_options_table(self, table_node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse options from a markdown table AST node.

        Expected table structure:
        | Option | Score | Feedback |
        |--------|-------|----------|
        | Option text | score | feedback text |

        Args:
            table_node: AST node of type 'table'.

        Returns:
            List[Dict[str, Any]]: List of parsed option dictionaries with keys 
                'ans', 'Score' (uppercase for compatibility), and 'Remark'.
        """
        options = []
        
        # Find table_body in children
        table_body = None
        for child in table_node.get('children', []):
            if child['type'] == 'table_body':
                table_body = child
                break
        
        if not table_body:
            logger.debug("No table body found")
            return options
        
        # Parse each table_row in the body
        for row_node in table_body.get('children', []):
            if row_node['type'] != 'table_row':
                continue
            
            cells = row_node.get('children', [])
            if len(cells) < 3:
                continue
            
            # Extract cell contents
            cell_contents = []
            for cell in cells:
                if cell['type'] == 'table_cell':
                    # Extract text from cell children
                    cell_text = self._ast_to_text(cell.get('children', []))
                    cell_contents.append(cell_text.strip())
            
            if len(cell_contents) >= 3:
                # Columns: Option text, Score, Feedback
                # Use capitalized 'Score' and 'Remark' for compatibility with question_bank
                option_dict = {
                    'ans': replace_obsidian_images(cell_contents[0]),
                    'Score': cell_contents[1],
                    'Remark': cell_contents[2]
                }
                options.append(option_dict)
        
        logger.debug(f"Parsed {len(options)} options from table")
        return options

        
    def _get_option_dict(self, node: Dict[str, Any], tabCount: int) -> Dict[str, Any]:
        """Convert a list item AST node into an option dictionary.

        Args:
            node: AST node for the list item.
            tabCount: Current indentation depth within nested lists.

        Returns:
            Dict[str, Any]: Dictionary containing parsed option fields such as 
                `ans`, `score`, `feedback`, etc.
        """
        dictData: Dict[str, Any] = {}
        for child in node['children']:
            if child['type'] in ('block_text', 'paragraph'):
                try:
                    if tabCount == 0:
                        dictData['ans'] = ''.join(c['raw'] for c in child['children'] if 'raw' in c)
                        dictData['ans'] = replace_obsidian_images(dictData['ans'])
                    else:
                        # Extract all raw text from all children (handles LaTeX and inline HTML)
                        full_text = ''.join(c['raw'] for c in child['children'] if 'raw' in c)
                        attr_text = full_text.split(':', 1)  # Split only on first colon
                        if len(attr_text) == 2:
                            dictData[attr_text[0].lstrip()] = attr_text[1].lstrip()
                except Exception as e:
                    logger.debug(f"Failed to parse option attribute: {e}")
            elif child['type'] == 'list':
                tabCount += 1
                for sublist in child['children']:
                    data = self._get_option_dict(sublist, tabCount)
                    dictData.update(data)
            elif child['type'] == 'list_item':
                dictData = self._get_option_dict(child, tabCount)
        return dictData

    def get_feedback(self) -> Dict[str, str]:
        """Extract feedback sections under a level-2 `Feedback` heading.

        Returns:
            Dict[str, str]: Mapping with keys "Correct" and/or "Wrong" to their 
                respective feedback text.
        """
        level = 2
        feedback: Dict[str, str] = {}
        recordFeedback = False
        pattern = r'feedback'
        patternRightFeedback = r'Correct'
        patternWrongFeedback = r'Wrong'
        nextFeedbackType = None
        content = []
        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level and re.search(pattern, element['children'][0]['raw'], re.IGNORECASE):
                recordFeedback = True
                logger.debug("Found feedback section")
                continue
            if recordFeedback and element['type'] == 'heading' and element['attrs']['level'] <= level:
                if nextFeedbackType:
                    feedback[nextFeedbackType] = self._ast_to_text(content)
                break
            if recordFeedback:
                if element['type'] == 'heading' and re.search(patternRightFeedback, element['children'][0]['raw'], re.IGNORECASE):
                    if nextFeedbackType:
                        feedback[nextFeedbackType] = self._ast_to_text(content)
                    nextFeedbackType = "Correct"
                    logger.debug("Found correct feedback section")
                    content = []
                    continue
                elif element['type'] == 'heading' and re.search(patternWrongFeedback, element['children'][0]['raw'], re.IGNORECASE):
                    if nextFeedbackType:
                        feedback[nextFeedbackType] = self._ast_to_text(content)
                    nextFeedbackType = "Wrong"
                    logger.debug("Found wrong feedback section")
                    content = []
                    continue
                if nextFeedbackType:
                    try:
                        if element['type'] == 'blank_line':
                            content.append({'type': 'linebreak'})
                        elif element['type'] == 'list':
                            # Append list node itself so it can be converted to HTML by _list_to_html()
                            content.append(element)
                        elif 'children' in element:
                            content.extend(element['children'])
                    except Exception as e:
                        logger.debug(f"Failed to process feedback element: {e}")
        
        # Save any pending feedback at the end of the loop
        if nextFeedbackType:
            feedback[nextFeedbackType] = self._ast_to_text(content)
        
        # Convert Obsidian-style image links to HTML <img> tags in all feedback
        for key in feedback:
            feedback[key] = replace_obsidian_images(feedback[key])
        
        logger.debug(f"Extracted {len(feedback)} feedback sections")
        return feedback

    def get_hint(self) -> Dict[str, Any]:
        """Extract hint and penalty information from a level-2 `Hint` section.

        Returns:
            Dict[str, Any]: Dictionary containing at least the key `hint` and `penalty`.
        """
        level = 2
        hint: Dict[str, Any] = {'penalty': 0}
        recordHint = False
        pattern = r'hint'
        content = []
        nextFieldType = 'hint'
        patternPenalty = r'(Penalty|Point)'
        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level and re.search(pattern, element['children'][0]['raw'], re.IGNORECASE):
                recordHint = True
                logger.debug("Found hint section")
                continue
            if recordHint:
                if element['type'] == 'heading' and re.search(patternPenalty, element['children'][0]['raw'], re.IGNORECASE):
                    if nextFieldType:
                        hint[nextFieldType] = self._ast_to_text(content)
                    nextFieldType = "penalty"
                    logger.debug("Found penalty section")
                    content = []
                    continue
                if element['type'] == 'heading' and nextFieldType == 'penalty':
                    break
                if recordHint:
                    try:
                        if element['type'] == 'blank_line':
                            content.append({'type': 'linebreak'})
                        else:
                            content.extend(element['children'])
                    except Exception as e:
                        logger.debug(f"Failed to process hint element: {e}")
        if content:
            hint[nextFieldType] = self._ast_to_text(content)
        if isinstance(hint['penalty'], str):
            hint['penalty'] = int(hint['penalty'].lstrip())
        logger.debug(f"Hint penalty: {hint['penalty']}")
        return hint

def replace_obsidian_images(text):
    """Convert Obsidian-style image links into HTML <img> tags.

    Supported input formats inside the double brackets include:
    - `filename.ext`
    - `filename.ext|width`
    - `filename.ext|widthxheight`

    The function generates a randomized `src` identifier and returns
    HTML `<img>` element (without wrapping <p> tags, as the caller
    will handle paragraph formatting).

    Args:
        text: Input text potentially containing Obsidian-style image links.

    Returns:
        str: Text with Obsidian image links replaced by HTML `<img>` tags.
    """
    def replacer(match):
        content = match.group(1)
        
        # Parse the format: ![[filename.ext]] or ![[filename.ext|width]] or ![[filename.ext|widthxheight]]
        if '|' in content:
            filename, dimensions = content.split('|', 1)
            filename = filename.strip()
            dimensions = dimensions.strip()
            
            # Check if it's width x height or just width
            if 'x' in dimensions.lower():
                parts = dimensions.lower().split('x')
                width = parts[0].strip()
                height = parts[1].strip()
            else:
                # Single value means width only
                width = dimensions
                height = "194"  # Keep default height
        else:
            filename = content.strip()
            width = "259"
            height = "194"
        
        # Generate random src identifier
        random_num = random.randint(10000, 99999)
        new_src = f"{random_num}_mob_{random_num}"
        
        # Return just the img tag without wrapping <p> tags
        # The caller will handle paragraph formatting
        return f'<img alt="" height="{height}" src="il_{new_src}" title="{filename}" width="{width}" />'

    pattern = r'!\[\[([^\]]+?)\]\]'
    
    return re.sub(pattern, replacer, text)