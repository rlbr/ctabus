from argparse import parser
parser = argparse.ArgumentParser(prog = 'ctabus')
parser.add_argument('arg',metavar = 'stop-id | cross streets')
parser.add_argument('-r','--route')
parser.add_argument('-d','--direction')
args = parser.parse_args()
if args.arg.isdecimal():
    pass
else:
    pass