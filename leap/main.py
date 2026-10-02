import aalpy
import argparse

import parse
import prefixtree
import leap
import symbolic_to_region_sample as symreg

argparser = argparse.ArgumentParser(description="run LEAP algorithm to learn an ERA")
argparser.add_argument('--inp', dest='infile', type=str,
                                help="name of .txt file containing the sample", 
                                required=True, metavar="<str>")
argparser.add_argument('--rw', dest='rw', action="store_true",
                                help="use this flag to use LEAP on region words included in the sample", 
                                required=False, default=False)
argparser.add_argument('--rpni', dest='rpni', action="store_true",
                                help="True if RPNI is to be used on the region words included in the sample", 
                                required=False, default=False)
argparser.add_argument('--m', dest='m', type=int,
                                help="maximum constant to appear in the sample (only can be used when --rw is True", 
                                required=False, metavar="<int>", default=-1)
argparser.add_argument('--dot', dest='dot', type=str,
                                help="name of the .dot file to which the learned ERA is to be written", metavar="<str>", required=False, default=None)
argparser.add_argument('--render', dest='render', action="store_true",
                                help="render the learned RPNI model to a pdf (only used when --rpni is True)",
                                required=False, default=False)
args = argparser.parse_args()

infilename = args.infile # input file name

with open(infilename, 'r') as infile:
    events, pos, neg = parse.parse_input(infile.read())

if (args.rpni):
    assert not args.rw

# ========================================== if region words are to be used
if args.rpni or args.rw: 
    assert args.m != -1 # ensure that m is set
    print(f'converting symbolic words to region words ...')
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
        if (args.rpni):
            p_reg = symreg.convert_to_region_words_rpni(p, regions, label=True)
            if (p_reg == []):
                p_reg = [(tuple(), True)]
        elif args.rw:
            p_reg = symreg.convert_to_region_words(p, regions)
        pos += p_reg

    for i, n in enumerate(neg_old, start=1):    # convert neg samples to region words
        if (args.rpni):
            n_reg = symreg.convert_to_region_words_rpni(n, regions, label=False)
            if (n_reg == []):
                n_reg = [(tuple(), False)]
        elif args.rw:
            n_reg = symreg.convert_to_region_words(n, regions)
        neg += n_reg
    
    print(f'DONE: size of sample set containing only region words: {len(pos)+len(neg)}')
# ============================================
if (args.rpni):
    data = pos + neg
    model = aalpy.run_RPNI(data, automaton_type='dfa', algorithm='classic')
    if (args.render):
        model.visualize()
    print(f'number of states: {len(model.states)}')
    print(model)
else:
    pt = prefixtree.create_prefix_tree(pos)
    leap.leap(pt, neg)
    # nondetLeap.leap(pt, neg, args.dot)
