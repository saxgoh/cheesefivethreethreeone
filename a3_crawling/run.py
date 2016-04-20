import json
from subprocess import call
import sys
# Initialization
depth = 5

# Initialization
if len(sys.argv) <> 2:
    exit("Usage: " + sys.argv[0] + " <input_urls_json_file>")
else:
    inFile = sys.argv[1]
try:
    print "Input File is "+inFile
    with open(inFile,"r") as dataFile:
        data = json.load(dataFile)
except:
        sys.exit('Cannot open input.json, exiting...')

# Method definition
def exec_scrapy(path, allowed_domains, username=None, password=None):
    cmd = "scrapy crawl regular -a base_url=" + path + " -a depth=" + `depth` + " -a allowed_domains=" + allowed_domains
    if username and password:
        cmd += " -a username=" + username + " -a password=" + password
        cmd += " -a login=true"
    try:
        call( [cmd] , shell=True )
    except:
        sys.exit('Cannot exec Scrapy, exiting...')

# Iteration of input file
for path, details in data.iteritems():
    login_params = None
    if 'loginParam' in details:
        login_params = details['loginParam']
    # Assumption for now: Only 1 allowed_domain
    allowed_domains = details['allowed_domains'][0]
    if login_params:
        for param in login_params:
            exec_scrapy(path + param['path'], allowed_domains, param['username'], param['password'])
    exec_scrapy(path, allowed_domains)

