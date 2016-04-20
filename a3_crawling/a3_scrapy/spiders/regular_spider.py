import scrapy
from selenium import webdriver
from scrapy.conf import settings
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from a3_scrapy.items import Form, Input
from a3_scrapy.output_struct import OutputStruct, Item
import re
from subprocess import check_output
import urlparse

class RegularSpider(CrawlSpider):
  name = "regular"
  handle_httpstatus_list = [500]
  allowed_domains = ""
  start_urls = []
  username = ""
  password = ""
  username_identifier = ""
  password_identifier = ""
  login = False
  ops = None
  collated_urls = {}
  visit_js = []
  traversed_urls = set()

  # Rules for CrawlSpider
  rules = [Rule(LinkExtractor(allow=(),deny=("logout", "Logout", "Log Out", "Log out", "Sign out")), callback="parse_item", follow= True,)]

  def __init__(self, *args, **kwargs):
    super(RegularSpider, self).__init__(*args, **kwargs)
    self.start_urls.append(kwargs["base_url"])
    # self.allowed_domains = kwargs["allowed_domains"]
    self.allowed_domains = [kwargs["allowed_domains"]]
    # if 'depth' in kwargs:
    settings.overrides['DEPTH_LIMIT'] = int(kwargs["depth"])
    if 'username' in kwargs:
        self.username = kwargs['username']
    if 'password' in kwargs:
        self.password = kwargs['password']
    if 'login' in kwargs:
        self.login = True
    print "THIS IS INIT"
    print self.start_urls
    print self.login

  # For JS customization
  # def process_value(value):
  #     return

  def parse_start_url(self, response):
      print "I WAS HERE"
      if self.login:
          print "Login"
          this_is_my_form = None
          for f in response.xpath("//form"):
              if re.search("login", f.extract(), re.IGNORECASE):
                  this_is_my_form = f
          this_is_my_form_url = this_is_my_form.xpath("@action").extract()
          if len(this_is_my_form_url) > 0:
              this_is_my_form_url = urlparse.urljoin(response.url, this_is_my_form_url[0])
          else:
              this_is_my_form_url = self.start_urls[0]
          print this_is_my_form_url
          print "=============================================="
          print "****"
          print "=============================================="
          print this_is_my_form.extract()
          print "=============================================="
          print "****"
          print "=============================================="

          # ASSUMPTION: most login forms put username above password
          #             therefore, for our login form, we will use
          #             the first match as username and second match as password
          username_field = this_is_my_form.xpath(".//input[@type='text']/@name").extract()
          password_field = this_is_my_form.xpath(".//input[@type='password']/@name").extract()
          other_fields = this_is_my_form.xpath(".//input[@value!='']")
          if len(username_field) > 0 and len(password_field) > 0:
              self.username_identifier = str(username_field[0])
              self.password_identifier = str(password_field[0])
              submit_data = {str(username_field[0]): self.username, str(password_field[0]): self.password}

              if len(other_fields) > 0:
                  for of in other_fields:
                      if len(of.xpath("@name")) > 0:
                          submit_data[str(of.xpath("@name").extract()[0])] = str(of.xpath("@value").extract()[0])
              print submit_data
              try:
                  return [scrapy.FormRequest(
                          url=this_is_my_form_url,
                          formdata=submit_data,
                          callback=self.parse_item
                  )]
              except:
                  return None
          else:
              try:
                  return [scrapy.FormRequest(
                          url=this_is_my_form_url,
                          formdata={'username': self.username, 'password': self.password},
                          callback=self.parse_item
                  )]
              except:
                  return None
      else:
          self.parse_item(response)

  def parse_javascript(self,response,baseurl):
      # .open("POST", "main.php", true);
      # .open("POST", "windows/leakscan.php", true);
      # .open("POST", "main.php", true);
      # .open("GET", "windows/function.php?file="+file+"&start="+start+"&end="+end);
      # .open("GET", "windows/code.php?file="+file+"&lines="+lines);
      new_forms=[]
      all_opens = re.findall(".open\(.*\);", response)
      for o in all_opens:
          # print "o = "
          # print o
          new_form=Form()
          match = re.findall("[\/\w]*\.php\??[^\),]*", o)
          if len(match) != 0:
              print match
              print match
              # print "MATCH = "
              # print match
              # print "TYPE = "
              method = re.findall("(POST|GET)", o, re.IGNORECASE)
              # print method
              if len(method) == 1:
                  new_form['method'] = [str(method[0]).decode('UTF-8')]
              # print "ACTION = "
              action = re.findall("[\/\w]*\.php", match[0])
              # print action
              if len(action) == 1:
                  #make full url
                  fullurl=urlparse.urljoin(baseurl,str(action[0]).decode('UTF-8'))
                  new_form['action'] = [fullurl]
              # print "VAR 1 = "
              params = re.findall("[\?\&]{1}(\w*)=", match[0])
              # print params
              inputs = []
              for p in params:
                  i = Input()
                  i["inputName"] = [str(p).decode('UTF-8')]
                  inputs.append(i)
              new_form["fields"] = inputs
          # new_forms.append(new_form)
          if "action" in new_form and "method" in new_form:
              itemproc = self.crawler.engine.scraper.itemproc
              itemproc.process_item(new_form,self)
          else:
              print "NO ACTION / NO METHOD in JS form"
      return

  def request_javascript(self,url,baseurl):
      print "i am in request"
      if url in self.visit_js:
         print "Javascript visited"
         print url
      else:
         self.visit_js.append(url)
         print url
         try:
             out = check_output(["curl", "-k", "-sS", url])
             test = self.parse_javascript(out,baseurl)
         except:
             print "***** check_output failed in request_javascript in pipeline!!! *****"
             print "***** For URL:" + url + "*****"

         return


  def parse_item(self, response):
      # if response.status == 500:
      #     print "spotted meta"
      #     print response.meta
      #     LinkExtractor(allow=(),deny=("logout", "Logout", "Log Out", "Log out", "Sign out"))

      # if self.login:
      #     print response.body
      if "=appearance" in response.body:
        print "++++++++++++++++++++"
        print response.body
        print "++++++++++++++++++++"

      new_forms = []
      sel = Selector(response)
      form = sel.xpath('//form[@action and @method]')

      if response.url not in self.traversed_urls:
          new_forms = self.generic_extraction_of_forms_and_input(response.url, new_forms)
          self.traversed_urls.add(response.url)

      # This is to capture headers with...
      print "&&&&&& HEADERS HERE &&&&&&"
      print response.request.headers
      print "&&&&&& HEADERS HERE &&&&&&"
      if "Location" in response.request.headers:
           new_forms.append(self.parse_header_type("Location", response.request))
           print "Location"
           print response.request.headers['Location']
      # Can use same logic as cookie
      # Type is header, injection is location, value is url
      if "Cookie" in response.request.headers:
           print "Cookie"
           print response.request.url
           cookies=response.request.headers['Cookie']
           #example of cookie PHPSESSID=ks4dsu79gf7ve17uu3rfhmh581; display_all_courses=1;
           new_form = Form()
           new_form["method"] = ["Header"]
           new_form["action"] = [response.request.url]
           input_field = Input()
           cstring = "Cookie"
           cvalues = set()
           for paramvalue in re.split("; ",cookies):
              param=re.split("=",paramvalue)
              if (len(param)>0):
                 if len(param[0])>0:
                     cvalues.add(param[0])
           cstring += ":" + ",".join(list(cvalues))
           input_field["inputName"] = [cstring]
           new_form["fields"] = [input_field]
           new_forms.append(new_form)
                    #Type is header, Injection is COOKIE, and the param is in param[0]
                    #URL is response.request.url
                    #ADD THIS INTO OUTPUT
                    #ADD THIS INTO OUTPUT
                    #ADD THIS INTO OUTPUT
                    #ADD THIS INTO OUTPUT
      if "Referer" in response.request.headers:
           new_forms.append(self.parse_header_type("Referer", response.request))
           print "Referer"
           print response.request.headers['Referer']
                 #Just add it as injnection point type header, param is Language
      if "Language" in response.request.headers:
           new_forms.append(self.parse_header_type("Language", response.request))
           print "Language"
           print response.request.headers['Language']
                 #Just add it as injnection point type header, param is Language
      if "X-Requested-By" in response.request.headers:
           new_forms.append(self.parse_header_type("X-Requested-By", response.request))
           print "X-Requested-By"
           print response.request.headers['X-Requested-By']
                    #Add type is header param is X-Requested-By to output
                    #Add type is header param is X-Requested-By to output
                    #Add type is header param is X-Requested-By to output
      print "HEADERS END"

      # This is to check a hrefs
      a_links = {}
      for a_link in sel.xpath("//a[not(@href='')]"):
          new_form = Form()
          if len(a_link.xpath("@method")) > 0:
              new_form["method"] = a_link.xpath("@method").extract()
          else:
              new_form["method"] = ["GET".decode("utf-8")]
          url = a_link.xpath("@href").extract()[0]
          print url
          netloc = urlparse.urlparse(url).netloc
          if netloc == '' or netloc in self.allowed_domains:
              url = urlparse.urljoin(self.start_urls[0], url)
              new_forms = self.generic_extraction_of_forms_and_input(url, new_forms)

      # This is to check javascript
      print "Checking Javascript"
      javascript_links = {}
      for javascript_link in sel.xpath("//script/@src"):
         url = urlparse.urljoin(response.url,javascript_link.extract())
         self.request_javascript(url,response.url)
         # Extract Path in Javascript SRC
         # Does not fulfil requirements of keeping one GET param.
         new_forms = self.generic_extraction_of_forms_and_input(url, new_forms, True)
         #End Extract Path in Javascript SRC

      print "LONELY INPUTS HERE"
      lonely_inputs = {}
      for ip in sel.xpath("//input"):
        lonely_inputs[ip.extract()] = ip
        print ip.extract()

      #Extract both GET and POST from form
      for formItem in form:
          new_form = Form()
          # new_form['action'] = formItem.xpath('@action').extract()
          action_url=formItem.xpath('@action').extract()[0].decode('UTF-8')

          #concat to form full path
          action_url=urlparse.urljoin(response.url,action_url)
          new_form['action'] = [action_url]
          new_form['method'] = formItem.xpath('@method').extract()

          if len(formItem.xpath("input")) == 0:
              print "Weird form detected!"
              # This are forms with everything outside
              form_items = sel.xpath("//*[ancestor::form]/..//input")
              form_textareas = sel.xpath("//*[ancestor::form]/..//textarea")
          else:
              # This are the regular forms
              print "Regular form..."
              form_items = formItem.xpath(".//input")
              form_textareas = formItem.xpath(".//textarea")

          inputs = []
          # Need to expand this to include multiple input where input is not a direct form_items but still nested in form tag
          for each_input in form_items:
              print "XXXXXXXXXXXXXXXXXXXXX"
              print each_input
              print "XXXXXXXXXXXXXXXXXXXXX"
              new_input = Input()
              new_input["inputName"] = each_input.xpath("@name").extract()
              new_input["inputType"] = each_input.xpath("@type").extract()
              # new_form.add_form_input(new_input)
              inputs.append(new_input)
              lonely_inputs.pop(each_input.extract(), None)

          for each_textarea in form_textareas:
              new_input = Input()
              new_input["inputName"] = each_input.xpath("@name").extract()
              new_input["inputType"] = "textarea"
              inputs.append(new_input)
              # new_form.add_form_input(new_input)

          # For each leftover input field, tag it to every form.
          # Assumption: On submit, servers will only use the form variable
          #             as required by the user. Therefore, extra inputs
          #             will either (1) be ignored by server
          #                      or (2) crash the server LOL
          if len(formItem.xpath("input")) == 0:
              for key, lonely_input in lonely_inputs.iteritems():
                  new_input = Input()
                  new_input["inputName"] = lonely_input.xpath("@name").extract()
                  new_input["inputType"] = lonely_input.xpath("@type").extract()
                  inputs.append(new_input)
          new_form["fields"] = inputs
          new_forms.append(new_form)
      print "======================================"
      print new_forms
      print "======================================"
      return new_forms

  def generic_extraction_of_forms_and_input(self, url, new_forms, call_process_item=False):
      split_url = url.split("?")
      if len(split_url) > 1:
          # for each param, generate a new form
          for p in re.split("&","".join(split_url[1:])):
              new_form = Form()
              new_form["method"] = ["GET".decode("utf-8")]
              action = split_url[0].decode("utf-8")
              ins = []
              split_param = p.split("=")
              # for n params, each form should stil contain n-1 params in the action
              if len(split_param) > 1:
                  action += "?"
                  for p2 in re.split("&","".join(split_url[1:])):
                      if p == p2:
                          i = Input()
                          i["inputName"] = [split_param[0]]
                          ins.append(i)
                      else:
                          action += p2 + "&"
                  action = action[:-1]
              else:
                  i = Input()
                  i["inputName"] = [split_param[0]]
                  ins.append(i)

              new_form["action"] = [action]
              new_form["fields"] = ins
              new_forms.append(new_form)

          if call_process_item and "action" in new_form and "method" in new_form:
              print "I am in calling"
              itemproc = self.crawler.engine.scraper.itemproc
              itemproc.process_item(new_form,self)

      return new_forms

  def parse_header_type(self, header_type, req):
      headers = req.headers[header_type]
      #example of cookie PHPSESSID=ks4dsu79gf7ve17uu3rfhmh581; display_all_courses=1;
      new_form = Form()
      new_form["method"] = ["Header"]
      new_form["action"] = [req.url]
      input_field = Input()
      param_field = None
      for paramvalue in re.split("; ",headers):
          param=re.split("=",paramvalue)
          if len((param))>0:
              if len(param[0])>0:
                  param_field = header_type
      if param_field != None:
          input_field["inputName"] = [param_field]
          new_form["fields"] = [input_field]
      return new_form
