import os

currentdate = '2014-02-27'

os.system("pullrss4.py")
os.system("cleanrss4.py -d " + currentdate)
os.system("getcontent3.py -d " + currentdate)
os.system("imagedownload.py")

