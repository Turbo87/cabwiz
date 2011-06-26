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
            value = value.split(',')[-1].replace('\\', '/').replace('"', '').strip()
            if not value.endswith('/'): value += '/'
            names[id] = value
            
        return names
    
    def __parse_disk_files(self, cab, names):
        files = {}
        for file, id in self.__inf['SourceDisksFiles'].iteritems():
            id = int(id)
            if id in names:
                files[file.replace('"', '').strip()] = names[id]
            
        return files
    
    def __parse_destinations(self, cab):
        destinations = {}
        for name, value in self.__inf['DestinationDirs'].iteritems():
            value = value.split(',')[-1].replace('\\', '/').replace('"', '').strip()
            destinations[name.strip()] = value
            
        return destinations
    
    def __parse_copy_files(self, cab, files, destinations):
        if 'CopyFiles' not in self.__inf['DefaultInstall']: return {}
        
        copy_files = []
        for section in self.__inf['DefaultInstall']['CopyFiles'].split(','):
            section = section.strip()
            if (section not in self.__inf or 
                section not in destinations): 
                continue
            
            for line in self.__inf[section]:
                line = line.split(',')
                if len(line) < 1: continue
                
                filename = line[0].strip()
                file = [filename]
                if filename not in files: continue
                file.append(files[filename])
                
                file.append(line[1].strip() if len(line) > 1 else filename)
                file.append(destinations[section])
                 
                file.append(int(line[3].strip(), 16) if len(line) > 3 else 0)
                
                copy_files.append(file)
            
        return copy_files
    
    def __get_string_id(self, cab, string):
        for i in range(len(cab.Strings)):
            if cab.Strings[i] == string: return i + 1
        
        cab.Strings.append(string)
        return len(cab.Strings)
    
    def __get_dir_id(self, cab, dir):
        for i in range(len(cab.Dirs)):
            if cab.Dirs[i][0] == dir: return i + 1
        
        parts = dir.split('/')
        strings = []
        for part in parts:
            strings.append(self.__get_string_id(cab, part.strip()))

        cab.Dirs.append([dir, strings])
        return len(cab.Dirs)
    
    def __convert_copy_files(self, cab, copy_files):
        for i in range(len(copy_files)):
            file = copy_files[i]
            
            out = CabWriter.munge_filename(file[0], i + 1)
            shutil.copy(file[1] + file[0], self.__dest + out)
            
            dir = self.__get_dir_id(cab, file[3])
            cab.Files.append([out, self.__dest, file[2], file[3], file[4], dir, file[0]])
            
        return True
    
    def __parse_setup_dll(self, cab, files):
        if ('CESetupDLL' not in self.__inf['DefaultInstall']):
            return False
        
        dll_in = self.__inf['DefaultInstall']['CESetupDLL']
        if dll_in not in files: return False
        
        dll_out = self.__dest + CabWriter.munge_filename(dll_in, 999)
        shutil.copy(files[dll_in] + dll_in, dll_out)
        
        cab.SetupFile = dll_out
            
        return True
    
    def __get_reghive_id(self, cab, root, path):
        for i in range(len(cab.RegHives)):
            if cab.RegHives[i][0] == str(root) + '/' + path: return i + 1
        
        parts = path.split('/')
        strings = []
        for part in parts:
            strings.append(self.__get_string_id(cab, part.strip()))

        cab.RegHives.append([str(root) + '/' + path, root, strings])
        return len(cab.RegHives)
    
    def __unreplace_install_dir(self, str):
        install_dir = self.__inf['CEStrings']['InstallDir'].replace('"', '')
        return str.replace(install_dir, '%InstallDir%')
    
    def __parse_registry(self, cab):
        if 'AddReg' not in self.__inf['DefaultInstall']: return {}
        
        reg = []
        for section in self.__inf['DefaultInstall']['AddReg'].split(','):
            section = section.strip()
            if (section not in self.__inf): 
                continue
            
            for line in self.__inf[section]:
                line = line.split(',')
                if len(line) < 5: continue
                
                reg.append([line[0], line[1].replace('\\', '/').replace('"', '').strip(),
                            line[2].replace('"', '').strip(), int(line[3], 16), line[4:]])
            
        return reg
    
    def __convert_registry(self, cab, reg):
        for item in reg:

            if item[0] == 'HKCR': root = 1
            elif item[0] == 'HKCU': root = 2
            elif item[0] == 'HKLM': root = 3
            elif item[0] == 'HKU': root = 4
            else: continue
            
            hive = self.__get_reghive_id(cab, root, item[1].strip('/'))
            
            key = item[2]
            
            type = (item[3] & 0x00010001)
            if type == 0x00010001: type = 1
            elif type == 0x00000000: type = 2
            elif type == 0x00010000: type = 3
            elif type == 0x00000001: type = 4
            else: continue
            
            if type == 1: value = int(item[4][0])
            elif type == 2: value = self.__unreplace_install_dir(item[4][0].replace('"', '').strip())
            elif type == 4: value = item[4][0]
            elif type == 3: 
                value = []
                for v in item[4]:
                    value.append(self.__unreplace_install_dir(v.replace('"', '').strip()))
            else: continue
            
            cab.RegKeys.append([hive, key, type, item[3], value])
    
    def __parse_links(self, cab, destinations):
        if 'CEShortcuts' not in self.__inf['DefaultInstall']: return {}
        
        links = []
        for section in self.__inf['DefaultInstall']['CEShortcuts'].split(','):
            section = section.strip()
            if (section not in self.__inf): 
                continue
            
            section_dest = destinations[section] if section in destinations else '' 
            
            for line in self.__inf[section]:
                line = line.split(',')
                if len(line) < 3: continue
                
                link = [line[0].replace('"', '').strip() + '.lnk']
                link.append(line[2].replace('"', '').strip())
                link.append(int(line[1]) != 0)
                
                dir = section_dest
                if len(line) > 3:
                    dir = line[3].replace('\\', '/').replace('"', '').strip()
                
                if dir == '': continue
                
                link.append(dir.rstrip('/') + '/')
                links.append(link)
            
        return links
    
    def __convert_links(self, cab, links):
        for link in links:
            parts = (link[3] + link[0]).split('/')

            strings = []
            base_dir = ''
            for part in parts:
                if base_dir == '': base_dir = part
                else: strings.append(self.__get_string_id(cab, part.strip()))
            
            if base_dir.startswith('%CE') and base_dir.endswith('%'):
                base_dir = int(base_dir.strip('%')[2:])
            else:
                base_dir = 0
            
            type = 0 if link[2] else 1
            if type == 0:
                destination = self.__get_dir_id(cab, link[1])
            else:
                for i in range(len(cab.Files)):
                    if cab.Files[i][6] == link[1]:
                        destination = i + 1
                        break
                
            cab.Links.append([link[0], base_dir, destination, type, strings])
    
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
        files = self.__parse_disk_files(cab, names)
        destinations = self.__parse_destinations(cab)
        copy_files = self.__parse_copy_files(cab, files, destinations)
        self.__convert_copy_files(cab, copy_files)
        self.__parse_setup_dll(cab, files)
        reg = self.__parse_registry(cab)
        self.__convert_registry(cab, reg)
        links = self.__parse_links(cab, destinations)
        self.__convert_links(cab, links)

        cab_file = self.__create_output_filename()
        if cab_file == "":
            return False
        
        print 'Writing CAB file to "' + self.__dest + cab_file + '" ...'
        if not cab.write(cab_file, self.__dest):
            return False
        
        return True
