import os
from os.path import expanduser

#make sure we have an output directory in your home directory.
#on linux and mac this should be ~/mrscoleman-blog
#on windows this should be C:\Users\<Your Username>\mrscoleman-blog
BASE_DIR = os.path.join(expanduser("~"),".mrscoleman-blog")

