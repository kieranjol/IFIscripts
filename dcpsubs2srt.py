import sys
from lxml import etree

filename = sys.argv[1]
srt_file = filename +'.srt'

xmlo = etree.parse(filename)
count = int(xmlo.xpath('count(//Subtitle)'))
counter = 0

with open(srt_file, "w") as myfile:
       print 'Transforming ', count, 'subtitles'

while counter < count:
    counter2 = counter +1
    in_point = xmlo.xpath('//Subtitle')[counter].attrib['TimeIn']
    out = xmlo.xpath('//Subtitle')[counter].attrib['TimeOut']
    in_point = in_point[:8] + '.' + in_point[9:]
    out = out[:8] + '.' + out[9:]

    with open(srt_file, "a") as myfile:
        myfile.write(str(counter + 1) + '\n')
        myfile.write(in_point + ' --> ' + out + '\n')
        bla =  [bla.text for bla in xmlo.iterfind('.//Subtitle[%s]/Text' % int(counter2) ) ]
        for i in bla:
                myfile.write(i + '\n')
        myfile.write('\n')

        print 'Transforming ' + str(counter) + ' of' + str(count) + ' subtitles\r' ,
          
    counter +=1 
