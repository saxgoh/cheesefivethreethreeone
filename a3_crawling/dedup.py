import json

with open("sampleinput.json","r") as f:
  j = json.load(f)

checkset = set()
output = []

for data in j:
  if data not in checkset:
    output.append(data)
    checkset.add(e)

outfile = open("output.json","w")
json.dump(output, outfile, sort_keys=True, indent=4)
outfile.close()
