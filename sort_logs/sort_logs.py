import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument("--sort", "-s", type=str, required=False)
parser.add_argument("--limit", "-l", type=int, required=False, default=10)

args = parser.parse_args()

valid_sorts = ['nMatched', 'nModified', 'docsExamined', 'ninserted','nscanned', 'nscannedObjects']
if args.sort not in valid_sorts:
    print 'Invalid sort, please use one of: ' + ', '.join(str(x) for x in valid_sorts)
    exit

strfilter = args.sort
limit = args.limit

output = []
total  = 0

for line in sys.stdin:
    position = line.find(strfilter)
    total = total + 1
    if position > 0:
        next_space = line.find(' ',position)
        metric = line[position+len(strfilter)+1:next_space]
        output.append({'logline' : line, 'value' : metric})
    if total > limit * 2: #perform a sort and remove part of the array
        output = sorted(output, key=lambda k: int(k.get('value', 0)), reverse=True)
        output = output[:10]
        total = 0

output = sorted(output, key=lambda k: int(k.get('value', 0)), reverse=True)
output = output[:limit]


for i in output:
    print  '(' + i['value'] + ')' + '  --log--> ' + i['logline']
    print '--------------------------------'


