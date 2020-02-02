# AnimeFLV scraper

Script to get the download links for your favorite animes

## Usage

Run "python3 main.py"

Default behaviour: just decodes links directly obtained from the website (to ignore link shortners)

### Options:

* -u, --url		Decodes single URL obtained from the website to ignore link shortners) | Requires: [Link]

* -r, --request		Scrapes for specific anime URLS | Requires: [Anime name]

* -l, --limit		Number of episodes to get, default = 10 | Requires: [Number]

* --addfavorite		Adds your favorite anime to the list (works with --checkupdates option) | Requires: [Anime name]

* -c, --checkupdates	Checks if there is a new episode or your favorite anime available (needs to add a favorite anime with --addfavorite)
 
* --range		To skip episodes. Example: Get episodes from 15 to 25 --range 15,25 | Requires: [Range]

* -m, --mega		Get only download links for MEGA

* -z, --zippyshare	Get only download links for Zippyshare

* -a, --all		Get all download links for each episode

### Examples

> python3 main.py --addfavorite "Dr stone"\n
> python3 main.py --checkupdates -a
