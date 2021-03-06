from subprocess import call
import json
import sys
import os

if len(sys.argv) != 3:
    print "#####"
    print "Usage: python automate.py [input.json] [payloads.json]"
    print "#####"
    sys.exit(0)

print sys.argv
inputFilename = sys.argv[1]
payloadFilename = sys.argv[2]

if not os.path.isfile(inputFilename):
    print "Input URL File does not exist: "+inputFilename
    sys.exit(0)

if not os.path.isfile(payloadFilename):
    print "Payload File does not exist: "+payloadFilename
    sys.exit(0)

# get json objects of urls
with open(inputFilename, 'r') as f:
    inputJson = json.load(f)

#Run A3_Crawling
print "Running a3_crawling"
callcmd='python run.py ' +inputFilename
call([callcmd], shell=True)

#Run A3_exploit
#loop through outputfolder in a3_crawling
dirPath='output'
if not os.path.exists(dirPath):
    print "Output does not exist"
else:
    for filename in os.listdir(dirPath):
        if len(filename)>0:
          callexploit='python ../a3_exploit/run.py '+str("output/"+filename)+" "+payloadFilename
          print "==============calling exploit========="
          print callexploit
          print "==============calling exploit========="
          call([callexploit], shell = True)
            
