import selenium
from selenium import webdriver
import os
import time
import requests
import io
from PIL import Image
import hashlib

def scroll(wd, interval):
	wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(interval)

def get_urls(query_word, wd, number_images, humanity_interval):
	api = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
	wd.get(api.format(q = query_word.replace('_',' ')))

	urls = set()
	start_point = 0
	while len(urls) < number_images:
		scroll(wd, humanity_interval)

		thumbnails = wd.find_elements_by_css_selector("img.rg_ic")
		num_thumbnails = len(thumbnails)
		print(f"Located: {num_thumbnails} results")

		for thumbnail in thumbnails[start_point:len(thumbnails)]:
			try:
				thumbnail.click()
				time.sleep(humanity_interval)
			except Exception:
				continue

			previews = wd.find_elements_by_css_selector("img.irc_mi")
			for preview in previews:
				src = preview.get_attribute('src')
				if src != None:
					urls.add(src)

			if len(urls) >= number_images:
				break

		if len(urls) >= number_images:
			print(f"Collected: {len(urls)} urls, finished")
			break
		else:
			print(f"Collected: {len(urls)} urls, continue..")
			time.sleep(2)
			button = wd.find_element_by_css_selector(".ksb")
			if button != None:
				wd.execute_script("document.querySelector('.ksb').click();")
		start_point = len(thumbnails)

	return urls

def image_dl(target_dir, url):
	try:
		image_raw = requests.get(url).content
	except Exception as e:
		print(f"Could not download {url} - {e}")

	try:
		image_bytes = io.BytesIO(image_raw)
		image = Image.open(image_bytes).convert("RGB")
		width, height = image.size
		name = hashlib.sha1(image_raw).hexdigest() + '.jpg'
		path = os.path.join(target_dir, name)
		if width >= 200 and height >= 200:
			with open(path, 'wb') as f:
				image.save(f, "JPEG", quality=100)
		else:
			print(f"Dropped: {url} - due to low quality")
	except Exception as e:
		print(f"Failed: {url} - {e}")


def batch_dl_single_query(query_word, target_dir, driver_dir, number_images, interval):
	target_folder = os.path.join(target_dir, query_word)
	if not os.path.exists(target_folder):
		os.makedirs(target_folder)

	with webdriver.Chrome(executable_path = driver_dir) as wd:
		url_repo = get_urls(query_word, wd, number_images, interval)

		print("Working on batch download...")
		i = 0
		for url in url_repo:
			print(f"{i}/{len(url_repo)}")
			image_dl(target_folder, url)
			i+=1

def batch_dl_many_queries():
	print("in development")

batch_dl_single_query("American_films", "./images", "chromedriver.exe", 50, 0.1)