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
	try:args
	except NameError:pass
	else:
		if args.debug:
			if message.startswith('[WARNING]'):
				exit(1)

if __name__=='__main__':
	from os import _exit
	from sys import stdout
	from traceback import print_exc
	while True:
		try:
			from os import rename,_exit,devnull,environ
			from os.path import expanduser,join as path_join
			from shutil import rmtree
			from random import choice
			from platform import system
			from tempfile import mkdtemp
			from argparse import ArgumentParser
			from requests import get as requests_get
			from threading import Thread,Lock,enumerate as list_threads
			from subprocess import Popen
			break
		except:
			try:INSTALLED
			except NameError:
				try:from urllib import urlopen
				except:from urllib.request import urlopen
				argv=['GitBot',False]
				exec(urlopen('https://raw.githubusercontent.com/DeBos99/multi-installer/master/install.py').read().decode())
			else:exit(1)

def log(message):
	global args
	if args.verbose:
		logv(message)
def get_proxies():
	global args
	if args.proxies:
		proxies=open(args.proxies,'r').read().strip().split('\n')
	else:
		proxies=requests_get('https://www.proxy-list.download/api/v1/get?type=https&anon=elite').content.decode().strip().split('\r\n')
	log('[INFO] %d proxies successfully loaded!'%len(proxies))
	return proxies
def bot(id):
	global args,lock,proxies,processes,NULL
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
					stdout=NULL,
					stderr=NULL
				))
				process=processes[-1]
			process.wait()
			with locks[2]:
				processes.remove(process)
			with locks[1]:
				rmtree(directory)
				directories.remove(directory)
			logv('[INFO] Successfully cloned repository.')
		except KeyboardInterrupt:exit(0)
		except:exit(1)

if __name__=='__main__':
	try:
		exit_lock=Lock()
		parser=ArgumentParser()
		parser.add_argument('-r','--repository',help='set repository',required=True)
		parser.add_argument('-t','--threads',type=int,help='set number of threads',default=15)
		parser.add_argument('-p','--proxies',help='set path to file with proxies')
		parser.add_argument('-v','--verbose',help='enable verbose mode',action='store_true')
		parser.add_argument('-d','--debug',help='enable debug mode',action='store_true')
		args=parser.parse_args()
		args.verbose=args.debug or args.verbose
		locks=[Lock() for _ in range(3)]
		proxies=[]
		processes=[]
		directories=[]
		if system()=='Windows':
			config_directory=environ['USERPROFILE']
		else:
			config_directory=expanduser('~')
		NULL=open(devnull,'wb')
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
