# Only works on animeflv.net

from copy     import copy
from optparse import Option
from optparse import OptionParser
from bs4      import BeautifulSoup
import urllib.parse
import sys
import requests
import json
import ast
import os

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def add_favorite_anime(anime_name):
	home = os.path.expanduser('~')

	if sys.platform in ('linux', 'linux2'):
		folder_path = home + '/.animeflv'
		list_path   = folder_path + '/favs.dat'

		if not os.path.exists(folder_path):
			os.mkdir(folder_path)
		else:
			if os.path.exists(list_path):
				anime = get_anime_url(anime_name, episode_list=False)
				if anime is not None:
					with open(list_path, 'r') as anime_file:
						anime_list = [item.replace('\n', '').split(',') for item in anime_file.readlines()]
						anime_list = list(filter(lambda x: x[1] == anime['slug'], anime_list))
						if len(anime_list) > 0:
							sys.exit("Anime already exists")
					with open(list_path, 'a+') as anime_list:
						anime_path = f"{folder_path}/{anime['id']}.dat"
						anime_list.write(f"{anime['id']},{anime['slug']}\n")
						open(anime_path, 'a').close()
					sys.exit(f"{anime['title']} added to your favorite list")
				else:
					print("Error - Anime returned None")

	sys.exit(0)


def check_updates():
	home = os.path.expanduser('~')
	
	if sys.platform in ('linux', 'linux2'):
		folder_path = home + '/.animeflv'
		list_path   = folder_path + '/favs.dat'

		if not os.path.exists(folder_path):
			os.mkdir(folder_path)
		else:
			if os.path.exists(list_path):
				with open(list_path, 'r') as list_file:
					for item in list_file.readlines():
						if not item.startswith('#'):
							data  = item.replace('\n','').split(',')
							url   = f"https://animeflv.net/anime/{data[0]}/{data[1]}"
							anime = { 'url': url, 'id': data[0], 'name': data[1] }
							episodes = get_episode_list(anime, updates=True)
							episodes = [",".join([str(it_episode[0]), str(it_episode[1])]) for it_episode in episodes]
							anime_path = f"{folder_path}/{data[0]}.dat"
							not_watched_list = []

							if os.path.exists(anime_path):
								with open(anime_path, 'r') as episode_file:
									episode_list = [episode.replace('\n', '') for episode in episode_file.readlines()]

								for episode in episodes:
									if not episode in episode_list:
										not_watched_list.append(episode)

								for not_watched in not_watched_list:
									episode = not_watched.split(',')
									id = episode[1]
									slug = anime['name'] + '-' + str(episode[0])

									print(f"Not watched episode #{episode[0]}")

									episode_url = f"https://animeflv.net/ver/{id}/{slug}"
									get_episode_download_link(episode_url, all_links=True)
								
									with open(anime_path, 'a+') as episode_file:
										episode_file.write(not_watched + '\n')

								if len(not_watched_list) == 0:
									print("No new episodes")
			else:
				print("No anime list found")
			
	if sys.platform in ('win32'):
		pass

	sys.exit(0)

def get_anime_url(anime_name, episode_list=True):
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
		if episode_list:
			get_episode_list(anime)
		else:
			return anime
	else:
		return None


def get_episode_list(anime, default_download='mega', updates=False):
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
		episodes.sort(key=lambda x:x[0])
		if updates:
			return episodes
	except Exception as e:
		print(e)
		return []

	if episodes:
		try:
			range_limit = None
			if options.range:
				range_limit = [int(n) for n in options.range.split(',')]
				range_limit.sort()
				if len(range_limit) != 2:
					sys.exit('Wrong range specified')
			for key, episode in enumerate(episodes):
				id   = episode[1]
				if range_limit:
					if len(range_limit) == 2:
						if key+1 < range_limit[0] or key+1 > range_limit[1]:
							continue
					
				slug = anime['slug'] + '-' + str(episode[0])
				episode_url = "https://animeflv.net/ver/{}/{}".format(id, slug)
				print(f"Episode: {episode[0]}")
				choose = 'mega' if options.mega else 'zippyshare' if options.zippyshare else default_download
				get_episode_download_link(episode_url, choose)
				if key+1 >= limit:
					break
		except Exception as e:
			print(e)
		

def get_episode_download_link(url, choose='mega', all_links=False):
	all_links = options.all if options.all else all_links
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
					if all_links:
						selected_links.append(link[link.find('?s=')+3:])
					else:
						selected_link = link[link.find('?s=')+3:]
				if choose in link:
					break
		if all_links:
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
parser.add_option("--addfavorite", dest="add_favorite_anime", help="Add your favorite anime to the list")
parser.add_option("-c", "--checkupdates", action="store_true", dest="checkupdates", help="Checks if theres a new episode of your favorite list, needs to add favorites first.")
parser.add_option("--range", help="range example=1,10")
parser.add_option("-m", "--mega", action="store_true", help="download link default mega")
parser.add_option("-z", "--zippyshare", action="store_true", help="download link default zippyshare")
parser.add_option("-a", "--all", action="store_true", help="download all links")
(options, args) = parser.parse_args()


if __name__ == '__main__':
	if options.checkupdates:
		check_updates()
	if options.add_favorite_anime:
		add_favorite_anime(options.add_favorite_anime)
	if options.url:
		url = options.url
		url = urllib.parse.unquote(url)
		if url.find('ouo.io') == -1:
			sys.exit('Not an ouo.io Link')
		else:
			print(url[url.find('?s=')+3:])
	if options.get_anime_url:
		get_anime_url(options.get_anime_url)
	else:
		#print ("Bad HTTP Link")
		get_links()
