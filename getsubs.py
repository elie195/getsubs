"""
*******************
Python script that expects a single command-line argument which is the full path to a video file. If a folder is passed, the script will process all MKV files in that folder.
The script will search opensubtitles.org (using hash and size of video file) and download the matching .srt file.
The matching .srt file will be placed in the same directory as the video file and will have the same filename as well (except for the file extension of course).

Arguments: [File|Folder] [Username] [Password]
*******************
"""

#TODO: Implement error checking
#TODO: Implement settings/config file
#TODO: Allow relative path/specify output path


import os, sys, glob
from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File
import base64, gzip



#Main function
def downloadSubs(Parameters):

    #Assign/allocate object and get token after logging in with credentials from the Parameters object

    opensubs = OpenSubtitles()
    token = opensubs.login(Parameters.username, Parameters.password)
    if token is None:
        print ('\n*** Login failed! ***\n')
        sys.exit()
    #Get hash and size of file from Parameters object
    f = File(os.path.join(Parameters.path, Parameters.video))
    print ('\tPath: %s' % Parameters.path)
    print ('\tFile: %s' % Parameters.video)
    hash = f.get_hash()
    size = f.get_size()

    #Search subtitles DB using file hash and size. Looks like the first result is the best matching result
    data = opensubs.search_subtitles([{'sublanguageid': 'eng', 'moviehash': hash, 'moviebytesize': size}])

    #Sort data by "Subtitle Downloads Count" - Descending. This should download the best result
    data.sort(key=lambda e:int(e['SubDownloadsCnt']), reverse=True)

    if data:
        #Download first result, decode it from BASE64, add gz extension, save file
        download = opensubs.download_subtitles([data[0]['IDSubtitleFile']])
        print ('\nDownloading: %s' % data[0]['SubFileName'])
        data_decoded = base64.b64decode(unicode(download[0]['data']))
        gz_file = os.path.join(Parameters.path, Parameters.subtitle) + '.gz'
        print ('\nCreating gz file: %s' % gz_file)
        download_file = open(gz_file,'w')
        download_file.write(data_decoded)
        download_file.close()
        print ('Created gz file: %s' % gz_file)

        #Extract SRT file from gz file and place it in the same folder
        print ('Opening gz file: %s' % gz_file)
        srt_file_buffer = gzip.open(gz_file, 'r')
        srt_file_name = os.path.join(Parameters.path, Parameters.subtitle)
        print ('Creating SRT file: %s' % srt_file_name)
        srt_file = open(srt_file_name,'w')
        srt_file.write(srt_file_buffer.read())
        srt_file.close()
        print ('Created SRT file: %s' % srt_file_name)

        #Delete .gz file
        print ('Deleting %s' % gz_file)
        os.remove(gz_file)

    else:
        print ('*** No match found for file! ***')


#Cookie-cutter yes/no prompt function
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
        
        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).
        
        The "answer" return value is one of "yes" or "no".
        """
    valid = {"yes":True,   "y":True,  "ye":True,
        "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    
    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


#Set Parameters object for login info and movie details
class Parameters(object):
    username = sys.argv[2]
    password = sys.argv[3]
    path = 'changeme'     #Path to file without filename (e.g. /Users/eblech/Movies)
    video = 'changeme'    #Filename only with extension (e.g. Game.of.Thrones.S01E01.mkv)
    subtitle = 'changeme'

#Execute function with Parameters class as parameters
#Check if path given by argument exists
fn = sys.argv[1]
if os.path.exists(fn):
    
    
    #If entire folder is passed
    if os.path.isdir(fn):
        Parameters.path = fn
        os.chdir(fn)

        types = ('*.mkv', '*.avi', '*.m4v', '*.mp4')
        files_grabbed = []
        current_status = 0
        for stuff in types:
            files_grabbed.extend(glob.glob(stuff))
            if files_grabbed == []:
                print ('*** No matching files found in folder! Supported formats are: %s ***' % (types,))
                sys.exit()              #Exit if no matching files are found
    
        for files in files_grabbed:
            print (files)
        if query_yes_no('\n\nProcess these files?'):
            for files in files_grabbed:
                print ('Processing file: %s' % files)
                Parameters.video = files        #Sets fn_tail (filename only)
                Parameters.subtitle = os.path.splitext(Parameters.video)[0] + '.srt'
                downloadSubs(Parameters)
                current_status += 1
                percent_done = (float(current_status)/len(files_grabbed))*100
                print ('\nDone - %0.02f%% complete\n\n\n' % percent_done)
        else:
            sys.exit()
    
    #If specific file is passed
    if os.path.isfile(fn):
        print ('Processing file: %s' % os.path.basename(fn))
        fn_split = os.path.split(fn)
        Parameters.path = fn_split[0]       #Sets fn_head (path only)
        Parameters.video = fn_split[1]      #Sets fn_tail (filename only)
        Parameters.subtitle = os.path.splitext(Parameters.video)[0] + '.srt'
        downloadSubs(Parameters)


#If path doesn't exist (maybe also doesn't have permission, need to check)
else:
    print ('*** Invalid path/permissions failure. Please enter the full path to the video file ***')








