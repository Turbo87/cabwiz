# http://msdn.microsoft.com/en-us/library/aa924359.aspx
# http://msdn.microsoft.com/en-us/library/bb964579.aspx

import sys
import InfReader

def read_replacements_section(inf, section):
    replacements = []
    for line in inf.get_section(section):
        line = line.split('=')
        if len(line) < 2:
            continue
        
        key = line[0].strip()
        value = line[1].strip()
        replacements.append([key, value])

    return replacements        

def read_replacements(inf):
    # Read replacements from CEStrings section
    replacements = read_replacements_section(inf, 'CEStrings')
    
    # Read replacements from Strings section if it exists
    if inf.has_section('Strings'):
        replacements.extend(read_replacements_section(inf, 'Strings'))
        
    # Return replacements array
    return replacements        

def apply_replacements(inf):
    # Read replacement sections from INF file
    replacements = read_replacements(inf)
    
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
    inf.apply_replacements(replacements)

def process_parameters(parameters):
    print 'Reading INF file "' + parameters['inf-file'] + '" ...'
    inf = InfReader.InfReader()
    
    if not inf.read(parameters['inf-file']):
        return
    
    apply_replacements(inf)
    
    print inf.raw()

def read_parameters(argv):    
    if len(argv) < 2:
        return {}

    if '/help' in argv or '-help' in argv or '--help' in argv:
        return {'help': True}
        
    parameters = {'inf-file': argv[1]}
    
    for i in range(len(argv)):
        if i < 2:
            continue
        
        if (argv[i] == '/dest' or argv[i] == '-dest') and i + 1 < len(argv):
            parameters['dest-dir'] =  argv[i + 1]
            continue
        
        if (argv[i] == '/err' or argv[i] == '-err') and i + 1 < len(argv):
            parameters['err-file'] =  argv[i + 1]
            continue
        
        if (argv[i] == '/cpu' or argv[i] == '-cpu') and i + 1 < len(argv):
            j = i + 1
            parameters['cpu-type'] = []
            while j < len(argv) and not (argv[j].startswith('/') or argv[j].startswith('-')):
                parameters['cpu-type'].append(argv[j])
                j += 1
            continue
        
        if (argv[i] == '/platform' or argv[i] == '-platform') and i + 1 < len(argv):
            parameters['platform-name'] =  argv[i + 1]
            continue
        
    return parameters

def print_help():
    print '''Usage:    python cabwiz.py <inf-file> [/dest <dest-dir>] [/err <err-file>] [/cpu <cpu-type> [<cpu-type]] [/platform <platform-name]
    
         inf-file       INF source file to use
         dest-dir       absolute dest dir for CAB files
         err-file       error file
         cpu-type       cpu types to support in the INF file
         platform-name  the name of the platform to support in the INF file'''

def main():
    parameters = read_parameters(sys.argv)
    
    if 'help' in parameters:
        print_help()
        return
    
    if 'inf-file' not in parameters:
        print_help()
        print
        print 'Error: invalid command line parameters'
        return
    
    process_parameters(parameters)
    
if __name__ == '__main__':
    main()
