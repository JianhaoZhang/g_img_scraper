import selenium
from selenium import webdriver
import os
import time
import requests
import io
import random
from PIL import Image
import hashlib
from yago_parse_list import *
from tokenize import *
from multiprocessing.pool import ThreadPool



def scroll(wd, interval):
	wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(interval)

def get_urls(query_word, wd, number_images, humanity_interval):
	api = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
	wd.get(api.format(q = query_word.replace('_',' ')))

	urls = set()
	start_point = 0
	trap = 5
	cur = 0
	retry = 20
	while len(urls) < number_images and trap > 0 and retry > 0:
		scroll(wd, humanity_interval)
		try:
			thumbnails = wd.find_elements_by_css_selector("img.rg_ic")
		except Exception:
			continue
		num_thumbnails = len(thumbnails)
		print(f"Located: {num_thumbnails} results")

		for thumbnail in thumbnails[start_point:len(thumbnails)]:
			try:
				thumbnail.click()
				time.sleep(humanity_interval)
				wd.switch_to.window(wd.window_handles[0])
			except Exception as e:
				print(e)
				continue
			try:
				previews = wd.find_elements_by_css_selector("img.irc_mi")
			except Exception:
				continue
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
			if (cur == len(urls)):
				retry -= 1
			cur = cur + len(urls)
			if (len(urls) == 0):
				trap -= 1
			time.sleep(1)
			try:
				button = wd.find_element_by_css_selector(".ksb")
			except Exception:
				continue
			if button != None:
				wd.execute_script("document.querySelector('.ksb').click();")
		start_point = len(thumbnails)

	return urls

def image_dl(target_dir, url):
	try:
		image_raw = requests.get(url, timeout=30).content
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
				image.save(f, "JPEG", quality=85)
				return name
		else:
			print(f"Dropped: {url} - due to low quality")
			return "Error"
	except Exception as e:
		print(f"Failed: {url} - {e}")
		return "Error"

def image_batch_dl(entry):
	url = entry[0]
	query_word = entry[1]
	print(url)
	hashcode = image_dl("./images/parallel", url)
	if hashcode != "Error":
		with open ("reference.csv", "a+", encoding="utf-8") as f:
			f.write(hashcode + "," + query_word)
			return 1
	else:
		return 0

def parallel_dispatcher(urls_file, threads):
	urls = []
	if not os.path.exists("./images/parallel"):
		os.makedirs("./images/parallel")
	with open(urls_file, encoding = "utf-8") as urls_file:
		for line in urls_file:
			url = line.split(",")[0]
			t = line.split(",")[1]
			urls.append([url,t])
	pool = ThreadPool(threads)
	results = pool.map(image_batch_dl, urls)
	pool.close()
	pool.join()
	print("success rate: " + str(float(results.count(1))/float(len(results))))


def file_parser(keywords, t):
	l = []
	with open(keywords, encoding="utf-8") as keywords:
		if t == "yago":
			for line in keywords:
				l.append(line)
		elif t == "google":
			for line in keywords:
				l.append(line.split(',')[1])
		elif t == "imagenet":
			for line in keywords:
				candidates = line.split('\'')[1].split(',')
				candidate = random.choice(candidates)
				l.append(candidate.strip(" "))
		else:
			print("parser failed")
	return l

def collect_url_into_csv(query_word, driver_dir, lower_bound, upper_bound, interval):
	chrome_options = webdriver.ChromeOptions()
	# chrome_options.add_argument("--window-size=1920,1080")
	# chrome_options.add_argument("--start-maximized")
	# chrome_options.add_argument("--headless")
	
	with webdriver.Chrome(executable_path = driver_dir, options = chrome_options) as wd:
		number_images = random.choice(range(upper_bound - lower_bound)) + lower_bound
		url_repo = get_urls(query_word, wd, number_images, interval)
		with open ("urls.csv", "a+", encoding="utf-8") as f:
			for url in url_repo:
				f.write(url + "," + query_word + "\n")

def collect_many_category_url(entities, keywords, t, lower_bound, upper_bound, interval):
	l = file_parser(keywords, t)
	fetch_list = []
	if entities > 0:
		fetch_list = random.sample(l, entities)
	else:
		fetch_list = l
	i = 0
	for item in fetch_list:
		print(str(i) + "/" + str(len(fetch_list)) + " : " + item)
		collect_url_into_csv(item, "chromedriver.exe", lower_bound, upper_bound, interval)
		i += 1

def batch_dl_single_query(query_word, target_dir, driver_dir, number_images, interval):
	target_folder = os.path.join(target_dir, "results")
	if not os.path.exists(target_folder):
		os.makedirs(target_folder)

	with webdriver.Chrome(executable_path = driver_dir) as wd:
		url_repo = get_urls(query_word, wd, number_images, interval)

		print("Working on batch download...")
		i = 1
		for url in url_repo:
			print(f"{i}/{len(url_repo)}")
			hashcode = image_dl(target_folder, url)
			if hashcode != "Error":
				with open ("reference.csv", "a+", encoding="utf-8") as f:
					f.write(hashcode + "," + query_word)
			i+=1

def batch_dl_many_queries(entities, keywords):
	#parse_list(sourcefile,resultfile, entities)
	l = []
	with open(keywords, encoding="utf-8") as keywords:
		for line in keywords:
			l.append(line)
	fetch_list = random.sample(l, entities)
	print(f"{entities} random keywords")
	i = 1
	for item in fetch_list:
		batch_dl_single_query(item, "./images", "chromedriver.exe", 100, 0.1)
		print(f"{i}-th keyword complete")
		i+=1
	print("Finished")

def batch_dl_many_queries_google(entities, keywords):
	#parse_list(sourcefile,resultfile, entities)
	l = []
	with open(keywords, encoding="utf-8") as keywords:
		for line in keywords:
			l.append(line.split(',')[1])
	fetch_list = random.sample(l, entities)
	print(f"{entities} random keywords")
	i = 1
	for item in fetch_list:
		batch_dl_single_query(item, "./images", "chromedriver.exe", 100, 0.1)
		print(f"{i}-th keyword complete")
		i+=1
	print("Finished")


#batch_dl_single_query("cat", "./images", "chromedriver.exe", 50, 0.1)
#tokenize('taxonomy.csv', 'granular_types.txt', 'tokens.txt')
#batch_dl_many_queries(100, 'tokens.txt')
#batch_dl_many_queries_google(1000, 'class-descriptions.csv')
collect_many_category_url(100, "imagenet1000_clsidx_to_labels.txt", "imagenet", 100, 102, 0.1)
parallel_dispatcher("./urls.csv",20)