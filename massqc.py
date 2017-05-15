import sys
import subprocess
import os


def main():    
    for root, dirnames, filenames in os.walk(sys.argv[1]):
        for filename in filenames:
            if filename.endswith(('.mov', '.mkv')):
                if filename[0] != '.':
                    cmd = ['qcli', '-i', os.path.join(root,filename)]
                    subprocess.call(cmd)


if __name__ == '__main__':
    main()