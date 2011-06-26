import InfReader
import CabWriter
import shutil
import os

class InfCabGlue:
    def __init__(self, parameters):
        self.__parameters = parameters
        self.__inf = {}
        self.__dest = ''
        
    def __create_output_filename(self):
        filename = self.__inf['CEStrings']['AppName'].strip('"')
        
        if 'cpu-type' in self.__parameters:
            filename += '.' + self.__parameters['cpu-type']
        
        return filename + ".cab"
    
    def __parse_general(self, cab):
        if ('AppName' not in self.__inf['CEStrings'] or 
            'Provider' not in self.__inf['Version']):
            return False
        
        cab.AppName = self.__inf['CEStrings']['AppName'].strip('"')
        cab.Provider = self.__inf['Version']['Provider'].strip('"')
        return True
    
    def __parse_device_version(self, version):
        v = self.__inf['CEDevice'][version].split('.')
        
        if len(v) == 0:
            return None
        
        major = int(v[0]) 
        
        minor = 0
        if len(v) > 1:
            minor = int(v[1]) 
        
        return [major, minor]
    
    def __parse_device(self, cab):
        if ('ProcessorType' not in self.__inf['CEDevice'] or 
            'VersionMin' not in self.__inf['CEDevice'] or 
            'VersionMax' not in self.__inf['CEDevice']):
            return False
        
        cab.Architecture = int(self.__inf['CEDevice']['ProcessorType'])
        
        min = self.__parse_device_version('VersionMin')
        if not min: return False
        cab.VersionMin = min
        
        max = self.__parse_device_version('VersionMax')
        if not max: return False
        cab.VersionMax = max
        
        if 'BuildMax' in self.__inf['CEDevice']:
            cab.BuildMax = int(self.__inf['CEDevice']['BuildMax'], 16)
            
        return True
    
    def __parse_disk_names(self, cab):
        names = {}
        for id, value in self.__inf['SourceDisksNames'].iteritems():
            id = int(id)
            value = value.split(',')[-1]
            names[id] = value
            
        return names
    
    def __parse_setup_dll(self, cab):
        if ('CESetupDLL' not in self.__inf['DefaultInstall']):
            return False
        
        dll_in = self.__inf['DefaultInstall']['CESetupDLL']
        dll_out = self.__dest + CabWriter.munge_filename(dll_in, 999)
        shutil.copy(dll_in, dll_out)
        
        cab.SetupFile = dll_out
            
        return True
    
    def glue(self):
        print 'Reading INF file "' + self.__parameters['inf-file'] + '" ...'
        inf = InfReader.InfReader()
        
        if not inf.read(self.__parameters['inf-file']):
            return False
        
        self.__inf = inf.raw()
        if 'dest-dir' in self.__parameters: 
            self.__dest = self.__parameters['dest-dir']
            if not self.__dest.endswith('/'): self.__dest += '/'
            if not os.path.exists(self.__dest): os.mkdir(self.__dest)
        
        cab = CabWriter.CabWriter()
        if not self.__parse_general(cab): return False
        if not self.__parse_device(cab): return False
        names = self.__parse_disk_names(cab)
        self.__parse_setup_dll(cab)

        cab_file = self.__create_output_filename()
        if cab_file == "":
            return False
        
        print 'Writing CAB file to "' + self.__dest + cab_file + '" ...'
        if not cab.write(cab_file, self.__dest):
            return False
        
        return True