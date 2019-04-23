import re
import requests
import subprocess
from os import rename,_exit
from os.path import expanduser
from sys import stdin,argv
from traceback import print_exc

try:
	home_directory=expanduser('~')
	rename('%s/.gitconfig'%home_directory,'%s/.gitconfig.bak'%home_directory)
	rename('%s/.git-credentials'%home_directory,'%s/.git-credentials.bak'%home_directory)
	subprocess.call('git config --global http.lowSpeedLimit 1000'.split())
	subprocess.call('git config --global http.lowSpeedTime 600'.split())
	while True:
		proxies=re.findall(re.compile('<td>([\d.]+)</td>'),str(requests.get('https://free-proxy-list.net/').content))
		proxies=['%s:%s'%x for x in list(zip(proxies[0::2],proxies[1::2]))]
		print('%d proxies successfully loaded!'%len(proxies))
		for proxy in proxies:
			subprocess.call(('git config --global http.proxy %s'%proxy).split())
			current_subprocess=subprocess.Popen('timeout 10 git clone https://github.com/%s'%argv[1],shell=True)
			current_subprocess.wait()
			current_subprocess=subprocess.Popen('rm -rf ytviewer'.split())
except KeyboardInterrupt:exit_code=0
except:exit_code=1
try:
	current_subprocess.terminate()
	subprocess.call('rm -rf ytviewer'.split())
	rename('%s/.gitconfig.bak'%home_directory,'%s/.gitconfig'%home_directory)
	rename('%s/.git-credentials.bak'%home_directory,'%s/.git-credentials'%home_directory)
except:pass
if exit_code!=0:
	print_exc()
_exit(exit_code)
