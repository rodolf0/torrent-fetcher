#!/usr/bin/env python

# http://oreilly.com/catalog/pythonxml/chapter/ch01.html

# Using DOM
import urllib
import xml.dom.minidom
 
def eztv_miner():
  try:
    stream = urllib.urlopen('http://www.ezrss.it/feed/')
  except IOError:
    raise StopIteration
  doc = xml.dom.minidom.parse(stream)

  for item in doc.getElementsByTagName("item"):
    title, link, show = "", "", ""

    # get the item Title (of the episode)
    for title_node in item.getElementsByTagName("title"):
      for elem_node in title_node.childNodes:
        if elem_node.nodeType == xml.dom.minidom.Node.CDATA_SECTION_NODE:
          title = elem_node.data
      if title: break

    # get the Show name
    for title_node in item.getElementsByTagName("description"):
      for elem_node in title_node.childNodes:
        if elem_node.nodeType == xml.dom.minidom.Node.CDATA_SECTION_NODE:
          show = filter(lambda el: el.startswith("Show Name:"),
                        elem_node.data.split(";")).pop()
          show = show.replace("Show Name: ", "")
      if show: break

    # get the item link
    for link_node in item.getElementsByTagName("link"):
      for elem_node in link_node.childNodes:
        if elem_node.nodeType == xml.dom.minidom.Node.TEXT_NODE:
          link = elem_node.data
      if link: break

    yield { "title": title, "show-name": show, "link": link }



# Using SAX
import xml.sax

class ArgenteamMiner(xml.sax.handler.ContentHandler):
  def __init__(self):
    # Just some flags to determine if we're in that node
    self.state = { "item" : False, "title" : False, "link" : False }
    self.title, self.link = "", ""
    self.mapping = {}

  def startElement(self, name, attrs):
    if name in self.state:
      self.state[name] = True

  def endElement(self, name):
    if name in self.state:
      self.state[name] = False
    if name == "item":
      self.mapping[self.title] = self.link

  def characters(self, data):
    if self.state["item"]:
      if self.state["title"]:
        self.title = data
      elif self.state["link"]:
        self.link = data


def argenteam_miner():
  parser = xml.sax.make_parser()
  handler = ArgenteamMiner()
  parser.setContentHandler(handler)
  try:
    stream = urllib.urlopen('http://www.argenteam.net/rss/tvseries_torrents.xml')
  except IOError:
    raise StopIteration

  parser.parse(stream)

  for title in handler.mapping:
    yield { "title": title, "link": handler.mapping[title] }


###### Entry point ######
if __name__ == '__main__':
  import myConfig
  import re

  for torrent in argenteam_miner():
    if torrent["title"].startswith(myConfig.argenteam_titles):
      print torrent["title"] + '^' + torrent["link"]

  for torrent in eztv_miner():
    for eztitle in myConfig.eztv_titles:
      if re.search(eztitle, torrent["title"]) and not re.search("720", torrent["title"]):
        print torrent["title"] + '^' + torrent["link"]
