def tokenize(taxonomy, output1, output2):
	supercat_set = set()
	cat_set = set()
	token_set = set()
	with open(taxonomy, encoding="utf-8") as tax:
		for line in tax:
			supercat_set.add(line.split(',')[2])
			cat_set.add(line.split(',')[1])
	granular = cat_set - supercat_set
	for val in granular:
		tokens = val.replace('<', '').replace('>', '').split('_')
		for t in tokens:
			t = t.replace('"', '').replace('(','').replace(')','').replace('\\n','')
			if len(t) > 1:
				if t.isdigit() and (len(t) > 4) or ('\\u' in t):
					#do nothing
					continue
				else:
					token_set.add(t)

	with open(output2, "w", encoding="utf-8") as o2:
		for val in token_set:
			o2.write(val+"\n")
	with open(output1, "w", encoding="utf-8") as o1:
		for val in granular:
			o1.write(val.replace('<','').replace('>','')+"\n")
