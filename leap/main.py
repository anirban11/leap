import argparse

import parse
import prefixtree
import leap
import symbolic_to_region_sample as symreg

argparser = argparse.ArgumentParser(description="run tLsep algorithm to learn an ERA")
argparser.add_argument('--inp', dest='infile', type=str,
                                help="name of .txt file containing the sample", 
                                required=True, metavar="<str>")
argparser.add_argument('--rw', dest='rw', type=bool,
                                help="True if only region words are to be allowed in the sample", 
                                required=False, metavar="<bool>", default=False)
argparser.add_argument('--m', dest='m', type=int,
                                help="maximum constant to appear in the sample (only can be used when --rw is True", 
                                required=False, metavar="<int>", default=-1)
args = argparser.parse_args()



infilename = args.infile # input file name

with open(infilename, 'r') as infile:
    events, pos, neg = parse.parse_input(infile.read())


# ========================================== if region words are to be used
if args.rw: 
    assert args.m != -1 # ensure that m is set
    print(f'converting samples to region words only ...\n')
    m = args.m 
    list_of_events = []
    for e in events:
        list_of_events.append(e.name)
    regions = symreg.create_list_of_regions(m, list_of_events)  # create regions
    pos_old = pos[:]
    neg_old = neg[:]
    pos = []
    neg = []
    for i, p in enumerate(pos_old, start=1):    # convert pos samples to region words
        p_reg = symreg.convert_to_region_words(p, regions)
        pos += p_reg
    for i, n in enumerate(neg_old, start=1):    # convert neg samples to region words
        n_reg = symreg.convert_to_region_words(n, regions)
        neg += n_reg
    print(f'size of sample set containing only region words: {len(pos)+len(neg)}')
# ============================================
pt = prefixtree.create_prefix_tree(pos)
leap.leap(pt, neg)