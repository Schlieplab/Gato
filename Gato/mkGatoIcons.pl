#!/usr/bin/env perl

################################################################################
#
# Create a PythonFile containing all the gifs passed on the command line
# as base64-encrypted strings. The name of the strings are the basename
# of the gif-file.
#
#
use File::Basename;


$header = '################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   GatoIcons.py
#	        automatically created by mkGatoIcons
#
#       _COPYRIGHT_
#
#
################################################################################
';

$outfile = "GatoIcons.py";
$base64  = "base64 -base64 -e -in";

print "# --------- mkGatoIcons.pl - creating $outfile\n";
open(FILE,">$outfile") || warn "Cannot open file $outfile!\n";

print FILE $header;

foreach $file (@ARGV) {

  print "# working on $file\n";
  ($name, $path, $suffix) = fileparse($file, '\.gif');

  print FILE "$name = \"\"\"\n";
  print FILE `$base64 $file`;
  print FILE "\"\"\"\n\n\n";
  
}

