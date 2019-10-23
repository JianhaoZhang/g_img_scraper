import random
def parse_list(filename, target_file, entities):
	all_item = 24193408
	randomlist = {}
	for x in range(entities):
		j = random.randint(0, all_item-1)
		randomlist[j] = True
	with open(filename, encoding="utf-8") as origin, open(target_file, "w", encoding="utf-8") as out:
		i = 0
		for line in origin:
			if randomlist.get(i, "00") == True:
				if "rdf:type" in line:
					word = line.split('>')[0]
					word = word.split('<')[1]
					if "/" in word:
						word = word.split('/')[1]
					out.write(word+"\n")
			if (i%1000000 == 0):
				print(f"{i}/{all_item}")
			i+=1
