import json
import os
from scrapy import signals
#from datetime import datetime
import time
from urlparse import urlparse, urljoin
from a3_scrapy.output_struct import OutputStruct, Item
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class A3ScrapyPipeline(object):
    filename=''

    def open_spider(self, spider):
      print "=========================================="
      print " OPENED SPIDER "
      print "=========================================="
      print "Started: " + spider.start_urls[0]
      return

    def process_item(self, item, spider):
      print "^^^^^^^^Start of Pipeline^^^^^^^^^^^"

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

        # remove duplicates after adding new params
        merged_set = input_set.union(additional_arr)
        # turn form into hash
        self.add_to_collated_urls(url, {'type': method, 'param': merged_set}, spider)

      # use full url under form action
      self.add_to_collated_urls(str(action), {'type': method, 'param': input_set}, spider)

      print "^^^^^^^^End of Pipeline^^^^^^^^^^^"
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
      spider.collated_urls[method + " " + url] = type_param_struct
      return

    def close_spider(self, spider):
      print spider.collated_urls
      final_op = {}
      for k,v in spider.collated_urls.iteritems():
        actual_key = k.split(" ")[1]
        actual_key = urljoin(spider.start_urls[0], actual_key)
        actual_value = v
        actual_value["param"] = list(v["param"])
        if actual_key in final_op:
          original = final_op[actual_key]
          original.append(actual_value)
          final_op[actual_key] = original
        else:
          final_op[actual_key] = [actual_value]

      append_username=''
      if spider.login:
        final_op["login_required"] = {'path': spider.start_urls[0], 'param': {'username_element_name': spider.username_identifier, 'username_value': spider.username, 'password_element_name': spider.password_identifier, 'password_value': spider.password}}
        append_username="_"+str(spider.username).replace("@","").replace(".","")

      filename = urlparse(spider.start_urls[0]).netloc+append_username+"_"+str(int(time.strftime("%H%M%S")))
      filename = filename.replace(":","").replace("/","")

      if not os.path.exists('output'):
            os.makedirs('output')

      op_file = open("./output/"+filename + ".json", "ab")
      op_file.write(json.dumps([final_op], indent=2))
      print "=========================================="
      print " CLOSED SPIDER "
      print "=========================================="
      return
