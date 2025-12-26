import re
import mistune

class MarkdownReader:
    def __init__(self, fname:str) -> None:
        self._fname = fname
        self._ast_tree:dict = None 
        try:
            with open(self._fname, "r", encoding='UTF-8') as f:
                self._content = f.read()
                renderer = mistune.create_markdown(renderer='ast')
                self._ast_tree = renderer(self._content)
        except Exception as e:            
            raise RuntimeError(f"Failed to read file '{self._fname}': {e}") from e
    
    def get_attrs(self) -> dict[str, str]:
        attr:dict[str,str] = {}
        for element in self._ast_tree:
            if(element['type'] == 'heading'):
                break
            if(element['type'] == 'paragraph'):
                for child in element['children']:
                    try:
                        attr_text = child['raw'].split(':')
                        if len(attr_text) == 2:
                            attr[attr_text[0].lstrip()] = attr_text[1].lstrip()
                    except:
                        pass
        return attr

    def get_headings(self, level:int):
        headings:list[str] = []

        for element in self._ast_tree:
            if(element['type'] == 'heading' and element['attrs']['level'] == level):
                headings.append(element['children'][0]['raw'])

        return headings

    def get_description(self,level:int, offset:int):
        description:str = None
        ctr = 0
        start_recording = False
        content = []

        for element in self._ast_tree:
            if(element['type'] == 'heading' and element['attrs']['level'] == level and start_recording == False):
                if(ctr == offset):
                    start_recording = True
                ctr += 1
                continue
            elif(element['type'] == 'heading' and start_recording == True):
                break
            if(start_recording):
                try:
                    if(element['type'] == 'blank_line'):
                        content.append({'type':'linebreak'})
                    else:
                        content.extend(element['children'])
                except:
                    pass
        description = self._ast_to_text(ast_nodes=content)
        return description

    def _ast_to_text(self, ast_nodes):
        retStr = ''
        for node in ast_nodes:
            if(node['type'] == 'text'):
                retStr += node['raw']
            elif(node['type'] == 'linebreak'):
                retStr += '\n'
            elif node['type'] == 'list_item':
                retStr += self._unwrap_list_to_text(node, tabCount=0)
        return retStr


    def _unwrap_list_to_text(self, node, tabCount):
        retStr = ''
        for child in node['children']:
            if (child['type'] == 'block_text'):
                retStr += child['children'][0]['raw'] +'\n'
            elif child['type'] == 'list':
                tabCount += 1
                for sublist in child['children']:
                    retStr += '\t'*tabCount+self._unwrap_list_to_text(sublist, tabCount) + '\n'
            elif child['type'] == 'list_item':
                retStr += self._unwrap_list_to_text(child, tabCount=tabCount)
        return retStr
    
    def get_q_type(self):
        attr = self.get_attrs()
        q_type = None
        if 'type' in attr.keys():
            q_type = attr['type']
        return q_type

    def get_title(self):
        title = None
        titles = self.get_headings(1)
        if len(titles)>0:
            title = titles[0]
        return title

    def get_summary(self):
        description = self.get_description(1,0)
        return description

    def get_problem_statement(self):
        titles = self.get_headings(2)
        pattern = r"quiz"

        index = next( (i for i, s in enumerate(titles) if re.search(pattern, s, re.IGNORECASE)), None)
        statement = self.get_description(2, index)
        return statement

    def get_options(self):
        level = 2
        pattern = r"options"
        build_opt_dict = False
        options = []
        for element in self._ast_tree:
            if(element['type'] == 'heading' and element['attrs']['level'] == level and re.search(pattern, element['children'][0]['raw'], re.IGNORECASE)):
                build_opt_dict = True
                continue
            elif(element['type'] == 'heading' and build_opt_dict == True):
                break
            if(build_opt_dict):
                if element['type'] == 'list':
                    for option in element['children']:
                        options.append( self._get_option_dict(option, 0))
        return options
        
    def _get_option_dict(self, node, tabCount):
        dictData = {}
        for child in node['children']:
            if (child['type'] == 'block_text'):
                try:
                    if tabCount == 0:
                        dictData['ans'] = child['children'][0]['raw']
                    else:
                        attr_text = child['children'][0]['raw'].split(':')
                        if len(attr_text) == 2:
                            dictData[attr_text[0].lstrip()] = attr_text[1].lstrip()
                except:
                    pass
            elif child['type'] == 'list':
                tabCount += 1
                for sublist in child['children']:
                    data = self._get_option_dict(sublist, tabCount) 
                    dictData |=data
            elif child['type'] == 'list_item':
                dictData = self._get_option_dict(child, tabCount=tabCount)
        return dictData


    def _get_feedback(self):
        pass
