#!/usr/bin/env python

"""
parse_ssn.py
============
Please type "./parse_ssn.py -h" for usage help

Authors:
  Eric A. Franzosa (franzosa@hsph.harvard.edu)

Copyright (c) 2016 Harvard T. H. Chan School of Public Health

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import print_function # PYTHON 2.7+ REQUIRED 
import os
import sys
import argparse
import csv

#-------------------------------------------------------------------------------
# description
#-------------------------------------------------------------------------------

description = """
DESCRIPTION:

  This is a python program for parsing a sequence similarity 
  network. It is a component of the Chemically-Guided Functional
  Profiling workflow described in:

  <citation>

BASIC OPERATION:

  ./parse_ssn.py nodes.csv edges.csv

ARGUMENTS:
"""

# ---------------------------------------------------------------
# constants
# ---------------------------------------------------------------

c_na = "#N/A"
c_epsilon = 1e-20

# ---------------------------------------------------------------
# arguments
# ---------------------------------------------------------------

def get_args( ):
    """ master argument parser """
    parser = argparse.ArgumentParser( 
        description=description, 
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument( 
        "nodes",
        type=str,
        help="SSN nodes file (csv format)",
    )
    parser.add_argument( 
        "edges",
        type=str,
        help="SSN edges file (csv format)",
    )
    parser.add_argument( 
        "-e", "--min-percid",
        type=float,
        metavar="<0-100>",
        default=0.0,
        help="Filtered edges must exceed this percent identity (Default=0.0)",
    )
    parser.add_argument(
        "-a", "--accession-list",
        type=str,
        metavar="<path>",
        default="cgfp-accessions.txt",
        help="Path to output file 1: list of UniProt protein accession numbers",
    )
    parser.add_argument( 
        "-c", "--clusters-file",
        type=str,
        metavar="<path>",
        default="cgfp-clusters.txt",
        help="Path to output file 2: mapping of accession numbers to clusters (connected components) in the SSN",
    )
    args = parser.parse_args()
    return args

#-------------------------------------------------------------------------------
# helper classes
#-------------------------------------------------------------------------------

class Node:
    def __init__( self ):
        self.visited = False
        self.accessions = None
        self.neighbors = set( )
    def attach( self, node ):
        self.neighbors.add( node )
    def get_connected_component( self ):
        cc, front = {self}, {self}
        while any( [not inode.visited for inode in front] ):
            new_front = set( )
            for inode in front:
                if not inode.visited:
                    inode.visited = True
                    new_front.update( inode.neighbors )
            cc.update( new_front )
            front = new_front
        return list( cc )

#-------------------------------------------------------------------------------
# utilities and file i/o
#-------------------------------------------------------------------------------

def try_open( path, *args ):
    """ open and fail gracefully """
    fh = None
    try:
        fh = open( path, *args )
    except:
        sys.exit( "Unable to open: %s, please check the path" % ( path ) )
    return fh

def read_lines( fh, headers=True, dialect="excel" ):
    for row in csv.reader( fh, dialect=dialect ):
        if headers:
            headers=False
        else:
            yield row

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

def main( ):
    args = get_args()
    nodes = []
    nodes_map = {}
    accessions = set( )
    # load nodes
    for row in read_lines( try_open( args.nodes ) ):
        nd = Node( )
        nodes.append( nd )
        nd.accessions = row[1].split( "|" )
        for acc in nd.accessions:
            nodes_map[acc] = nd
            accessions.add( acc )
    # load edges
    for row in read_lines( try_open( args.edges ) ):
        percid, pair = row[1], row[5]
        if float( percid ) >= args.min_percid:
            a, b = pair.split( "," )
            node_a = nodes_map.get( a )
            node_b = nodes_map.get( b )
            node_a.attach( node_b )
            node_b.attach( node_a )
    # get connected components
    ccs = []
    for node in nodes:
        if not node.visited:
            ccs.append( node.get_connected_component( ) )
    # write accessions
    with try_open( args.accession_list, "w" ) as fh:
        for acc in sorted( accessions ):
            print( acc, file=fh )
    # write cluster mapping
    with try_open( args.clusters_file, "w" ) as fh:
        for i, cluster in enumerate( sorted( ccs, key=lambda x: -len( x ) ) ):
            for node in cluster:
                for acc in node.accessions:
                    print( "{}\t{}".format( i+1, acc ), file=fh )
            
if __name__ == "__main__":
    main( )
