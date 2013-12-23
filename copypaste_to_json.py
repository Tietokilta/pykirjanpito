import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()
output = []

with open(args.filename) as fp:
    data = fp.readlines()

for line in data:
    line = line.strip().replace('TILISIIRTO ','TILISIIRTO  ')
    parts = filter(lambda x: x != '', [x.strip() for x in line.split("  ")])
    if parts[1] in ['PANO', 'PALVELUMAKSU']:
        parts.insert(2, '-')
    sign = '+'
    if len(parts) == 4:
        parts.insert(3, '')
    #print parts
    if parts[4][0] == '-':
        sign = '-'
    output.append(  {
        "id": 0,
        "name": parts[1],
        "amount": parts[4].replace('-', ''),
        "sign": sign,
        "message": parts[3],
        "date": parts[0].replace('.20','.')
    })

print json.dumps(output)