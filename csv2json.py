import csv
import json

source = open('data/foi-emails.csv', 'r')
dest = open('data/foi-emails.json', 'w')
csvreader = csv.reader(source)

emails = {}

for line in csvreader:
    emails[line[0]] = line[1]
    # item = dict(name=line[0], email=line[1])

print(json.dumps(emails))
dest.write(json.dumps(emails))