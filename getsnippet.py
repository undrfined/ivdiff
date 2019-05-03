import json


snippet = input()
try:
    file = open("snippets.json", "r")
    ls = json.loads(file.read())
except Exception:
    ls = {}
print(ls[snippet])
file.close()
