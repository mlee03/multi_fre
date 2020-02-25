#!/usr/bin/python
#:module load python/3.5.2

import xml.etree.ElementTree as ET
import argparse
import sys
import subprocess
from multiprocessing import Pool

#: assumes each xml has same the targets, platforms, experiments, and regressions

class allinfo() :

    def __init__( self ) :
        self.xmlfiles    = []  #: [ 'xmlfile1', 'xmlfile2', etc ]
        self.xmltrees    = {}  #: { 'xmlfile1':xmltree1, 'xmlfile2':xmltree2, etc }
        self.xmlroots    = {}  #: { 'xmlfile1':xmlroot1, 'xmlfile2':xmlroot2, etc }
        self.targets     = {}  #: { 'xmlfile1':[targetlist1],     'xmlfile2':[targetlist2]    , etc }
        self.platforms   = {}  #: { 'xmlfile1':[platformlist1] ,  'xmlfile2':[platformlist2]  , etc }
        self.experiments = {}  #: { 'xmlfile1':[experimentlist1], 'xmlfile2':[experimentlist2], etc }
        self.regressions = {}  #: { 'xmlfile1':{exp1:[reglist1]}, 'xmlfile2':{exp2:[regist2]} , etc }
        self.awg_version = {}  #: { 'xmlfile1':awg_version1, 'xmlfile2':awg_version2, etc }
        self.num_procs   = 1
        self.list_platforms   = False
        self.list_targets     = False
        self.list_experiments = False
        self.list_regressions = False
        self.count2exit  = 0


    #: awg_version
    def get_awg_version( self ) :
        for (ifile,iroot) in self.xmlroots.items() :
            if self.awg_version[ifile] == '' : 
                for elem in iroot.iter('property') :
                    if elem.attrib['name'] == 'AWG_VERSION' : self.awg_version[ifile] = elem.attrib['value'] 
        
    #: get roots and trees 
    def get_roots_and_trees( self ) :
        for ifile in self.xmlfiles :
            self.xmltrees[ifile] = ET.parse(ifile)
            self.xmlroots[ifile] = self.xmltrees[ifile].getroot()
        self.get_awg_version()

    #: platform parser 
    def get_platforms( self, writeme=True ) :  
        self.platforms = {}
        for (ifile,iroot) in self.xmlroots.items() :
            self.platforms[ifile] = [ elem.attrib.values()[0] for elem in iroot.iter('platform') ]
            if writeme : 
                print( 3*'******************************' )
                for i in range(len(self.platforms[ifile])) : print( "{:25s} PLATFORM  {:3d} {}".format(ifile,i,self.platforms[ifile][i]) )
        self.count2exit += 1 

    #: experiment parser
    def get_experiments( self, writeme=True ) :
        self.experiments = {}
        for (ifile,iroot) in self.xmlroots.items() :    
            tmplist = [ elem.attrib.values()[0] for elem in iroot.iter('experiment') ]
            self.experiments[ifile] = [ iexp.replace("$(AWG_VERSION)", self.awg_version[ifile]) for iexp in tmplist ]
            if writeme : 
                print( 3*'******************************' )
                for i in range(len(self.experiments[ifile])) : print( "{:25s} EXPERIMENT {:3d}   {}".format(ifile, i, self.experiments[ifile][i]) )
        self.count2exit += 1 


    #: regression parser
    def get_regressions( self, myexp=None, writeme=True ) :
        self.regressions = {}
        for (ifile,iroot) in self.xmlroots.items() : 
            self.regressions[ifile] = {}
            if myexp == None : self.get_experiments( writeme=False ) 
            for iexp in self.experiments[ifile] :
                path="./experiment/[@name='" + iexp + "']/runtime/regression"
                self.regressions[ifile][iexp]  = [ regression.attrib['name'] for regression in iroot.findall(path) ]
                if writeme : 
                    print( 3*'******************************' )
                    for i in range(len(self.regressions[ifile][iexp])) : 
                        print( " {:25s}  EXPERIMENT  {:30s}  REGRESSION {:3d}   {}".format( ifile, iexp, i, self.regressions[ifile][iexp][i] ) )
                            
        self.count2exit += 1 

    #: print targets
    def get_targets( self, writeme=True ) :
        if writeme :
            print( 3*'******************************' )
            print( " TARGET debug-openmp " )
            print( " TARGET repro-openmp " )
            print( " TARGET prod-openmp " )
            print( " TARGET debug " )
            print( " TARGET repro " )
            print( " TARGET prod  " )
        self.count2exit += 1 
        
    #: parse user arguments
    def setup_parser( self ) :
        parser = argparse.ArgumentParser()
        parser.add_argument( '-x', help="-x list of name_of_xml_file.xml"  )
        parser.add_argument( '-t', help="-t list of targets"   )
        parser.add_argument( '-p', help="-p list of platforms" )
        parser.add_argument( '-e', help="-e list of experiments" )
        parser.add_argument( '-r', help="-r list of regressions" )
        parser.add_argument( '--no-link',        action='store_true', help='Do not link for execuable' )
        parser.add_argument( '--force-checkout', action='store_true', help='For a checkout of the code')
        parser.add_argument( '--force-compile',  action='store_true', help='For a new compile script' )
        parser.add_argument( '--list_t', action='store_false', help = '-list_t, prints all targets. Need -x xml_file.xml' )
        parser.add_argument( '--list_p', action='store_false', help = '-list_p, prints all platforms.  Need -x xml_file.xml' )
        parser.add_argument( '--list_e', action='store_false', help = '-list_e, prints all experiments.  Need -x xml_file.xml' )
        parser.add_argument( '--list_r', action='store_false', help = '-list_r, prints all regressions for specified experiment.  Need -x xml_file.xml' )

        args = parser.parse_args()
        self.list_platforms   = args.list_p 
        self.list_targets     = args.list_t 
        self.list_experiments = args.list_e 
        self.list_regressions = args.list_r 
        xmlfiles, targets, platforms, experiments, regressions = args.x, args.t, args.p, args.e, args.r

        #: xmlfiles
        if xmlfiles == None : 
            self.xmlfiles = None
        else :
            self.xmlfiles = [ ifile for ifile in xmlfiles.split(',') ]
            for ifile in self.xmlfiles : self.awg_version[ifile] = '' 
        
        #: targets
        if targets == None : 
            self.targets = None 
        else :
            for ifile in self.xmlfiles : self.targets[ifile] = [ itarget for itarget in targets.split(',') ]

        #: platforms
        if platforms == None : 
            self.platforms == None 
        else :
            for ifile in self.xmlfiles : self.platforms[ifile] = [ iplatform for iplatform in platforms.split(',') ]

        #: experiments
        if experiments ==  None : 
            self.experiments = None 
        else :
            for ifile in self.xmlfiles : self.experiments[ifile] = [ iexperiment for iexperiment in experiments.split(',') ]        

        #: regressions
        if regressions ==None :
            self.regressions = None 
        else :
            for ifile in self.regressions : 
                self.regressions[ifile] = {}
                for iexp in self.experiments : self.regressions[ifile][iexp] = [ ireg for ireg in regression.split(',') ]
        

    #: setup FREmake arguments
    def setup_Fremake_arguments( self, writeme=True ) :
        if self.xmlfiles    == None : sys.exit( "ERROR:  must define xml files"   )
        if self.targets     == None : sys.exit( "ERROR:  must define targets.    --list_t to see targets"     )
        if self.platforms   == None : sys.exit( "ERROR:  must define platsforms  --list_p to see platforms"   )
        if self.experiments == None : sys.exit( "ERROR:  must define experiments --list_e to see experiments" )
        if self.regressions == None : print( "NO REGRESSION for FREMAKE" )

        rfile = self.xmlfiles[0]

        self.num_procs = len(self.experiments[rfile]) * len(self.targets[rfile]) * len(self.platforms[rfile]) * len(self.xmlfiles)
        icount, myruns = 0, [ [] for i in range(self.num_procs) ]
        for ifile in self.xmlfiles : 
            for iexp in self.experiments[ifile] : 
                for iplat in self.platforms[ifile] : 
                    for itarg in self.targets[ifile] : 
                        myruns[icount].append( 'fremake' )
                        for iarg in [ '-x',ifile ] : myruns[icount].append(iarg)
                        for iarg in [ '-p',iplat ] : myruns[icount].append(iarg)
                        for iarg in [ '-t',itarg ] : myruns[icount].append(iarg)
                        myruns[icount].append( iexp )
                        myruns[icount].append( {'xml':ifile, 'awg_version':self.awg_version[ifile]} )
                        icount += 1
        if writeme == True :
            print( 3*'******************************' )
            for irun in myruns : print( irun )
            print( 3*'******************************' )
        return myruns

    def checkout_code( self, myruns=[], writeme=True ) :
        mycheckouts, checkedversions, checkedxml = [], [],[]
        for irun in myruns :
            if irun[-1]['xml'] not in checkedxml :
                checkedxml.append( irun[-1]['xml'] )
                if irun[-1]['awg_version'] not in checkedversions :
                    checkedversions.append( irun[-1]['awg_version'] )
                    tmp = irun[:-1] ; tmp.append( '--force-checkout' )
                    mycheckouts.append( tmp )

        if writeme == True : 
            print( 3*'******************************' )
            print( " will check out " )
            for irun in mycheckouts : print( irun )
            print( 3*'******************************' )
        return mycheckouts

