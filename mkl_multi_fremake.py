#!/usr/bin/python
#:module load python/3.5.2

import xml.etree.ElementTree as ET
import argparse


#: awg_version
def get_awg_version( root='', awg_version='' ) :

    if awg_version == '' : 
        for elem in root.iter('property') :
            if elem.attrib['name'] == 'AWG_VERSION' : awg_version = elem.attrib['value']
    return awg_version


#: platform parser 
def get_platforms( root='', xmlfile='', writeme=True ) :
    
    platform_list = [ elem.attrib.values()[0] for elem in root.iter('platform') ]
    if writeme : 
        print( 3*'******************************' )
        for i in range(len(platform_list)) : print( "{:25s} PLATFORM  {:3d} {}".format(xmlfile,i,platform_list[i]) )
    return platform_list


#: experiment parser
def get_experiments( root='', awg_version='', xmlfile='', writeme=True ) :

    if awg_version == '' : awg_version = get_awg_version( root=root,awg_version=awg_version )
    exp_list = [ elem.attrib.values()[0] for elem in root.iter('experiment') ]
    exp_list = [ iexp.replace("$(AWG_VERSION)", awg_version) for iexp in exp_list ]
    if writeme : 
        print( 3*'******************************' )
        for i in range(len(exp_list)) : print( "{:25s} EXPERIMENT {:3d}   {}".format(xmlfile, i, exp_list[i]) )
    return exp_list


#: regression parser
def get_regressions( root='', expname='expname', xmlfile='', writeme=True ) :

    path="./experiment/[@name='" + expname + "']/runtime/regression"
    reg_list = [ regression.attrib['name'] for regression in root.findall(path) ]
    if writeme : 
        print( 3*'******************************' )
        for i in range(len(reg_list)) : 
            print( " {:25s}  EXPERIMENT  {:30s}  REGRESSION {:3d}   {}".format( xmlfile, expname, i, reg_list[i] ) )


def setup_parser() :
    parser = argparse.ArgumentParser()
    parser.add_argument( '-x', help="-x list of name_of_xml_file.xml"  )
    parser.add_argument( '-t', help="-t  list of targets" )
    parser.add_argument( '-p', help="-p list of platforms" )
    parser.add_argument( '-e', help="-e list of experiments" )
    parser.add_argument( '--list_t', action='store_true', help = '-list_t, prints all targets. Need -x xml_file.xml' )
    parser.add_argument( '--list_p', action='store_true', help = '-list_p, prints all platforms.  Need -x xml_file.xml' )
    parser.add_argument( '--list_e', action='store_true', help = '-list_e, prints all experiments.  Need -x xml_file.xml' )
    parser.add_argument( '--list_r', action='store_true', help = '-list_r, prints all regressions for specified experiment.  Need -x xml_file.xml' )
    return parser


def cleanup_arguments( args='' ) :

    xmlfiles, targets, platforms, experiments = args.x, args.t, args.p, args.e 
    if xmlfiles    != None : xmlfiles    = [ ifile for ifile in xmlfiles.split(',') ]
    if targets     != None : targets     = [ itarget for itarget in targets.split(',') ]
    if platforms   != None : platforms   = [ iplatform for iplatform in platforms.split(',') ]
    if experiments != None : experiments = [ iexperiment for iexperiment in experiments.split(',') ]

    Qget_platforms   = True if args.list_p else False
    Qget_targets     = True if args.list_t else False
    Qget_experiments = True if args.list_e else False
    Qget_regressions = True if args.list_r else False

    return xmlfiles, targets, platforms, experiments, \
        Qget_platforms, Qget_targets, Qget_experiments, Qget_regressions

#: ---------------------------------------------------------------------------------------------------#
#: ---------------------------------------------------------------------------------------------------#


#: get arguments
parser = setup_parser() 
xmlfiles, targets, platforms, experiments,  \
    Qget_platforms, Qget_targets, Qget_experiments, Qget_regressions = cleanup_arguments( args=parser.parse_args() )


#: get trees 
mytrees, myroots = {}, {}
for ifile in xmlfiles : mytrees[ifile] = ET.parse(ifile)
for ifile in xmlfiles : myroots[ifile] = mytrees[ifile].getroot()


if Qget_platforms : 
    for (ifile,iroot) in myroots.items() : 
        get_platforms( root=iroot, xmlfile=ifile )

if Qget_experiments :
    for (ifile,iroot) in myroots.items() : 
        get_experiments( root=iroot, xmlfile=ifile )

if Qget_regressions :
    for (ifile,iroot) in myroots.items() : 
        if experiments == None :  experiments = get_experiments( root=iroot, xmlfile=ifile, writeme=False )
        for iexp in experiments :
            get_regressions( root=iroot, expname=iexp, xmlfile=ifile )




        






