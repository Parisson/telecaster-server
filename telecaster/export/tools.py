
# External functions

def get_type(value):
    """ Return a String with the type of value """
    types = {bool : 'bool', int : 'int', str : 'str'}
    # 'bool' type must be placed *before* 'int' type, otherwise booleans are
    # detected as integers
    for type in types.keys():
        if isinstance(value, type) :
            return types[type]
    raise TypeError, str(value) + ' has an unsupported type'

def get_cast(value, type) :
    """ Return value, casted into type """
    if type == 'bool' :
        if value == 'True' :
            return True
        return False
    elif type == 'int' :
        return int(value)
    elif type == 'str' :
        return str(value)
    raise TypeError, type + ' is an unsupported type'

def get_file_mime_type(path):
    """ Return the mime type of a file """
    try:
        file_out1, file_out2 = os.popen4('file -i "'+path+'"')
        for line in file_out2.readlines():
            line_split = line.split(': ')
            mime = line_split[len(line_split)-1]
            return mime[:len(mime)-1]
    except IOError:
        return 'Exporter error [1]: path does not exist.'

def get_file_type_desc(path):
    """ Return the type of a file given by the 'file' command """
    try:
        file_out1, file_out2 = os.popen4('file "'+path+'"')
        for line in file_out2.readlines():
            description = line.split(': ')
            description = description[1].split(', ')
            return description
    except IOError:
        return 'Exporter error [1]: path does not exist.'

def iswav(path):
    """ Tell if path is a WAV """
    try:
        mime = get_file_mime_type(path)
        return mime == 'audio/x-wav'
    except IOError:
        return 'Exporter error [1]: path does not exist.'

def iswav16(path):
    """ Tell if path is a 16 bit WAV """
    try:
        file_type_desc = get_file_type_desc(path)
        return iswav(path) and '16 bit' in file_type_desc
    except IOError:
        return 'Exporter error [1]: path does not exist.'

def get_file_name(path):
    """ Return the file name targeted in the path """
    return os.path.split(path)[1]

def split_file_name(file):
    """ Return main file name and its extension """
    try:
        return os.path.splitext(file)
    except IOError:
        return 'Exporter error [1]: path does not exist.'

def clean_word(word) :
    """ Return the word without excessive blank spaces, underscores and
    characters causing problem to exporters"""
    word = re.sub("^[^\w]+","",word)    #trim the beginning
    word = re.sub("[^\w]+$","",word)    #trim the end
    word = re.sub("_+","_",word)        #squeeze continuous _ to one _
    word = re.sub("^[^\w]+","",word)    #trim the beginning _
    #word = string.replace(word,' ','_')
    #word = string.capitalize(word)
    dict = '&[];"*:,'
    for letter in dict:
        word = string.replace(word,letter,'_')
    return word

def recover_par_key(path):
    """ Recover a file with par2 key """
    os.system('par2 r "'+path+'"')

def verify_par_key(path):
    """ Verify a par2 key """
    os.system('par2 v "'+path+'.par2"')

