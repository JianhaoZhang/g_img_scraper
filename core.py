import selenium
import os

def batch_dl(query_word, target_dir, driver_dir, number_images):
	target_folder = os.path.join(target_dir, '_'.join(query_word.lower().split(' ')))
	if not os.path.exists(target_folder):
		os.makedirs(target_folder)

batch_dl("dog food", "./images", "/", 5)