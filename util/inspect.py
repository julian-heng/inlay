from urllib.parse import urlsplit
import youtube_dl
import logging
import re

from sites.sites import twitter, reddit

logging.basicConfig(filename="process.log",
                    filemode='a',
                    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)

platforms = {
    "Twitter": twitter,
    "Reddit": reddit
}

def process_site(msg, sites):
    try:
        url = re.search("(?P<url>https?://[^\s]+)", msg).group("url")

        split_url = urlsplit(url)

        logging.debug(f"Using URL {url} parsed -> {split_url}")

        for site in sites:
            if sanitise_base_url(split_url.netloc) in site["catch"]:
                return site, url

        return None, url
    except AttributeError:
        pass # URL not found in regex
    except Exception as e:
        logging.error(f"Error: Could not process URL {e}")
            
    return None, None

def process_url(url, site, direct=False):
    try:
        if direct and not site:
            return extract_info(url)["url"]
        else:
            info = extract_info(url)
            
            if site["name"] in platforms.keys(): # There is a special handler for the URL 
                embed = platforms[site["name"]](info)
            else:
                embed = info["url"] # Attempt get key "URL"

            logging.debug(f"Result string: {embed}")

            return embed
    except Exception as e:
        logging.error(f"Error: Could not get direct link for URL {e}")

    return None

def extract_info(url):
    logging.debug(f"Getting URL {url} information")

    with youtube_dl.YoutubeDL({"format": "bestvideo/best", "quiet": True}) as ydl:
        try:
            return ydl.extract_info(url, download=False) # Also provides rich metadata info
        except Exception as e:
            logging.error(f"Error: Could not get video URL. {e}")

def sanitise_base_url(base):
    return base.replace("www.", "")