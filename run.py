import json
from subprocess import call

# Initialization
depth = 5

with open("input.json","r") as dataFile:
    data = json.load(dataFile)

# Method definition
def exec_scrapy(path, allowed_domains, username=None, password=None):
    cmd = "scrapy crawl regular -a base_url=" + path + " -a depth=" + `depth` + " -a allowed_domains=" + allowed_domains
    if username and password:
        cmd += " -a username=" + username + " -a password=" + password
        cmd += " -a login=true"
    call( [cmd] , shell=True )

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
