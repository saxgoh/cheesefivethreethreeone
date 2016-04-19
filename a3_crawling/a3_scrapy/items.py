# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class Website(Item):
  # define the fields for your item here like:
  # name = scrapy.Field()
  url = Field()
  #pass

class Param(Item):
  paramType = Field()
  parameter = Field()

class Form(Item):
  action = Field()
  method = Field()
  fields = Field()
  # form_inputs = []
  # def add_form_input(self,new_input_object):
  #   self.form_inputs.append(new_input_object)

class Input(Item):
  inputName = Field()
  inputType = Field()

