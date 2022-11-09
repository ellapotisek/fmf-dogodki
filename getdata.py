import re
import requests
import sys
import os
import time
import html
import csv

sources = [
	"158/zagovori-diplom-fizika",
	"186/zagovori-diplom-matematika",
	"160/zagovori-doktoratov-fizika",
	"185/zagovori-doktoratov-matematika",
	"159/zagovori-magisterijev-fizika",
	"184/zagovori-magisterijev-matematika"
]

#število strani pod posamezno kategorijo, ker te vsa večja števila preusmerijo na 1. stran, kar je precej težko ugotoviti s programom
sources_len = [23, 30, 12, 5, 15, 19]

path_pattern = (
    r'<a href="(?P<path>.*?)" class="news__item news__item--news">'
)
		
dissertation_urls = []

def get_html(url, fname):
	print(f'Loading {url} ...')
	sys.stdout.flush()
	if os.path.isfile(os.path.join("htmls", fname)):
		print(f'{fname} is already saved')
		return
	r = requests.get(url, verify=False) # FMF spletna stran uporablja sumljive TLS extensione, ki jih Python ne podpira
	with open(os.path.join('htmls', fname), 'w', encoding='utf-8') as f:
		f.write(r.text)
		print('Saved!')

	
def get_list_htmls():
	for k, source in enumerate(sources):
		tpl_url = f'https://www.fmf.uni-lj.si/sl/obvestila/agregator/{source}'
		url = tpl_url
		i = 1
		tpl_fname = f'{source[4:]}'
		fname = tpl_fname
		for i in range(1, sources_len[k] + 1):
			time.sleep(.1)
			get_html(url, fname)
			i += 1
			
			with open(f'htmls/{fname}') as f:
				html = f.read()
				
			for match in re.finditer(path_pattern, html):
				trash = match.groupdict()
				dissertation_urls.append(trash["path"])
			
			url = tpl_url + f'?page={i}'
			fname = tpl_fname + f'{i}'

	f = open('paths.txt', "w")
	for path in dissertation_urls:
		f.write(path + '\n')
	f.close() 

id_pattern = (
  r'/(?P<id>[0-9]*?)/'
)

def get_events():
	id_list = []
	with open('paths.txt') as f:
		for path in f:
			path = path[:-1]
			match = re.search(id_pattern, path)
			fname = match.groupdict()["id"]
			get_html(f'https://www.fmf.uni-lj.si{path}', fname)
			id_list.append(fname)
			time.sleep(0.1)
	with open('fnames.txt', 'w') as f:
		for fname in id_list:
			f.write(fname + '\n')

event_pattern = (
	r'<h1>(?P<sth>[^:]*?):\s?'
	#r'(?P<name>.*?)[,.]\s?'
	r'(?P<title>.*?)</h1>\s*?'
	r'<div class="news__info">\s*?'
	r'<div>Datum objave:\s(?P<posted>[0-9.\s]*?)</div>\s*?'
	r'<div class="news__item-source">(?P<d_type>.*?)</div>\s*?'
	r'</div>\s*?<div\sclass="news__blurb">\s+'
	r'(?P<timeplace>.*?)\n'
)

event_pattern2 = (
	r'<li>(?P<com_member>[^<]*?)[,.]?\s?</li>'
)

data_list = []
committees = []

def parse_html(fname):
	try:
		with open(f'htmls/{fname}') as f:
			h = f.read()
		match = re.search(event_pattern, h)
		data = match.groupdict()
		data["id"] = fname
		data_list.append(data)
		committee = re.findall(event_pattern2, h)
		committee = list(map(html.unescape, committee))
		a = dict()
		a["committee"] = committee
		a["id"] = fname
		committees.append(a)
	except:
		pass
	
def get_data():
	with open('paths.txt') as f:
		trash = f.read()
	id_list = trash.split('\n')
	for path in id_list:
		match = re.search(id_pattern, path)
		fname = match.groupdict()["id"]
		parse_html(fname)
	with open('data.txt', 'w') as f:
		for item in data_list:
			f.write(item + '\n')

def make_csv(dicts, keys, fname):
	with open(fname, 'w', encoding='utf-8') as f:
		writer = csv.DictWriter(f, fieldnames=keys)
		writer.writeheader()
		writer.writerows(dicts)
	

