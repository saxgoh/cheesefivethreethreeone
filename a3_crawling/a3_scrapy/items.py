# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class Form(Item):
  action = Field()
  method = Field()
  fields = Field()

class Input(Item):
  inputName = Field()
  inputType = Field()

