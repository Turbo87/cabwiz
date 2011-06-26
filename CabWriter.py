import subprocess
import struct

def munge_filename(munged, extension):
    munged = munged.split("/")[-1].split(".")[0]
    munged = munged.replace(" ", "")[:8].zfill(8)
    munged = '%s.%03d' % (munged, extension)
    return munged
    
class CabWriter:
    def __init__(self):
        self.AppName = ''
        self.Provider = ''
        self.Unsupported = ''
        self.Architecture = 0
        self.MaxVersion = [0, 0]
        self.MaxBuild = 0
        self.MinVersion = [0, 0]
        self.MinBuild = 0
        self.Strings = []
        self.Dirs = []
        self.Files = []
        self.SetupFile = ''
        self.RegHives = []
        self.RegKeys = []
        self.Links = []
        
    def __get_manifest(self):
        # Header.
        offset = 100;
    
        # Application.
        application_offset = offset
        application = self.AppName + "\0"
        offset += len(application)
    
        # Provider.
        provider_offset = offset
        provider = self.Provider + "\0"
        offset += len(provider)
    
        # Unsupported platforms.
        unsupported_offset = offset
        unsupported = self.Unsupported + '\0' if self.Unsupported != "" else ""
        offset += len(unsupported)
    
        # Strings.
        strings_offset = offset
        strings = ''
        for i in range(len(self.Strings)):
            string = self.Strings[i]
            strings += struct.pack('<HH', i, len(string) + 1)
            strings += string + '\0'
        
        offset += len(strings)
    
        # Directories.
        directories_offset = offset;
        directories = ''
        for i in range(len(self.Dirs)):
            dir = self.Dirs[i]
            directories += struct.pack('<HH', directory_id, 2 * len(dir[1]))
            for id in dir[1]:
                directories += struct.pack('<H', id)
        
        offset += len(directories)
    
        # Files.
        files_offset = offset;
        files = '';
        for i in range(len(self.Files)):
            file = self.Files[i]
            
            filename = path
            filename = file[0].split("/")[-1]

            files += struct.pack('<HHHIH', i, file[1], i, 0, 1 + len(filename))
            files += file + '\0'
        
        offset += len(files)
    
        # RegHives.
        reghives_offset = offset
        reghives = ''
        offset += len(reghives)
    
        # RegKeys.
        regkeys_offset = offset
        regkeys = ''
        offset += len(regkeys)
    
        # Links.
        links_offset = offset
        links = ''
        offset += len(links)
    
        # Header.
        length = offset;
    
        header = 'MSCE'
        header += struct.pack('<IIIIIIIIIII', 0, length, 0, 1, self.Architecture, 
                              self.MinVersion[0], self.MinVersion[1], 
                              self.MaxVersion[0], self.MaxVersion[1], 
                              self.MinBuild, self.MaxBuild)
        header += struct.pack('<HHHHHH', len(self.Strings), len(self.Dirs), 
                              len(self.Files), len(self.RegHives), 
                              len(self.RegKeys), len(self.Links))
        header += struct.pack('<IIIIII', strings_offset, directories_offset, 
                              files_offset, reghives_offset, regkeys_offset, links_offset)
        header += struct.pack('<HHHHHHHH', application_offset, len(self.AppName), 
                              provider_offset, len(self.Provider), 
                              unsupported_offset, len(self.Unsupported), 0, 0)
        
        return (header + application + provider + unsupported + 
                strings + directories + files + reghives + regkeys + links)
        
    def write(self, path, dir = ''):
        cab_files = []
        
        if dir != '' and not dir.endswith('/'):
            dir += '/'
        
        manifest = 'manifest.000';
        with open(dir + manifest, "wb") as m:
            m.write(self.__get_manifest())
        
        lcab_args = ['lcab', '-n']
        lcab_args.append(dir + manifest)
        lcab_args.extend(cab_files)
        if self.SetupFile != "": lcab_args.append(self.SetupFile)
        lcab_args.append(path)
        subprocess.call(lcab_args)
        
        return True
