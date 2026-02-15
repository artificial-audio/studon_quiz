class McqSAQuestion:
    
    def __init__(self):
        
        self.mandatory_fields = {
            'type': 'mcq-sa',
            'title': None,
            'options':None,
            'problem_statement': None
        }
        
        self.optional_fields = {
            'summary': None,
            'feedback':None,
            'hint': None
        }
    
    
    def get_type(self):
        return self.mandatory_fields['type']
    
    def set_title(self, title):
        self.mandatory_fields['title'] = title
    
    def get_title(self):
        return self.mandatory_fields['title']
    
    def set_summary(self, summary):
        self.optional_fields['summary'] = summary
    
    def get_summary(self):
        return self.optional_fields['summary']
    
    def set_problem_statement(self, problem_statement):
        self.mandatory_fields['problem_statement'] = problem_statement
    
    def get_problem_statement(self):
        return self.mandatory_fields['problem_statement']
    
    def set_options(self, options):
        self.mandatory_fields['options'] = options
    
    def get_options(self):
        return self.mandatory_fields['options']
    
    def set_feedback(self, feedback):
        self.optional_fields['feedback'] = feedback
    
    def get_feedback(self):
        return self.optional_fields['feedback']
    
    def set_hint(self, hint):
        self.optional_fields['hint'] = hint
    
    def get_hint(self):
        return self.optional_fields['hint']

    def get_field_names(self):
        return list(self.mandatory_fields.keys()) + list(self.optional_fields.keys())
    
    def isValid(self):
        for field_name, field_value in self.mandatory_fields.items():
            if field_value is None:
                return False
        return True