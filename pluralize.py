#!/usr/bin/python3
import re, os
from subprocess import check_output as shell

DICTIONNARIES_PATH = "dicts" #Todo
class Dictionnary():
	def __init__(self, lang):
		self.lang = lang
		self.cmds = {}

		f = self.getFileName("morph.bin")
		self.cmds["analyse"] = ['lt-proc', '-z', f]

		f = self.getFileName("gen.bin")
		self.cmds["gen"] = ['lt-proc', '-z', '-n', f]

		f = self.getFileName("pgen.bin")
		self.cmds["postgen"] = ['lt-proc', '-z', '-p', f]


	def getFileName(self, ext):
		f = os.path.join(DICTIONNARIES_PATH, self.lang + "." + ext)
		if not os.path.exists(f):
			raise Exception("Missing dictionnary: %s"%f)
		return f

	def lt_proc(self, type, data):
		return shell(self.cmds[type], input=data)

	def lt_proc_string(self, type, string):
		string = bytes(string, 'UTF-8')
		piped = self.lt_proc(type, string)
		return str(piped, 'UTF-8')

	def lt_proc_txt(self, type, string):
		string = bytes(string, 'UTF-8')
		deformated = shell("apertium-destxt", input=string)
		piped = self.lt_proc(type, deformated)
		reformated = shell("apertium-retxt", input=piped)
		return str(reformated, 'UTF-8')


	def analyse(self, string):
		lex = self.lt_proc_txt("analyse", string)

		lex = re.split("\\^([^$]+)\\$", lex)[1::2]
		lex = lex[:-1] #Discard trailing dot added by destxt
		return list(map(Word, lex))

	def gen_raw(self, lex):
		return self.lt_proc_string("gen", lex)[:-1] #Remove trailing \0

	def gen(self, lex):
		lex = " ".join(map(lambda x:"^%s$"%(x), lex))
		return self.gen_raw(lex)

	def postgen(self, lex):
		return self.lt_proc_string("postgen", lex)[:-1] #Remove trailing \0



class Word():
	def __init__(self, lex = None):
		if lex:
			t = lex.split('/')
			self.surfaceform = t[0]
			self.lexicalforms = list(map(LexicalForm, t[1:]))
		else:
			self.surfaceform = ""
			self.lexicalforms = []

	def copy(self):
		w = Word()
		w.surfaceform = self.surfaceform
		w.lexicalforms = self.lexicalforms.copy()
		return w

	def toLexicalUnit(self):
		if len(self.lexicalforms)!=1:
			return None
		form = self.lexicalforms[0]
		return "^%s$"%(form)

	def __repr__(self):
		return str({self.surfaceform: list(map(str, self.lexicalforms))})


class LexicalForm():
	def __init__(self, form = None):
		if(form):
			s = re.split("<([^>]+)>", form)
			self.form = s[0]
			self.tags = s[1::2]
		else:
			self.form = ""
			self.tags = set()

	def isUnknown(self):
		return self.form.find("*")!=-1 or len(self.tags)==0

	def copy(self):
		f = LexicalForm()
		f.form = self.form
		f.tags = self.tags.copy()
		return f

	def __repr__(self):
		form = self.form.replace("*", "")
		return form + "".join(map(lambda x: "<%s>"%(x), self.tags))



class Pluralizer():
	def __init__(self, lang):
		self.tagnames = {'nbr': {'sg':'sg', 'pl':'pl'}, 'noun': 'n'} #Todo: work with other languages
		self.dict = Dictionnary(lang)

	def pluralize(self, words):
		tag_noun = self.tagnames["noun"]
		tag_sg = self.tagnames["nbr"]["sg"]
		tag_pl = self.tagnames["nbr"]["pl"]
		words = self.dict.analyse(words)

		for word in words:
			if len(word.lexicalforms)!=1:
				word.lexicalforms = [x for x in word.lexicalforms if tag_noun in x.tags]

		def generate(words):
			lex = " ".join(map(Word.toLexicalUnit, words))
			lex = self.dict.gen_raw(lex)
			return self.dict.postgen(lex)

		pluralizedCombinations = []
		generatedwords = generate(words)
		for i, word in enumerate(words):
			if len(word.lexicalforms)!=1:
				raise Exception("Ambiguous input")

			form = word.lexicalforms[0]
			if form.isUnknown():
				continue
			if not tag_noun in form.tags:
				continue
			if not (tag_sg in form.tags or tag_pl in form.tags):
				continue

			nwords = words.copy()
			nform = form.copy()
			nwords[i] = word.copy()
			nwords[i].lexicalforms[0] = nform
			if tag_sg in form.tags:
				nform.tags[nform.tags.index(tag_sg)] = tag_pl
				pluralizedCombinations.append({'singular': generatedwords, 'plural': generate(nwords)})
			if tag_pl in form.tags:
				nform.tags[nform.tags.index(tag_pl)] = tag_sg
				pluralizedCombinations.append({'singular': generate(nwords), 'plural': generatedwords})

		return pluralizedCombinations

if __name__ == "__main__":
	string = "Barre de céréales au lait de vache"
	d = Dictionnary("fr")
	print(d.analyse(string))

	p = Pluralizer('fr')
	print(p.pluralize(string))
