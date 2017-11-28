from output_viewer.index import OutputIndex, OutputPage, OutputGroup, OutputRow, OutputFile
import json

ind = OutputIndex("Test Package")
blob = ind.toJSON("/tmp/index.json")
f = json.load(open("/tmp/index.json"))
print(f["version"])

