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
