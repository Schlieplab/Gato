#!/usr/bin/env python
import sys
import base64

infile = open(sys.argv[1],'rb')
base64.encode(infile,sys.stdout)
infile.close()
