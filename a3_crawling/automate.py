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
#loop through outputfolder
dirPath='../a3_exploit/output'
if not os.path.exists(dirPath):
    print dirPath
    print "output does not exist"
else:
    for root, dirs, filenames in os.walk(dirPath):
        for f in filenames:
          print(f)  
          injectionFilename="../a3_exploit/output"+f
          payloadpath="../a3_exploit/"+payloadFilename
          callexploit='python ../a3_exploit/run.py '+injectionFilename+" "+payloadpath
          print injectionFilename
          call([callexploit], shell = True)
            
