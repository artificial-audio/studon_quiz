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
                renderer = mistune.create_markdown(renderer='ast')
                self._content_n = self.replace_latex(self._content)
                self._ast_tree = renderer(self._content_n)
            logger.debug(f"Successfully parsed markdown file: {self._fname}")
        except Exception as e:
            logger.error(f"Failed to read file '{self._fname}': {e}")
            raise RuntimeError(f"Failed to read file '{self._fname}': {e}") from e
    
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
                        content.append({'type': 'linebreak'})
                    else:
                        content.extend(element['children'])
                except Exception as e:
                    logger.debug(f"Failed to process element: {e}")
        description = self._ast_to_text(content)
        return description

    def _ast_to_text(self, ast_nodes: List[Dict[str, Any]]) -> str:
        """Convert a list of AST nodes into plain text.

        Supports text nodes, line breaks, lists and inline HTML.

        Args:
            ast_nodes: A list of nodes produced by the `mistune` AST renderer.

        Returns:
            str: The joined textual representation of the nodes.
        """
        retStr = ''
        for node in ast_nodes:
            if node['type'] == 'text':
                retStr += node['raw']
            elif node['type'] == 'linebreak':
                retStr += '\n'
            elif node['type'] == 'list_item':
                retStr += self._unwrap_list_to_text(node, 0)
            elif node['type'] == 'inline_html':
                retStr += node['raw']
        return retStr

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
                retStr += child['children'][0]['raw'] + '\n'
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

    def get_options(self) -> List[Dict[str, Any]]:
        """Extract the options block from the markdown as a list of dicts.

        The function searches for a level-2 heading containing the word
        "options" and then parses the following list into option
        dictionaries. Each option dictionary may contain answer text and
        additional key/value attributes.

        Returns:
            List[Dict[str, Any]]: List of option dictionaries.
        """
        level = 2
        pattern = r"options"
        build_opt_dict = False
        options = []
        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level and re.search(pattern, element['children'][0]['raw'], re.IGNORECASE):
                build_opt_dict = True
                logger.debug("Found options section")
                continue
            elif element['type'] == 'heading' and build_opt_dict:
                break
            if build_opt_dict and element['type'] == 'list':
                for option in element['children']:
                    options.append(self._get_option_dict(option, 0))
        logger.debug(f"Extracted {len(options)} options")
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
                        else:
                            content.extend(element['children'])
                    except Exception as e:
                        logger.debug(f"Failed to process feedback element: {e}")
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

    The function generates a randomized `src` identifier and returns an
    HTML paragraph containing an `<img>` element with `title`, `src`,
    `width` and `height` attributes.

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
        
        return f'<p><img alt="" height="{height}" src="il_{new_src}" title="{filename}" width="{width}" /></p>'

    pattern = r'!\[\[([^\]]+?)\]\]'
    
    return re.sub(pattern, replacer, text)