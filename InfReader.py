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
        
        self.__apply_replacements()
        self.__array_to_dict()
        
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

    def __read_replacements_section(self, section):
        replacements = []
        for line in self.get_section(section):
            line = line.split('=')
            if len(line) < 2:
                continue
            
            key = line[0].strip()
            value = line[1].strip()
            replacements.append([key, value])
    
        return replacements        
    
    def __read_replacements(self):
        # Read replacements from CEStrings section
        replacements = self.__read_replacements_section('CEStrings')
        
        # Read replacements from Strings section if it exists
        if self.has_section('Strings'):
            replacements.extend(self.__read_replacements_section('Strings'))
            
        # Return replacements array
        return replacements        

    def __apply_replacement(self, replacement):
        new_sections = {}
        for section, content in self.__data.iteritems():
            new_content = []
            for line in content:
                new_content.append(line.replace('%' + replacement[0] + '%', replacement[1]))
                
            new_sections[section] = new_content
            
        self.__data = new_sections
    
    def __apply_replacements(self):
        # Read replacement sections from INF file
        replacements = self.__read_replacements()
        
        # Apply replacements to themselves until none left
        found = True
        while found:
            found = False
            
            for replacement in replacements:
                for i in range(len(replacements)):
                    if replacement[0] in replacements[i][1]: 
                        found = True
                        replacements[i][1] = replacements[i][1].replace('%' + replacement[0] + '%', replacement[1]) 
    
        # Apply replacements to the other sections
        for replacement in replacements:
            self.__apply_replacement(replacement)
            
    def __array_section_to_dict(self, section, content):
        dict = {}
        for line in content:
            line = line.split('=')
            if len(line) < 2:
                continue
            
            key = line[0].strip()
            value = line[1].strip()
            dict[key] = value
        
        self.__data[section] = dict
            
    def __array_to_dict(self):
        for section, content in self.__data.iteritems():
            if (section.startswith('Version') or
                section.startswith('CEStrings') or
                section.startswith('Strings') or
                section.startswith('CEDevice') or
                section.startswith('SourceDisksNames') or
                section.startswith('SourceDisksFiles') or
                section.startswith('DefaultInstall') or
                section.startswith('DestinationDirs')):
                self.__array_section_to_dict(section, content)
                
