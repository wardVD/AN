#!/usr/bin/env python

"""Script to check standard CMS references.
    """

__version__ = "$Revision: Test$"
#$HeadURL: $
#$Id:$

import re
import shutil
import socket
import sys
import os
import io
import string
import subprocess


    

def f5(seq, idfun=None): 
    """From http://www.peterbe.com/plog/uniqifiers-benchmark. Fast method to create a unique list while preserving order (otherwise just use a set)
        """
    # order preserving
    if idfun is None:
       def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
    return result

def extractBalanced(text, delim):
    """ Extract a delimited section of text: available opening delimiters are '{', '"', and  '<'.
        Does not check for escaped delimeters. """
    delims = {"{":"}", '"':'"', "<":">"} # matching closing delims
    if not(delim in delims.keys()):
        pout = text.find(',')+1
        pin = 0
    else:
        pin = text.find(delim) + 1
        if pin == 0: 
            print('Bad delim')
        nbraces = 1;
        pout = pin
        while nbraces > 0:
            if pout > len(text): 
                print("extractBalanced >>> Error parsing text: {0}".format(text[pin:pin+min([len(text),15])]))
                return [0, None] # probably unmatched } inside TeX comment string
            if text[pout:pout+2] == '\\'+delim: # look for escaped delim
                pout += 2
            else:
                if text[pout:pout+2] == '\\'+delims[delim]:
                    pout += 2
                else:
                    if text[pout:pout+1] == delims[delim]:
                        nbraces -= 1
                    elif text[pout:pout+1] == delim:
                        nbraces += 1
                    pout += 1
    return [pout, text[pin:pout-1]]

class cleanError(Exception):
    """Base class for exceptions in this module."""
    pass

