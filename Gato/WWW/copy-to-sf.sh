#!/bin/bash
#
# Update gato.sf.net website at Sourceforge from a checked out version
# from CVS
#

rsync -r -R --cvs-exclude . gato.sf.net:/home/groups/g/ga/gato/htdocs
ssh gato.sf.net "find /home/groups/g/ga/gato/htdocs -type f -exec chmod 664 {} \;"
ssh gato.sf.net "find /home/groups/g/ga/gato/htdocs -type d -exec chmod 775 {} \;"