from os import rename,_exit,devnull,environ
from os.path import expanduser,join as path_join
from sys import stdout
from shutil import rmtree
from random import choice
from tempfile import mkdtemp
from argparse import ArgumentParser
from requests import get as requests_get
from platform import system as get_os_type
from traceback import print_exc
from threading import Thread,Lock,enumerate as list_threads
from subprocess import Popen

def exit(exit_code):
	global processes,directories,config_directory
	try:processes
	except NameError:pass
	else:
		for process in processes:
			try:process.terminate()
			except:pass
	try:directories
	except NameError:pass
	else:
		for directory in directories:
			try:rmtree(directory)
			except:pass
	try:config_directory
	except NameError:pass
	else:
		rename(path_join(config_directory,'.gitconfig.bak'),path_join(config_directory,'.gitconfig'))
		rename(path_join(config_directory,'.git-credentials.bak'),path_join(config_directory,'.git-credentials'))
	if exit_code:
		print_exc()
	stdout.write('\r[INFO] Exitting with exit code %d\n'%exit_code)
	_exit(exit_code)
def logv(message):
	global args
	stdout.write('%s\n'%message)
	if message.startswith('[ERROR]'):
		exit(1)
	if args.debug==2:
		if message.startswith('[WARNING]'):
			exit(1)
def log(message):
	global args
	if args.debug:
		logv(message)
def get_proxies():
	global args
	if args.proxies:
		proxies=open(args.proxies,'r').read().strip().split('\n')
	else:
		proxies=requests_get('https://www.proxy-list.download/api/v1/get?type=https&anon=elite').content.decode().strip().split('\r\n')
	print('[INFO] %d proxies successfully loaded!'%len(proxies))
	return proxies
def bot(id):
	global args,lock,proxies,processes,devnull_file
	while True:
		try:
			with locks[0]:
				if len(proxies)==0:
					proxies.extend(get_proxies())
				proxy=choice(proxies)
				proxies.remove(proxy)
			log('[INFO][%d] Connecting to %s'%(id,proxy))
			directory=mkdtemp()
			with locks[1]:
				directories.append(directory)
			with locks[2]:
				processes.append(Popen(
					['timeout','10','git','clone','https://www.github.com/%s'%args.repository,directory],
					env={
						'https_proxy':proxy
					},
					stdout=devnull_file,
					stderr=devnull_file
				))
				process=processes[-1]
			process.wait()
			with locks[2]:
				processes.remove(process)
			with locks[1]:
				rmtree(directory)
				directories.remove(directory)
		except KeyboardInterrupt:exit(0)
		except:exit(2)

if __name__=='__main__':
	try:
		exit_lock=Lock()
		parser=ArgumentParser()
		parser.add_argument('-r','--repository',help='set the repository for the bot',required=True)
		parser.add_argument('-t','--threads',type=int,help='set number of the threads',default=15)
		parser.add_argument('-p','--proxies',help='set the path to the list with the proxies')
		parser.add_argument('-d','--debug',help='show all logs',action='count')
		args=parser.parse_args()
		locks=[Lock() for _ in range(3)]
		proxies=[]
		processes=[]
		directories=[]
		if get_os_type()=='Windows':
			config_directory=environ['USERPROFILE']
		else:
			config_directory=expanduser('~')
		devnull_file=open(devnull,'wb')
		rename(path_join(config_directory,'.gitconfig'),path_join(config_directory,'.gitconfig.bak'))
		rename(path_join(config_directory,'.git-credentials'),path_join(config_directory,'.git-credentials.bak'))
		for i in range(args.threads):
			t=Thread(target=bot,args=(i+1,))
			t.daemon=True
			t.start()
		for t in list_threads()[1:]:
			t.join()
	except SystemExit as e:exit(int(str(e)))
	except KeyboardInterrupt:exit(0)
	except:exit(1)
