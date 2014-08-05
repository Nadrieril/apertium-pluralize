#!/usr/bin/python3
import re, os
from subprocess import Popen, PIPE

# morph_file = 'fr.morph.bin'
# gen_file = 'fr.gen.bin'
# input_word = cgi.FieldStorage().getvalue("word")


# p = Popen(['lt-proc', morph_file], stdin=PIPE, stdout=PIPE, universal_newlines=True)
# lex = p.communicate(input = input_word+"\n")[0].strip()

# if re.match("^\\^[^/]+/\\*", lex):

# else:
# 	print()
# 	lex = re.sub("^\\^[^/]+/", "^", lex)

# 	lex = lex.replace("<sg>", "<pl>")
# 	p = Popen(['lt-proc', '-g', gen_file], stdin=PIPE, stdout=PIPE, universal_newlines=True)
# 	plural = p.communicate(lex+"\n")[0].strip()

# 	lex = lex.replace("<pl>", "<sg>")
# 	p = Popen(['lt-proc', '-g', gen_file], stdin=PIPE, stdout=PIPE, universal_newlines=True)
# 	singular = p.communicate(lex+"\n")[0].strip()

# 	print('{"singular": "%s", "plural": "%s"}'%(singular, plural))


DICTIONNARIES_PATH = "dicts" #Todo
class Dictionnaries():
	@staticmethod
	def getFileName(lang, type, compiled):
		ext = ".%s.%s"%(type, "bin" if compiled else "dix")
		return os.path.join(DICTIONNARIES_PATH, lang + ext)

	@staticmethod
	def exists(lang):
		return os.path.isfile(Dictionnaries.getFileName(lang, "morph", True)) and os.path.isfile(Dictionnaries.getFileName(lang, "gen", True))

	@staticmethod
	def get(lang):
		if not lang in Dictionnaries.loaded:
			Dictionnaries.loaded[lang] = Dictionnary(lang)
		return Dictionnaries.loaded[lang]



class Dictionnary():
	def __init__(self, lang):
		self.lang = lang
		self.procs = {}

		f = Dictionnaries.getFileName(lang, "morph", True)
		self.procs["morph"] = Popen(['lt-proc', '-z', f], stdin=PIPE, stdout=PIPE)

		f = Dictionnaries.getFileName(lang, "gen", True)
		self.procs["gen"] = Popen(['lt-proc', '-z', '-g', f], stdin=PIPE, stdout=PIPE)


	@staticmethod
	def pipe_cmd(cmd, data):
		return Popen(cmd, stdin=PIPE, stdout=PIPE).communicate(input = data)[0]

	@staticmethod
	def pipe_lt_proc(proc, data):

		proc.stdin.write(data)
		proc.stdin.write(b'\0')
		proc.stdin.flush()

		output = []
		char = proc.stdout.read(1)
		while char and char != b'\0':
			output.append(char)
			char = proc.stdout.read(1)

		return b"".join(output)

	@staticmethod
	def pipe_lt_proc_string(proc, string):
		if type(string) == type(''): string = bytes(string, 'utf-8')
		deformated = Dictionnary.pipe_cmd("apertium-destxt", string)
		piped = Dictionnary.pipe_lt_proc(proc, deformated)
		reformated = Dictionnary.pipe_cmd("apertium-retxt", piped)
		return str(reformated)

	def morph(self, string):
		return Dictionnary.pipe_lt_proc_string(self.procs["morph"], string)
	def gen(self, string):
		return Dictionnary.pipe_lt_proc_string(self.procs["gen"], string)


d = Dictionnary("fr")
# print(d.pipe(d.procs["morph"].stdin, d.procs["morph"].stdout, "Cheval maison"))
# print(d.translate("cheval maison"))
print(d.morph("Gâteau"))

# class Pluralizer(Object):
# 	def __init__(self, lang):
