class InfReader:
    def __init__(self):
        self.__data = {}
        
    def read_file(self, file):
        section = ''
        for line in file:
            line = line.strip()
            if line.startswith(';'):
                continue
            
            if line.startswith('[') and line.endswith(']'):
                section = line.lstrip('[').rstrip(']')
                self.__data[section] = []
            elif section != '':
                self.__data[section].append(line)
        
    def read(self, path):
        with open(path, 'r') as file:
            self.read_file(file)
            
        file.close()
        
    def raw(self):
        return self.__data
    
    def has_section(self, section):
        return section in self.__data

    def get_section(self, section):
        return self.__data[section]

    def apply_replacement(self, replacement):
        new_sections = {}
        for section, content in self.__data.iteritems():
            new_content = []
            for line in content:
                new_content.append(line.replace('%' + replacement[0] + '%', replacement[1]))
                
            new_sections[section] = new_content
            
        self.__data = new_sections

    def apply_replacements(self, replacements):
        for replacement in replacements:
            self.apply_replacement(replacement)
