import InfReader

class InfCabGlue:
    def __init__(self, parameters):
        self.__parameters = parameters
        self.__inf = {}
        
    def glue(self):
        print 'Reading INF file "' + self.__parameters['inf-file'] + '" ...'
        inf = InfReader.InfReader()
        
        if not inf.read(self.__parameters['inf-file']):
            return False
        
        self.__inf = inf.raw()
        
        return True