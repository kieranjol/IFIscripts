import sys
import os

def main():
    
    input = sys.argv[1]
    print('Label Frontend,Label Backend,Definition,Format of content,Obligation,Repeatability')
    with open(input, 'r') as source:
        raw_dump = source.read()
        raw_dump = raw_dump.replace('\r', '\n')
        raw_info =  raw_dump.split('\n')
    #print raw_info
    for line in raw_info:
        if line != '':
            mandatory = 'optional'
            repeatability = 'repeatable'
            format_of_content = line.split(':')[1].split(',')[0][1:]
            if 'Text(subst-list)' in line:
                format_of_content = 'Text(subst-list)' 
            backend_name = line.split(':')[0].replace(':', '').split('.')[1][1:]
            if 'required' in line:
                mandatory = 'required'
            if ', Term & Word,' in line:
                indexing = 'Term & Word Indexing'
            elif ', Word' in line:
                indexing = 'Word Indexing'
            elif ', Term' in line:
                indexing = 'Term Indexing'
            if 'single-only' in line:
                repeatability = 'not-repeatable'
            if 'valid-list' in line:
                format_of_content += ':Validation list'
            if 'override' in line:
                format_of_content += ':override'
            if 'update-valid-list' in line:
                format_of_content += ':update-valid-list'
            a =  "'','%s','', '%s:%s','%s','%s'"  % (backend_name, format_of_content, indexing,  mandatory, repeatability)
            print(a.replace('\'', ''))
if __name__ == '__main__':
    main()
