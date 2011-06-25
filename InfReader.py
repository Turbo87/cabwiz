class InfReader:
    def __init__(self):
        self.__data = {}
        
    def read_file(self, file):
        section = ''
        for line in file:
            pos = line.find(';')
            if pos != -1:
                line = line[:pos]
                
            line = line.strip()
            if line == "":
                continue
            
            if line.startswith('[') and line.endswith(']'):
                section = line.lstrip('[').rstrip(']')
                self.__data[section] = []
            elif section != '':
                self.__data[section].append(line)
                
        if not self.__check_sections():
            return False
        
        return True
        
    def read(self, path):
        with open(path, 'r') as file:
            return self.read_file(file)
        
    def __check_section(self, section):
        if self.has_section(section):
            return True
        
        print 'Error: Section "' + section + '" is missing'
        return False
    
    def __check_sections(self):
        return (self.__check_section('Version') and
                self.__check_section('CEStrings') and
                self.__check_section('DefaultInstall') and
                self.__check_section('DestinationDirs'))

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