class cleanRefs:

    def __init__(self, tag, baseDir, verbose):
        self._tag = tag
        self._refs = [] # references from paper: bibkey
        self._verbosity = verbose
        self._bib = {} # holds tuple (artType, {fieldName:fieldValue}), key is bibkey in bib file (same as used in _refs)
        self._rules =[ ('VOLUME',re.compile('[A-G]\s*\d'),'Volume with serial number'),
                       ('VOLUME',re.compile(r'\\bf'), r'Volume with \bf'), # change to be any control sequence
                       ('VOLUME',re.compile('CMS'), 'PAS as article? Please use TECHREPORT'),
                       ('AUTHOR',re.compile('[A-Z]\.[A-Z]'),'Author with adjacent initials'),
                       ('AUTHOR',re.compile('et al\.'), 'Author with explicit et al'),
                       ('AUTHOR',re.compile(r'\\etal'), 'Author with explicit etal'),
                       ('AUTHOR',re.compile(r'Adolphi'), 'Adolphi: this may be an error in attribution for the CMS detector paper. Please check'),
                       ('JOURNAL',re.compile('CMS'), 'PAS as article? Please use TECHREPORT'),
                       ('JOURNAL',re.compile('[A-z]\.[A-z].'), 'Missing spaces in journal name'),
                       ('JOURNAL',re.compile('~'), 'Found ~ in a journal name--don\'t override BibTeX'),
                       ('ISSUE',re.compile('.*'), 'Don\'t normally use the ISSUE field'),
                       ('EPRINT',re.compile('(?<!/)[0-9]{7}'), 'Old style arXiv ref requires the archive class (see http://arxiv.org/help/arxiv_identifier)'),
                       ('TITLE',re.compile('(?i)MadGraph.*v4'), 'MadGraph v5 references are preferred over v4 (unless v4 was what was actually used)'),                       
                       ('DOI',re.compile('doi|DOI'), 'Do not include dx.doi.org'),
                       ('DOI',re.compile(','), 'Only one doi in the DOI field'),
                       ('COLLABORATION',re.compile(r'Collaboration'), r'Should not normally use Collaboration: already in the format'), 
                       ('PAGES',  re.compile('-'), 'Range in page field: we only use first page') ] # rules for checking format: field, compiled re, message. (Add severity?)
        self._blankCheck = re.compile(r'^\s+$')
        # field ordering not yet implemented (if ever)
        self._fieldOrder = ('AUTHOR','COLLABORATION','TITLE','DOI','JOURNAL','VOLUME','TYPE','NUMBER','YEAR','PAGES','NOTE','URL','EPRINT','ARCHIVEPREFIX') #SLACCITATION always last
        # self._baseDir = r'C:\Users\George Alverson\Documents\CMS\tdr2\utils\trunk\tmp\\'
        self._baseDir = baseDir

        
    def getRefList(self):
        """Open the aux file and extract the \citation lines, adding the citations contained to an ordered list, which should match the bibtex reference order.
           """
        #\citation{Dawson:1983fw,Beenakker:1996ch,Plehn:2005cq,Beenakker:2009ha}

        # Use \bibcite instead? What about multi-refs?
        #\bibcite{Beenakker:2009ha}{{10}{}{{}}{{}}}
        badrefs = ['REVTEX41Control', 'apsrev41Control']

        file =  os.path.join(self._baseDir,self._tag + '_temp.aux')
        f = io.open(file,'r')
        refs = []
        for line in f:
            if line.startswith('\citation'):
                newrefs = line[10:len(line)-2].split(',')
                tested = newrefs in badrefs
                if not (newrefs[0] in badrefs):
                    refs.extend(newrefs)
                #print(refs)
        self._refs = f5(refs)
        f.close()

    def getRefs(self):
        """Open the bibfile and scan for "@artType{citation,", where citation matches one we are looking for. Extract the fields
           """
        file = os.path.join(self._baseDir,'auto_generated.bib')
        bibparse = re.compile('^\s*@(\S*)\s*\{',re.MULTILINE) # look for an entire bib entry
        tagparse = re.compile('^\s*(\S*)\s*,',re.MULTILINE) # find the bib tag
        f = io.open(file,'r')
        try:
            bibs = f.read()
        except UnicodeDecodeError:
            print('>>Unicode detected. {0} contains Unicode characters (typically quote marks or ligatures from cut and paste from Word). These are not allowed with the standard BibTex (requires BibTeX8).'.format(file))
            f.close()
            f = io.open(file,'rb')
            text = f.read()
            # check for Unicode characters
            p8 = re.compile(b"[\x80-\xFF]",re.DOTALL)
            pm = p8.findall(text)
            for cand in pm:
                index = text.find(cand)
                print("...Byte {0}: {1}".format(index,text[index:index+25]))
            f.close()
            print('Continuing using Unicode...')
            f = io.open(file,'r',encoding="UTF-8")
            bibs = f.read()
        f.close()
        p = 0
        m = bibparse.search(bibs[p:])
        while m:
            artType = m.group(1).upper()
            [pout, body] = extractBalanced(bibs[p+m.end(0)-1:],'{')
            t = tagparse.match(body)
            if (t):
                tag = t.group(1)
                items = self.parseBody(tag, body[t.end(0):])
                if tag in self._bib.keys():
                    print(">>> Duplicate entry for {0} being discarded".format(tag))
                else:
                    self._bib[tag] = (artType, items)
            else:
                raise cleanError("WARNING: Could not find a tag in string starting with: {0}".format(body.strip()[0:min([len(body.strip()), 25])])) 
            p = p + m.end(0) -1 + pout
            m = bibparse.search(bibs[p:])


    def parseBody(self, tag, body):
        """extract the tag and the fields from a citation"""

        # need to protect against "=" inside a URL.
        fieldparse = re.compile('\s*(\S*)\s*=\s*(\S)',re.MULTILINE)
        trim = re.compile('\s{2,}|\n',re.MULTILINE) # what about \r
        p = 0
        m = fieldparse.search(body[p:])
        entry = {}
        while m:
            field = m.group(1).upper()
            [pout, value] = extractBalanced(body[p+m.end(0)-1:],m.group(2))
            value = trim.sub(' ',value)
            entry[field] = value
            p = p + m.end(0) -1 + pout
            m = fieldparse.search(body[p:])

        if self._verbosity > 2:
            for key in entry.keys():
                print("{0}\t: {1}".format(key, entry[key]))

        return entry


    def checkRefs(self):
        """Correlate citations against bib file and check for common errors"""

        print("\n>>> Checking references against CMS rules\n")
        no_collab_rule = re.compile('Collaboration') # to check for a Collaboration as author: not _generally_ okay for papers

        for key in self._refs:
            if not key in self._bib:
                print("Missing bib entry for citation {0}. May be an upper/lower case problem (ignorable)".format(key))
            else:
                #
                # rule-based checks on particular fields
                #
                for rule in self._rules:
                    fieldName = rule[0]
                    if fieldName in self._bib[key][1].keys():
                        m = rule[1].search(self._bib[key][1][fieldName])
                        if m:
                            print("{0}:\t {1} problem; {2}.".format(key, rule[0], rule[2]))
                #
                # ad hoc checks
                #
                if self._bib[key][0]=='ARTICLE':
                    if not 'AUTHOR' in self._bib[key][1].keys():
                        print('{0}:\t Missing AUTHOR '.format(key))
                    else:
                        m = no_collab_rule.search(self._bib[key][1]['AUTHOR'])
                        if m:
                            print("{0}:\t {1} listed as author. Please check this is correct.".format(key, self._bib[key][1]['AUTHOR']))                                           
                    if not 'DOI' in self._bib[key][1].keys():
                        print('{0}:\t Missing DOI '.format(key))
                    if not 'EPRINT' in self._bib[key][1].keys():
                        print('{0}:\t Missing EPRINT '.format(key))
                    if not 'JOURNAL' in self._bib[key][1].keys():
                        print('{0}:\t Missing JOURNAL. Reformat as UNPUBLISHED?'.format(key))
                # number of authors check
                if 'AUTHOR' in self._bib[key][1].keys():
                    etal = re.search(' and others', self._bib[key][1]['AUTHOR']) 
                    authors_list = re.findall(" and ", self._bib[key][1]['AUTHOR'])
                    #print('{0}'.format(self._bib[key][1]['AUTHOR']))
                    nauthors = len(authors_list) + 1
                    if etal:
                        nauthors = nauthors - 1
                    collab = 'COLLABORATION' in self._bib[key][1].keys()
                    # here's the actual test 
                    if (nauthors > 1) and etal and collab:
                        print('{0}:\t Author count. More authors than necessary for a paper with a collaboration. List only the first plus "and others".'.format(key))
                    if (nauthors > 1 and nauthors < 15) and etal and not(collab):
                        print('{0}:\t Author count. Incomplete author list. Include all authors up through 15'.format(key))
                    if (nauthors > 15) and ~collab:
                        print('{0}:\t Author count. More authors than necessary. Include only the first fifteen plus "and others".'.format(key))
                    if (nauthors==1) and etal and not(collab):
                        print('{0}:\t Author count query. Are there really more than 15 authors for this reference?'.format(key))
                    # diagnostic
                    # print('{0}:\t Number of authors {1} '.format(key, nauthors))

                # check for both url and doi
                if 'DOI' in self._bib[key][1].keys() and 'URL' in self._bib[key][1].keys():
                    print('{0}:\t Both DOI and URL. DOI only is preferred.'.format(key))
                
                # empty/blank field check
                for item in self._bib[key][1].items():
                    if not item[1]:
                        print('{1}: Empty value for field {0}'.format(item[0],key))
                    m = self._blankCheck.search(item[1])
                    if m:
                        print('{1}: Blank value for field {0}'.format(item[0],key))                        
                #print(self.printCite(key))

    def rewrite(self):
        """Write out a new bib file. Default for now is just to reset the collab field"""
        if self._verbosity > 2:
            print("\n>>>rewrite: Rewriting a new bib file\n")
        outfile = os.path.join(self._baseDir,'auto_generated.bib') # overwrite original
        f = io.open(outfile,'w')
        for key in self._refs:
            if ('COLLABORATION' in self._bib[key][1].keys() and self._bib[key][1]['COLLABORATION'] in ['CMS', 'ATLAS', 'LHCb', 'ALICE']):
                self._bib[key][1]['AUTHOR'] = '{'+self._bib[key][1]['COLLABORATION']+' Collaboration}'
                del self._bib[key][1]['COLLABORATION']
            f.write(self.printCite(key))
        f.close()
    def printCite(self, key):
        """Print out a complete bibtex entry"""
        t = ["\t"+zi[0]+"=\t\""+zi[1]+"\",\n" for zi in self._bib[key][1].items()]
        tt = "".join(t)
        return '@{0}'.format(self._bib[key][0])+'{'+'{0},\n'.format(key)+tt+'}'

    def printLog(self):
        print("\n>>> Dumping BibTeX log file\n")
        file =  os.path.join(self._baseDir,self._tag + '_temp.blg')
        f = io.open(file,'r')
        for line in f:
            print(line), # add comma at end to suppress additional newlines





