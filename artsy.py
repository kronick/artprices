# -*- coding: cp1252 -*-

import urllib2
import json
import re
import os
import codecs

pwd = os.path.dirname(os.path.realpath(__file__))

COOKIES = 'km_ai=ghz2or4KHJ9qO5OJlmcER3B7Beg%3D; remember_user_token=BAhbB1sGbzoTQlNPTjo6T2JqZWN0SWQGOgpAZGF0YVsRaVRpaWkB2mk3aQH2aUppAYdpAGkHaQBpI2ktSSIZRnhhMjNkZXA2bzJMM2ljaVNGRDkGOgZFVA%3D%3D--d75fc9c38c8fdcbce58c1e4a7c61c827974b7207; kvcd=1342039391641; km_ni=sam.kronick%40gmail.com; km_vs=1; km_lv=1342039392; __utma=1.1619068193.1342039222.1342039222.1342039222.1; __utmb=1.11.9.1342039629018; __utmc=1; __utmz=1.1342039222.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); mp_super_properties=%7B%22all%22%3A%20%7B%22%24initial_referrer%22%3A%20%22http%3A//art.sy/log_in%22%2C%22%24initial_referring_domain%22%3A%20%22art.sy%22%2C%22index%22%3A%202%2C%22name%22%3A%20%22U%22%2C%22value%22%3A%20%22/filter/artworks%22%2C%22scope%22%3A%20%22page%22%2C%22distinct_id%22%3A%20%224f64da32f645870002001e28%22%7D%2C%22events%22%3A%20%7B%7D%2C%22funnels%22%3A%20%7B%7D%7D; km_uq=; _gravity_session=BAh7CEkiGXdhcmRlbi51c2VyLnVzZXIua2V5BjoGRVRbCEkiCVVzZXIGOwBGWwZvOhNCU09OOjpPYmplY3RJZAY6CkBkYXRhWxFpVGlpaQHaaTdpAfZpSmkBh2kAaQdpAGkjaS1JIhlGeGEyM2RlcDZvMkwzaWNpU0ZEOQY7AFRJIg9zZXNzaW9uX2lkBjsARkkiJTQwMTExMGVjZTdjY2JhODUyYzdlZjcyNGZmYTY1YThmBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMXdxVVgzbHM2OFozWXk1djB2UC9CUHlrb2lyL0pCUTFoa1o1MDFtU0JndTA9BjsARg%3D%3D--1d806824d476b8b14d8e51cc70a14f911bc9c2b5'

class Work:
  def __init__(self, id, artist, title, priceString, image):
    self.id = id
    self.artist = artist
    self.title = title
    self.price = self.parsePrice(priceString)

    self.downloadImage(image, "large")
    self.downloadImage(image, "medium")
    self.downloadImage(image, "square")
    self.downloadImage(image, "small")
    self.downloadImage(image, "larger")
    #self.downloadImage(image, "normalized")

    self.image = self.relativeImagePath("medium")

  def localImagePath(self, version="large"):
    return pwd + "/images/%s-%s.jpg" % (self.id, version)
  def relativeImagePath(self, version="large"):
    return "images/%s-%s.jpg" % (self.id, version)

  def downloadImage(self, image, version="large"):
    try:
      with open(self.localImagePath(version)) as f: pass
    except IOError as e:
      image = image.replace(":version", version)
      print "Downloading %s version of %s:" % (version, image)
      f = authenticatedRequest(image)
      out = open(self.localImagePath(version), 'wb')
      out.write(f.read())
      out.close()

    return self.relativeImagePath()

  @staticmethod
  def parsePrice(price):
    if price.startswith("Under "):
      price = price[6:]
    exchange = 1
    if price.startswith('$'):     # US Dollar
      exchange = 1
    elif price.startswith(u'£'):  # Great British pound
      exchange = 1.5487
    elif price.startswith(u'€'):  # Euro
      exchange = 1.2221
    elif price.startswith('Rp'):  # Indonesian Rupiah (?)
      exchange = 0.000106
    elif price.startswith(u'¥'):  # Chinese Yuan Renminbi (?)
      exchange = 0.156914
    elif price.startswith("R$"):  # Brazilian Real
      exchange = 0.4907
      
    else: print "Unknown currency: " + price

    prices = re.findall("[0-9]+[^ ]*", price)
    prices = [int(str(p).translate(None, ' ,'))*exchange for p in prices]

    return sum(prices) / len(prices)

def authenticatedRequest(url):
  opener = urllib2.build_opener()
  opener.addheaders.append(('Cookie', COOKIES))
  return opener.open(url)

page = 1
works = []
done = False
while not done:
  try:
    try:
      f = open(pwd + "/cached/%i.json" % page, 'r')
      contents = f.read()
      print "Reading page %i from cache" % page
    except IOError:
      print "Downloading page %i from web" % page
      f = authenticatedRequest("http://art.sy/api/v1/search/filtered?price_range=-1:1000000000000&sort=-date_added&page=%i" % page)
      contents = f.read()
      cache = open(pwd + "/cached/%i.json" % page, 'w')
      cache.write(contents)
      cache.close()
    j = json.loads(contents)
    f.close()
  except urllib2.HTTPError as e:
    print e
    continue
  except ValueError as e:
    print "Problem with the json: %s" % e
    print f.read()
  
  if len(j) <= 0:
    done = True
    break

  newWorks = 0
  for work in j:
    if work["price"] <> "":
      try:
        works.append(Work(work["id"],
                          work["artist"]["name"],
                          work["title"],
                          work["price"],
                          work["images"][0]["image_url"]))
        newWorks += 1
      except TypeError:
        pass

  print "Added %i works from page %i" % (newWorks, page)
  page += 1
  
# Sort by price
works.sort(key=lambda x: x.price, reverse=True)

html = codecs.open(pwd + "/index.html", encoding="utf-8", mode="w")

html.write("""<html>
  <head>
  <style>
  .work {
    margin-bottom: 2em;
    font-weight: bold;
  }
  </style>
  <body>
    <div align='center'>
          """)

for work in works:
  html.write("<div class='work'><img src='%s'><br />$%i</div>\n\n" % (work.image, work.price))
  print "%s by %s ($%i)" % (work.title, work.artist, work.price)

html.write("</div></body></html>")




# Currencies:
# Dollar
# Euro
# Yen
# Pound
