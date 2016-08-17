'''
Not actually code - I'm just calling it a .py script so that github   colours the text
Some common commands!
'''
# Check if input is passed as argument
if len(sys.argv) < 2:
    print '\nUSAGE: PYTHON REVTMD.PY FILENAME\n'
    print 'Requires EASYGUI\n'    
    sys.exit()
    
# Store the current time in ISO8601 format.
time_date = time.strftime("%Y-%m-%dT%H:%M:%S")
date = time.strftime("%Y-%m-%d")
    
    
    # Check if input is a file.
    # AFAIK, os.path.isfile only works if full path isn't present.
    if os.path.isfile(file_without_path):      
        print os.path.isfile(file_without_path)
        print "single file found"
        video_files = []                       # Create empty list 
        video_files.append(file_without_path)  # Add filename to list
        print video_files
    # Check if input is a directory. 
    elif os.path.isdir(file_without_path):  
        os.chdir(file_without_path)
        video_files =  glob('*.mov') + glob('*.mp4') + glob('*.mxf') + glob('*.mkv')
filename              = sys.argv[1]
filename_without_path = os.path.basename(filename)
filenoext = os.path.splitext(filename)[0]
Find desktop path              = os.path.expanduser("~/Desktop/%s.csv") % filename_without_path
wd = os.path.dirname(filename)
os.chdir(wd)
video_files =  glob('*.mxf')
xml_files   = glob('*.xml')
mxfhashes   = {}
mxfhashes[key][1] # access 2nd item in a list within a dictionary
revtmd_xmlfile = sys.argv[1] + 'revtmd.xml'

        # This removes the new line character from the framemrate.
        fixed_framerate = get_framerate.rstrip()
        
            # Generate new directory names in AIP
    metadata_dir   = wd + "/%s/metadata" % os.path.splitext(filename)[0]
    data_dir   = wd + "/%s/data" % os.path.splitext(filename)[0]
    provenance_dir   = wd + "/%s/provenance" % os.path.splitext(filename)[0]
'''
Create CSV - 
'''
f = open(csvfile, 'wt')
try:
    writer = csv.writer(f)
    writer.writerow( ('MXF HASH', 'STORED HASH', 'FILENAME', 'JUDGEMENT') )
   
finally:
    f.close()
# coding    
video_files =  glob('*.mxf')
xml_files   = glob('*.xml')
mxfhashes   = {}

# get Operating system and do something:
if _platform == "darwin":
      print "OS X"
      font_path= "fontfile=/Library/Fonts/AppleGothic.ttf"
elif _platform == "linux2":
      print "linux"
      font_path= "fontfile=/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
elif _platform == "win32":
      font_path = "'fontfile=C\:\\\Windows\\\Fonts\\\\'arial.ttf'"
