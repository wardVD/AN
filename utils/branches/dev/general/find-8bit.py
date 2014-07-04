#!/usr/bin/env python

"""Script look for 8 bit characters
    """

__version__ = "$Revision: 5556 $"
#$HeadURL: svn+ssh://alverson@svn.cern.ch/reps/admin/tdr2/conf/new-note.py $
#$Id: new-note.py 5556 2011-01-14 13:30:27Z alverson $

import re
import os
import string
import glob

def main(argv):
    import sys
    from optparse import OptionParser

    usage = "Usage: %prog [options]  [filenames]"
    pat = re.compile("\$Revision:\s+(\d+)\s+\$")
    version = pat.search(__version__)
    global opts
    parser = OptionParser(usage=usage, version=version)
    (opts, args) = parser.parse_args()

    for file in glob.glob(args[0]):
        f = open(file,"r",0)
        body = f.read()
        p = re.compile(r"[\x80-\xFF]",re.DOTALL)
        pm = p.findall(body)
        print("Testing %s" % file)
        print pm
        for cand in pm:
            index = body.find(cand)
            print body[index:index+25]
            
            
        print("next...")
        f.close()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
