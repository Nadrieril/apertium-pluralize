#!/usr/bin/python3
from ..pluralize import Pluralize

import json
import cgi
import cgitb; cgitb.enable()


lang = cgi.FieldStorage().getvalue("lang")
words = cgi.FieldStorage().getvalue("word")

print("Content-type: application/json")
try:
	p = Pluralize(lang)
	o = p.pluralize(words)
	print()
	print(json.dumps(o))

except:
	print("Status: 404\n")
	print('{"error":{"code":404,"message":"Not Found"}}')
