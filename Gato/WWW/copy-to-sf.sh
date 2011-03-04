#!/bin/bash
#
# Update gato.sf.net website at Sourceforge from a checked out version
# from CVS
#
#
#
#
#
# Files are at /home/project-web/gato/htdocs after shell login

rsync -aiv -r -R --cvs-exclude . schliep,gato@web.sourceforge.net:htdocs/
#ssh gato.sf.net "find /home/groups/g/ga/gato/htdocs -type f -exec chmod 664 {} \;"
#ssh gato.sf.net "find /home/groups/g/ga/gato/htdocs -type d -exec chmod 775 {} \;"
