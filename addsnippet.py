import json


try:
    file = open("snippets.json", "r")
    ls = json.loads(file.read())
except Exception:
    ls = {}
print(ls)
file.close()

print("name?")
name = input()

print("code?")
lines = []
while True:
    try:
        line = input()
        lines.append(line)
    except KeyboardInterrupt:
        print("end")
        break
text = '\n'.join(lines)

ls[name] = text

file = open("snippets.json", "w")
file.write(json.dumps(ls))
file.close()
