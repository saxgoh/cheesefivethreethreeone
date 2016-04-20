import json
import os
from scrapy import signals
#from datetime import datetime
import time
from urlparse import urlparse
from a3_scrapy.output_struct import OutputStruct, Item
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class A3ScrapyPipeline(object):
    filename=''
    # def __init__(self,filename):
    #   self.mysetting=filename
    #   # print object
    #
    # @classmethod
    # def from_crawler(cls, crawler):
    #     settings = crawler.settings
    #     instance = cls(settings['CUSTOM_SETTINGS_VARIABLE'])
    #     crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
    #     return instance

    # def spider_opened(self, spider):
    #     print "I AM HERE"
    #     print spider.start_urls[0]
    #     self.filename=spider.start_urls[0].replace(":", "").replace("/", "")
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     print self.filename
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    #     self.file = open(self.filename+".json", 'ab')
    #     # do stuff with the spider: initialize resources, etc.
    #     #spider.log("[MyPipeline] Initializing resources for %s" % spider.name)

    def open_spider(self, spider):
      print "------------------------------------------"
      print "=========================================="
      print "------------------------------------------"
      print " OPENED SPIDER "
      print "------------------------------------------"
      print "=========================================="
      print "------------------------------------------"
      print "Started: " + spider.start_urls[0]
      return

    def process_item(self, item, spider):
      print "~~~~~~~~Start of Pipeline~~~~~~~~~~~"
      print item

      # where item --> Form object
      action = item['action'][0]
      method = item['method'][0].lower()

      # for each input field, if name exists, add input to input_arr
      input_set = set()
      for one_input in item['fields']:
        inputName = one_input["inputName"]
        if len(inputName) > 0:
            input_set.add(inputName[0])

      # if action url contains parameter, remove them and add to param list
      additional_arr = []
      split_url = action.split("?")
      if len(split_url) == 2:
        # take only domain from url
        url = split_url[0]
        additional_params = split_url[1].split("&")
        # add each param after ?query1=1&query2=2...
        for additional_param in additional_params:
            param = additional_param.split("=")
            if param[0] != "":
                additional_arr.append(param[0])

        # res = {}
        # remove duplicates after adding new params
        merged_set = input_set.union(additional_arr)
        # turn form into hash
        self.add_to_collated_urls(url, {'type': method, 'param': merged_set}, spider)
        # res[url] = {'type': method, 'param': merged_arr}
        # turn hash into json
        # remove leading and following '[', ']'
        # add to collated urls for printing when spider closes
        # self.add_to_collated_urls(res,spider)

      # use full url under form action
      # res = {}
      # res[str(action)] = {'type': method, 'param': input_arr}
      self.add_to_collated_urls(str(action), {'type': method, 'param': input_set}, spider)
      # self.add_to_collated_urls(res,spider)

      print "~~~~~~~~End of Pipeline~~~~~~~~~~~"
      return

    def add_to_collated_urls(self, url, type_param_struct, spider):
      merged_params = None
      method = type_param_struct["type"]
      if method + " " + url in spider.collated_urls:
        # combine new struct with existing struct
        existing_params = spider.collated_urls[method + " " + url]["param"]
        new_params = type_param_struct["param"]
        merged_params = existing_params | new_params
        type_param_struct["param"] = merged_params
      # json.dumps(res, indent=2)
      # res = res[1:-1]
      # spider.collated_urls.add(res)
      print type_param_struct
      spider.collated_urls[method + " " + url] = type_param_struct
      return

    def close_spider(self, spider):
      print spider.collated_urls
      final_op = {}
      for k,v in spider.collated_urls.iteritems():
        actual_key = k.split(" ")[1]
        actual_value = v
        actual_value["param"] = list(v["param"])
        final_op[actual_key] = actual_value
        # print k + " --> "
        # print v

      append_username=''
      if spider.login:
        final_op["login_required"] = {'path': spider.start_urls[0], 'param': {'username_element_name': spider.username_identifier, 'username_value': spider.username, 'password_element_name': spider.password_identifier, 'password_value': spider.password}}
        append_username="_"+str(spider.username).replace("@","").replace(".","")

      filename = urlparse(spider.start_urls[0]).netloc+append_username+"_"+str(int(time.strftime("%H%M%S")))
      filename = filename.replace(":","").replace("/","")
#      filename = spider.start_urls[0].replace(":","").replace("/","") + "_" + str(int(time.time()))

      if not os.path.exists('output'):
            os.makedirs('output')

      op_file = open("./output/"+filename + ".json", "ab")
      op_file.write(json.dumps([final_op], indent=2))
      # print "------------------------------------------"
      # # for j in spider.collated_urls:
      # #   print j
      # print spider.collated_urls
      #
      # count = len(spider.collated_urls)
      # op_file.write("[{")
      # for j in spider.collated_urls:
      #   count -=1
      #   s = j
      #   if count !=0:
      #       s += ","
      #   op_file.write(s)
      # op_file.write("}]")
      print "------------------------------------------"
      print "=========================================="
      print "------------------------------------------"
      print " CLOSED SPIDER "
      print "------------------------------------------"
      print "=========================================="
      print "------------------------------------------"
      return
