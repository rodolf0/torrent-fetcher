#!/usr/bin/env python

from urllib.request import urlopen
import xml.sax

class SubdivxDownload(xml.sax.handler.ContentHandler):
  def __init__(self):
    # Just some flags to determine if we're in that node
    self.state = { "item" : False, "title" : False,
                   "link" : False, "description": False }
    self.title = ""
    self.link = ""
    self.description = ""
    self.items = []

  def startElement(self, name, attrs):
    if name in self.state:
      self.state[name] = True

  def endElement(self, name):
    if name in self.state:
      self.state[name] = False
    if name == "item":
      self.items.append({
        "title": self.title,
        "link": self.link,
        "desc": self.description
      })

  def characters(self, data):
    if self.state["item"]:
      if self.state["title"]:
        self.title = data
      elif self.state["link"]:
        self.link = data
      elif self.state["description"]:
        self.description= data


def subdivx_downloader(searchstr):
  parser = xml.sax.make_parser()
  handler = SubdivxDownload()
  parser.setContentHandler(handler)
  stream = urlopen('http://www.subdivx.com/feed.php?buscar=' + searchstr)
  parser.parse(stream)
  return handler.items



if __name__ == '__main__':
  import difflib
  import sys
  import re
  torrent = sys.argv[1]
  base, episode, rest = re.split("([sS][0-9]{2}[eE][0-9]{2}|[0-9]{1,2}x[0-9]{1,2})",
                                 torrent, maxsplit=1)
  if 'x' in episode:
    episode = "S{:02d}E{:02d}".format(*[int(x) for x in episode.split('x')])

  searchstr = re.sub("\.", "+", base) + episode

  best = None
  m = difflib.SequenceMatcher(lambda x: x in " \t:-,.&%#$!+[]{}=")
  for s in subdivx_downloader(searchstr):
    m.set_seqs(rest, s["desc"])
    ratio = m.ratio()
    if not best or ratio > best["ratio"]:
      best = s
      best["ratio"] = ratio

  if best:
    html = urlopen(best["link"]).read().decode("latin-1")
    l = re.search('"(?P<link>http://www.subdivx.com/bajar.php?[^"]*)"', html)
    if l:
      print(l.group("link"))

# vim: set sw=2 sts=2 : #
