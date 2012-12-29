import os
from os.path import expanduser

#make sure we have an output directory in your home directory.
#on linux and mac this should be ~/mrscoleman-blog
#on windows this should be C:\Users\<Your Username>\mrscoleman-blog
BASE_DIR = os.path.join(expanduser("~"),".mrscoleman-blog")

#ftp info
FTP_HOST = ""
FTP_PORT = 21
FTP_USER = ""
FTP_PASSWORD = ""
FTP_STATIC_ROOT = ""
