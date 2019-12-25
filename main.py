# Only works on animeflv.net

from copy import copy
from optparse import Option, OptionParser
from bs4 import BeautifulSoup
import urllib.parse, sys, requests, json, ast

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def get_anime_url():
	anime_name = options.get_anime_url
	params = {'value': anime_name}
	animeflv_search = "https://animeflv.net/api/animes/search"
	anime = None

	try:
		response = requests.post(animeflv_search, params=params, headers=headers)
		response.raise_for_status()
		url = "https://animeflv.net/anime/{}/{}"
		data = json.loads(response.content)
		
		if len(data) > 1:
			anime_list = {}
			for key, item in enumerate(data):
				anime_list[key] = item
				print(f"[{key+1}] {item['title']}")
			selected = input("Which one you are looking for? (leave blank if none): ")
			if selected != '':
				anime = anime_list[int(selected)-1]
				anime['url'] = url.format(anime['id'], anime['slug'])
				#print ("URL: ", anime['url'])
			else:
				print("None were selected.")
		else:
			anime = data[0]
			anime['url'] = url.format(anime['id'], anime['slug'])
			print(f"[1] {anime['title']}")
			#print ("URL: ", anime['url'])
			
	except Exception as err:
		print(f'Other error occurred: {err}')

	if anime:
		get_episode_list(anime)


def get_episode_list(anime, default_download='mega'):
	episodes = None
	limit = int(options.limit) if options.limit else 10
	try:
		url = anime['url']
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		print("Anime: ", url)
	
		soup = BeautifulSoup(response.content, 'html.parser')
		script = str(soup.findAll('script')[14])
		episodes = script.split('var episodes = ')[1]
		episodes = ast.literal_eval(episodes[:episodes.find(';')])
	except Exception as e:
		print(e)

	if episodes:
		try:
			for key, episode in enumerate(episodes):
				id   = episode[1]
				slug = anime['slug'] + '-' + str(episode[0])
				episode_url = "https://animeflv.net/ver/{}/{}".format(id, slug)
				print(f"Episode: {episode[0]}")
				choose = 'mega' if options.mega else 'zippyshare' if options.zippyshare else default_download
				get_episode_download_link(episode_url, choose)
				if key+1 >= limit:
					break
		except Exception as e:
			print(e)
		

def get_episode_download_link(url, choose='mega'):
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		soup = BeautifulSoup(response.content, 'html.parser')
		links = [a['href'] for a in soup.findAll('a', {"class": "fa-download"})]
		selected_links = []
		selected_link  = ''
		for link in links:
			if (check_url('','',link)):
				link = urllib.parse.unquote(link)
				if link.find('ouo.io') != -1:
					if options.all:
						selected_links.append(link[link.find('?s=')+3:])
					else:
						selected_link = link[link.find('?s=')+3:]
				if choose in link:
					break
		if options.all:
			print("\n".join(selected_links))
		else:
			print(selected_link)
	except Exception as e:
		print(e)
	

def get_links():
	linklist = []
	print("Write 'Stop' to end the loop.")
	while True:
		url = input("Insert url #{}: ".format(len(linklist)+1))
		if (url.lower() == 'stop'):
			break
		if (check_url('','',url)):
			url = urllib.parse.unquote(url)
			if url.find('ouo.io') != -1:
				linklist.append((url[url.find('?s=')+3:]))

	for key, link in enumerate(linklist):
		print(key+1, link)


def check_url(option, opt, value):
	try:
		if value.startswith('http') or value.startswith('https'):
			return value
		else:
			return None
	except Exception as e:
		print ("error", e)


class URL(Option):
    TYPES = Option.TYPES + ("url",)
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["url"] = check_url


parser = OptionParser(option_class=URL)
parser.add_option("-u", "--url", dest="url", help="decode URL", type="url")
parser.add_option("-r", "--request", dest="get_anime_url", help="scrape for specific anime URLs")
parser.add_option("-l", "--limit", help="limit default=10")
parser.add_option("-m", "--mega", action="store_true", help="download link default mega")
parser.add_option("-z", "--zippyshare", action="store_true", help="download link default zippyshare")
parser.add_option("-a", "--all", action="store_true", help="download all links")
(options, args) = parser.parse_args()


if __name__ == '__main__':
	if options.url:
		url = options.url
		url = urllib.parse.unquote(url)
		if url.find('ouo.io') == -1:
			sys.exit('Not an ouo.io Link')
		else:
			print(url[url.find('?s=')+3:])
	if options.get_anime_url:
		get_anime_url()
	else:
		#print ("Bad HTTP Link")
		get_links()