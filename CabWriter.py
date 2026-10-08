import subprocess
import struct
import binascii

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
        application = self.AppName.encode("utf-8") + b"\0"
        offset += len(application)
    
        # Provider.
        provider_offset = offset
        provider = self.Provider.encode("utf-8") + b"\0"
        offset += len(provider)
    
        # Unsupported platforms.
        unsupported_offset = offset
        unsupported = self.Unsupported.encode("utf-8") + b'\0' if self.Unsupported != "" else b""
        offset += len(unsupported)
    
        # Strings.
        strings_offset = offset
        strings = b''
        for i in range(len(self.Strings)):
            string = self.Strings[i].encode("utf-8")
            strings += struct.pack('<HH', i + 1, len(string) + 1)
            strings += string + b'\0'
        
        offset += len(strings)
    
        # Directories.
        directories_offset = offset;
        directories = b''
        for i in range(len(self.Dirs)):
            dir = self.Dirs[i]
            directories += struct.pack('<HH', i + 1, (len(dir[1]) * 2) + 2)
            for id in dir[1]:
                directories += struct.pack('<H', id)

            directories += struct.pack('<H', 0)

        offset += len(directories)
    
        # Files.
        files_offset = offset;
        files = b'';
        for i in range(len(self.Files)):
            file = self.Files[i]
            files += struct.pack('<HHHIH', i + 1, file[5], i + 1, file[4], len(file[2]) + 1)
            files += file[2].encode("utf-8") + b'\0'

        offset += len(files)
    
        # RegHives.
        reghives_offset = offset
        reghives = b''
        for i in range(len(self.RegHives)):
            hive = self.RegHives[i]
            reghives += struct.pack('<HHHH', i + 1, hive[1], 0, (len(hive[2]) * 2) + 2)
            for id in hive[2]:
                reghives += struct.pack('<H', id)

            reghives += struct.pack('<H', 0)

        offset += len(reghives)
    
        # RegKeys.
        regkeys_offset = offset
        regkeys = b''
        for i in range(len(self.RegKeys)):
            key = self.RegKeys[i]

            content = key[1] + '\0'
            if key[2] == 1: content += struct.pack('<I', key[4])
            elif key[2] == 2: content += key[4] + '\0'
            elif key[2] == 4: content += key[4]
            elif key[2] == 3:
                for item in key[4]: 
                    content += item + '\0'
                content += '\0'
            else: continue

            regkeys += struct.pack('<HHHIH', i + 1, key[0], 1, key[3], len(content))
            regkeys += content

        offset += len(regkeys)
    
        # Links.
        links_offset = offset
        links = b''
        for i in range(len(self.Links)):
            link = self.Links[i]
            links += struct.pack('<HHHHHH', i + 1, 0, link[1], link[2], link[3], (len(link[4]) * 2) + 2)
            for id in link[4]:
                links += struct.pack('<H', id)

            links += struct.pack('<H', 0)
        
        offset += len(links)
    
        # Header.
        length = offset;
    
        header = b'MSCE'
        header += struct.pack('<IIIIIIIIIII', 0, length, 0, 1, self.Architecture, 
                              self.MinVersion[0], self.MinVersion[1], 
                              self.MaxVersion[0], self.MaxVersion[1], 
                              self.MinBuild, self.MaxBuild)
        header += struct.pack('<HHHHHH', len(self.Strings), len(self.Dirs), 
                              len(self.Files), len(self.RegHives), 
                              len(self.RegKeys), len(self.Links))
        header += struct.pack('<IIIIII', strings_offset, directories_offset, 
                              files_offset, reghives_offset, regkeys_offset, links_offset)
        header += struct.pack('<HHHHHHHH', application_offset, len(self.AppName) + 1, 
                              provider_offset, len(self.Provider) + 1, 
                              unsupported_offset, len(self.Unsupported), 0, 0)
        
        return (header + application + provider + unsupported + 
                strings + directories + files + reghives + regkeys + links)
        
    def write(self, path, dir = '', verbose = False):
        if dir != '' and not dir.endswith('/'):
            dir += '/'
        
        if verbose: print("Creating manifest ...")
        manifest = 'manifest.000';
        with open(dir + manifest, "wb") as m:
            m.write(self.__get_manifest())
        
        lcab_args = ['lcab', '-n']
        lcab_args.append(dir + manifest)
        
        for file in reversed(self.Files):
            lcab_args.append(file[1] + file[0])
            
        if self.SetupFile != "": lcab_args.append(self.SetupFile)
        lcab_args.append(dir + path)
        
        if verbose: print("Starting lcab ...")
        with open("/dev/null", "w") as null:
            p = subprocess.Popen(lcab_args, stdout = None if verbose else null)
            p.wait()
        
        return True
