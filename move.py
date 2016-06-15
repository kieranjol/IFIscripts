import sys
import subprocess
import os
import pdb
import shutil
import filecmp

source               = sys.argv[1]
parent_dir           = os.path.dirname(source)
normpath             = os.path.normpath(source) 
dirname              = os.path.splitext(os.path.basename(source))[0]
relative_path        = normpath.split(os.sep)[-1]

destination          = sys.argv[2] # or hardcode
manifest_destination = destination + '/%s_manifest.md5' % dirname
destination         += '/%s' % dirname
manifest             = parent_dir + '/%s_manifest.md5' % relative_path

def make_manifest(manifest_dir, relative_manifest_path, manifest_textfile):
    os.chdir(manifest_dir)
    
    #pdb.set_trace()
    manifest_generator = subprocess.check_output(['md5deep', '-ler', relative_manifest_path])
    bla = manifest_generator.splitlines()
    bla.sort()

    with open(manifest_textfile,"wb") as fo:
        for i in bla:
            fo.write(i + '\n')
                       
make_manifest(parent_dir, relative_path,manifest)    
subprocess.call(['robocopy',sys.argv[1], destination, '/E'])
make_manifest(sys.argv[2],dirname, manifest_destination) 

if filecmp.cmp(manifest, manifest_destination, shallow=False): 
        	print "Your files have reached their destination and the checksums match"
else:
        	print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"
        	sys.exit()                 
