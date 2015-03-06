import csv
import json

x = json.load(open("items.json", "r"))

f = csv.writer(open("items.csv", "w+"))

# Write CSV Header, If you dont need that, remove this line
f.writerow(["category", "date", "comments", "title", "link"])

def maybe(x):
    if x:
        return x[0]
    else:
        return ""

def comments(x):
    if x:
        assert x[0][0] == '('
        assert x[0][-1] == ')'
        return x[0][1:-1]
    else:
        return "0"

for x in x:
    f.writerow([
        maybe(x["category"]),
        maybe(x["date"]),
        comments(x["comments"]),
        maybe(x["title"]),
        maybe(x["link"])])
