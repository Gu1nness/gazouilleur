#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, codecs
from contextlib import nested
from gazouilleur.lib.log import loggerr
try:
    from gazouilleur.config import URL_STATS
    from pystache import Renderer
except:
    URL_STATS = None

class Templater:

    def __init__(self):
        self.public_url = '%s/' % URL_STATS.rstrip('/') if URL_STATS else None
        self.templates = os.path.join("web", "templates")

    def render_template(self, template, name, data):
        outfile = template.replace('.html', '_%s.html' % name)
        try:
            ofile = os.path.join("web", outfile)
            with nested(open(os.path.join(self.templates, template), "r"), codecs.open(ofile, "w", encoding="utf-8")) as (temp, generated):
                generated.write(Renderer(string_encoding='utf8').render(temp.read(), data))
            os.chmod(ofile, 0o644)
            return True
        except IOError as e:
            loggerr("Could not write web/%s from %s/%s : %s" % (outfile, self.templates, template, e), action="stats")
            return False

