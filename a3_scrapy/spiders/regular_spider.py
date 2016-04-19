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
  login = False
  ops = None
  collated_urls = set()
  visit_js = []

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

          # ASSUMPTION: most login forms put username above password
          #             therefore, for our login form, we will use
          #             the first match as username and second match as password
          username_field = this_is_my_form.xpath(".//input[@type='text']/@name").extract()
          password_field = this_is_my_form.xpath(".//input[@type='password']/@name").extract()
          other_fields = this_is_my_form.xpath(".//input[@value!='']")
          if len(username_field) > 0 and len(password_field) > 0:
              submit_data = {str(username_field[0]): self.username, str(password_field[0]): self.password}
              if len(other_fields) > 0:
                  for of in other_fields:
                      if len(of.xpath("@name")) > 0:
                          submit_data[str(of.xpath("@name").extract()[0])] = str(of.xpath("@value").extract()[0])
              print submit_data
              return [scrapy.FormRequest(
                      url=this_is_my_form_url,
                      formdata=submit_data,
                      callback=self.parse_item
              )]
          else:
              return [scrapy.FormRequest(
                      url=this_is_my_form_url,
                      formdata={'username': self.username, 'password': self.password},
                      callback=self.parse_item
              )]
      else:
          self.parse_item(response)

  def parse_javascript(self,response):
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
                  #add leading slash
                  url=str(action[0]).decode('UTF-8')
                  if url.startswith("/"):
                     new_form['action'] = [url]
                  else:
                     new_form['action'] = ["/"+url]
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

  def request_javascript(self,url):
      print "i am in request"
      if url in self.visit_js:
         print "Javascript visited"
         print url
      else:
         self.visit_js.append(url)
         print url
         out = check_output(["curl", "-k", "-sS", url])
         test = self.parse_javascript(out)
         return


  def parse_item(self, response):
      # if response.status == 500:
      #     print "spotted meta"
      #     print response.meta
      #     LinkExtractor(allow=(),deny=("logout", "Logout", "Log Out", "Log out", "Sign out"))

      # if self.login:
      #     print response.body
      new_forms = []
      sel = Selector(response)
      form = sel.xpath('//form[@action and @method]')

      # This is to capture headers with...
      print "HEADERS HERE"
      print "HEADERS HERE"
      print "HEADERS HERE"
      print "HEADERS HERE"
      print "HEADERS HERE"
      print "HEADERS HERE"
      print response.headers

      if "Location" in response.headers:
           print response.headers
      elif "Language" in response.headers:
           print response.headers
      elif "Cookie" in response.headers:
           print response.headers
      elif "X-Requested-By" in response.headers:
           print response.headers
      print "HEADERS END"


      # This is to check javascript
      print "Checking Javascript"
      javascript_links = {}
      for javascript_link in sel.xpath("//script/@src"):
         url = response.url+javascript_link.extract()
         self.request_javascript(url)
      print "End check javascript"
      # End check javascript


      lonely_inputs = {}
      for ip in sel.xpath("//input"):
        lonely_inputs[ip.extract()] = ip

      #Extract both GET and POST from form
      for formItem in form:
          new_form = Form()
          new_form['action'] = formItem.xpath('@action').extract()
          new_form['method'] = formItem.xpath('@method').extract()

          if len(formItem.xpath("input")) == 0:
              print "weird form"
              # This are forms with everything outside
              form_items = sel.xpath("//*[ancestor::form]/input")
              form_textareas = sel.xpath("//*[ancestor::form]/textarea")
          else:
              # This are the regular forms
              print "regular form"
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
          # Assumption by Elvin: On submit, servers will only use the form variable
          #                      as required by the user. Therefore, extra inputs
          #                      will either (1) be ignored by server
          #                               or (2) crash the server LOL
          for key, lonely_input in lonely_inputs.iteritems():
              new_input = Input()
              new_input["inputName"] = lonely_input.xpath("@name").extract()
              new_input["inputType"] = lonely_input.xpath("@type").extract()
              inputs.append(new_input)
          new_form["fields"] = inputs
          new_forms.append(new_form)
      print "======================================"
      print "======================================"
      print new_forms
      print "======================================"
      print "======================================"
      return new_forms
