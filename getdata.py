import re
import requests
import sys
import os
import time

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
