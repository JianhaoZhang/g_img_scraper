Dependencies: selenium, requests, Pillow, hashlib

Can be installed via pip

Helper functions:

tokenize('taxonomy.csv', 'granular_types.txt', 'tokens.txt') # a yago taxonomy tokenizer

---------------------

Primary functions:

#Entities = number of keywords to retrieve from keywords document

#Keywords = document that contains keywords

#t = type of keywords document

#lower_bound = lowest number of images from single category

#upper_bound = highest number of images from single category

collect_many_category_url(entities, keywords, t, lower_bound, upper_bound, interval)

---------------------

#parallel image download with urls.csv collected by collect_many_category_url

#threads= number of threads to dispatch, recommended 8-16 for normal laptop

parallel_dispatcher("./urls.csv",threads)
