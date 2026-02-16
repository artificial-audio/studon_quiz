import re
from loguru import logger
import mistune
from typing import Any, Optional
from typing import Any, Dict, List

class MarkdownReader:
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
        return re.sub(r'(?<!\$)\$(?!\$)(.*)(?<!\$)\$', r'<span class="latex">\1</span>', content)

    def get_attrs(self) -> Dict[str, str]:
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
        headings: List[str] = []
        for element in self._ast_tree:
            if element['type'] == 'heading' and element['attrs']['level'] == level:
                headings.append(element['children'][0]['raw'])
        logger.debug(f"Found {len(headings)} headings at level {level}")
        return headings

    def get_description(self, level: int, offset: int) -> str:
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
        attr = self.get_attrs()
        q_type = attr.get('type')
        if q_type:
            logger.debug(f"Question type: {q_type}")
        return q_type

    def get_title(self) -> str | None:
        titles = self.get_headings(1)
        title = titles[0] if titles else None
        if title:
            logger.debug(f"Question title: {title}")
        return title

    def get_summary(self) -> str:
        description = self.get_description(1, 0)
        logger.debug(f"Summary length: {len(description)} chars")
        return description

    def get_problem_statement(self) -> str:
        titles = self.get_headings(2)
        pattern = r"quiz"
        index = next((i for i, s in enumerate(titles) if re.search(pattern, s, re.IGNORECASE)), None)
        if index is not None:
            statement = self.get_description(2, index)
            logger.debug(f"Problem statement found at index {index}")
            return statement
        logger.warning("No problem statement found")
        return ""

    def get_options(self) -> List[Dict[str, Any]]:
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
        dictData: Dict[str, Any] = {}
        for child in node['children']:
            if child['type'] == 'block_text':
                try:
                    if tabCount == 0:
                        dictData['ans'] = ''.join(c['raw'] for c in child['children'] if 'raw' in c)
                    else:
                        attr_text = child['children'][0]['raw'].split(':')
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
        level = 2
        hint: Dict[str, Any] = {'penalty': 0}
        recordHint = False
        pattern = r'hint'
        content = []
        nextFieldType = 'hint'
        patternPenalty = r'Penalty'
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