def main(argv):
    from optparse import OptionParser

    usage = "Usage: %prog [options]  tag"
    pat = re.compile("\$Revision:\s+(\d+)\s+\$")
    global version
    versionOK = pat.search(__version__)
    if versionOK:
        version = versionOK.group(1)
    else:
        version = "Test"
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-v", "--verbosity", action="count", dest="verbose", default=False,
                        help="trace script execution; repeated use increases the verbosity more")
    parser.add_option("-b",  "--base", action="store", dest="base", help="base of build area", default=r"E:\tdr2\utils\trunk\tmp")
    parser.add_option("-r", "--rewrite", action="store_true", dest="rewrite", default=False, help="rewrites the bib file and overwrites in base directory")
    global opts
    (opts, args) = parser.parse_args()
    if opts.verbose:
        print("\tVerbosity = {0}".format(opts.verbose))
        print(opts)
    tag = ""
    if len(args) > 0:
        tag = args[len(args)-1]
    else:
        print("Missing document tag (XXX-YY-NNN). Quitting.")
        exit

        
   
 
    myRefs = cleanRefs(tag, opts.base, opts.verbose)
    myRefs.getRefList()
    myRefs.getRefs()
    myRefs.checkRefs()
    myRefs.printLog()

    if (opts.rewrite):
        myRefs.rewrite()

if __name__ == "__main__":
    main(sys.argv[1:])
   