def fremake(irun) :
    subprocess.call(irun[:-1])

def goodbye() :
    print( 3*'******************************' ) 
    sys.exit( "Never say goodbye because goodbye means going away and going away means forgetting - Peter Pan" )

#: ---------------------------------------------------------------------------------------------------#
#: ---------------------------------------------------------------------------------------------------#


#: declare class 
all = allinfo( )

#: get arguments
all.setup_parser()

#: parse xml files
all.get_roots_and_trees()

#: print if prompted
if all.list_platforms   : all.get_platforms()
if all.list_experiments : all.get_experiments()
if all.list_regressions : all.get_regressions()
if all.list_targets     : all.get_targets()
if all.count2exit != 0  : goodbye()


myruns      = all.setup_Fremake_arguments() 
mycheckouts = all.checkout_code( myruns=myruns )

#: checkout 
if __name__ == '__main__':                 #: from TR
    pool = Pool(processes=all.num_procs)   #: Create a multiprocessing Pool.  From TR
    pool.map(fremake, mycheckouts[:] )     #: process data_inputs iterable with pool.  From TR


#: if __name__ == '__main__' for windows
if __name__ == '__main__':                #: from TR
    pool = Pool(processes=all.num_procs)  #: Create a multiprocessing Pool.  From TR
    pool.map(fremake, myruns )            #: process data_inputs iterable with pool.  From TR


