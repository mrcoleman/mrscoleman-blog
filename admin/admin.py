import web
import os
from web.contrib.template import render_jinja

render = render_jinja(
        'templates/admin',   # Set template directory.
        encoding = 'utf-8',                         # Encoding.
    )





OUTPUT_DIR = os.path.dirname(os.path.realpath("../static")) #by default we're going to go up one directory and save to the static folder


urls = ("/","index")

app = web.application(urls, globals())

class index:
	def GET (self):
		return render.index()

if __name__ == "__main__":
    app.run()