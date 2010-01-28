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
#
#	file:   GatoIcons.py
#
#       NOTE:   Automatically created by mkGatoIcons.pl
#               Do *not* edit this file manually
#
#
#
#       Copyright (C) 1998-2010, Alexander Schliep, Winfried Hochstaettler and 
#       Copyright 1998-2001 ZAIK/ZPR, Universitaet zu Koeln
#                                   
#       Contact: alexander@schliep.org, winfried.hochstaettler@fernuni-hagen.de             
#
#       Information: http://gato.sf.net
#
#       This library is free software; you can redistribute it and/or
#       modify it under the terms of the GNU Library General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This library is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#       Library General Public License for more details.
#
#       You should have received a copy of the GNU Library General Public
#       License along with this library; if not, write to the Free
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
#
#
################################################################################
';

$outfile = "GatoIcons.py";
$base64  = "./convert2base64.py";

print "# --------- mkGatoIcons.pl - creating $outfile\n";
open(FILE,">$outfile") || warn "Cannot open file $outfile!\n";

print FILE $header;

$init = 'def Init():
    import GatoUtil
    imageCache = GatoUtil.ImageCache() # singleton
';

foreach $file (@ARGV) {

  print "# working on $file\n";
  ($name, $path, $suffix) = fileparse($file, '\.gif');

  print FILE "$name = \"\"\"\n";
  print FILE `$base64 $file`;
  print FILE "\"\"\"\n\n";
  $init = $init . "    imageCache.AddImage(\"Icons/$name.gif\",$name)\n";
}

print FILE "$init\n";
