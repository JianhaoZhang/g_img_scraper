import selenium
from selenium import webdriver
import os

def get_urls(query_word, wd, number_images, humanity_interval):
	print(query_word)

def batch_dl_single_query(query_word, target_dir, driver_dir, number_images):
	target_folder = os.path.join(target_dir, '_'.join(query_word.lower().split(' ')))
	if not os.path.exists(target_folder):
		os.makedirs(target_folder)

	with webdriver.Chrome(executable_path = driver_dir) as wd:
		url_repo = get_urls(query_word, wd, number_images, 0.5)

batch_dl_single_query("dog food", "./images", "chromedriver.exe", 5)