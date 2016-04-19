import re

# Item = {
#   type: GET/POST/HEADER,
#   param: [v1,v2,v3]
# }

class Item:
  item_type = None
  param = []

  def __init__(self, item_type, params):
    if re.search(item_type, "^(GET|POST|HEADER)$"):
      self.item_type = item_type
    self.param = params

# OutputStruct
# {
#   base_url: {
#     path_one: [
#       Item1,
#       Item2
#     ]
#   }
# }

class OutputStruct:
  base_url = None
  relative_paths = {}

  def __init__(self, base_url):
    self.base_url = base_url

  def add_path(self, rpath_name, items):
    self.relative_paths[rpath_name] = items
