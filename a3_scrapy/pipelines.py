import json
from scrapy import signals
from datetime import datetime
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
      action = item['action'][0]
      method = item['method'][0]

      input_arr = []
      for one_input in item['fields']:
        inputName = one_input["inputName"]
        if len(inputName) > 0:
            input_arr.append(inputName[0])
      # removing duplicates in params
      input_arr = list(set(input_arr))

      additional_arr = []
      split_url = action.split("?")
      if len(split_url) == 2:
        url = split_url[0]
        additional_params = split_url[1].split("&")
        for additional_param in additional_params:
            param = additional_param.split("=")
            if param[0] != "":
                additional_arr.append(param[0])
        res = {}
        merged_arr = list(set(input_arr + additional_arr))
        res[url] = {'type': method, 'param': merged_arr}
        res = json.dumps(res, indent=2)
        res = res[1:-1]
        spider.collated_urls.add(res)

      res = {}
      res[str(action)] = {'type': method, 'param': input_arr}
      res = json.dumps(res, indent=2)
      res = res[1:-1]
      spider.collated_urls.add(res)

      print "~~~~~~~~End of Pipeline~~~~~~~~~~~"
      return

    def close_spider(self, spider):
      filename = spider.start_urls[0].replace(":","").replace("/","")
      op_file = open(filename + ".json", "ab")
      print "------------------------------------------"
      # for j in spider.collated_urls:
      #   print j
      print spider.collated_urls

      count = len(spider.collated_urls)
      op_file.write("[{")
      for j in spider.collated_urls:
        count -=1
        s = j
        if count !=0:
            s += ","
        op_file.write(s)
      op_file.write("}]")
      print "------------------------------------------"
      print "=========================================="
      print "------------------------------------------"
      print " CLOSED SPIDER "
      print "------------------------------------------"
      print "=========================================="
      print "------------------------------------------"
      return
