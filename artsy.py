# -*- coding: cp1252 -*-

import urllib2
import json
import re

class Work:
  def __init__(self, artist, title, priceString):
    self.artist = artist
    self.title = title
    self.price = self.parsePrice(priceString)

  @staticmethod
  def parsePrice(price):
    if price.startswith("Under "):
      price = price[6:]
    exchange = 1
    if price.startswith('$'):     # US Dollar
      exchange = 1
    elif price.startswith(u'�'):  # Great British pound
      exchange = 1.5487
    elif price.startswith(u'�'):  # Euro
      exchange = 1.2221
    elif price.startswith('Rp'):  # Indonesian Rupiah (?)
      exchange = 0.000106
    elif price.startswith(u'�'):  # Chinese Yuan Renminbi (?)
      exchange = 0.156914
    elif price.startswith("R$"):  # Brazilian Real
      exchange = 0.4907
      
    else: print "Unknown currency: " + price

    prices = re.findall("[0-9]+[^ ]*", price)
    prices = [int(str(p).translate(None, ' ,'))*exchange for p in prices]

    return sum(prices) / len(prices)

page = 264
works = []
done = False
while not done:
  try:
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'km_ai=ghz2or4KHJ9qO5OJlmcER3B7Beg%3D; remember_user_token=BAhbB1sGbzoTQlNPTjo6T2JqZWN0SWQGOgpAZGF0YVsRaVRpaWkB2mk3aQH2aUppAYdpAGkHaQBpI2ktSSIZRnhhMjNkZXA2bzJMM2ljaVNGRDkGOgZFVA%3D%3D--d75fc9c38c8fdcbce58c1e4a7c61c827974b7207; kvcd=1342039391641; km_ni=sam.kronick%40gmail.com; km_vs=1; km_lv=1342039392; __utma=1.1619068193.1342039222.1342039222.1342039222.1; __utmb=1.11.9.1342039629018; __utmc=1; __utmz=1.1342039222.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); mp_super_properties=%7B%22all%22%3A%20%7B%22%24initial_referrer%22%3A%20%22http%3A//art.sy/log_in%22%2C%22%24initial_referring_domain%22%3A%20%22art.sy%22%2C%22index%22%3A%202%2C%22name%22%3A%20%22U%22%2C%22value%22%3A%20%22/filter/artworks%22%2C%22scope%22%3A%20%22page%22%2C%22distinct_id%22%3A%20%224f64da32f645870002001e28%22%7D%2C%22events%22%3A%20%7B%7D%2C%22funnels%22%3A%20%7B%7D%7D; km_uq=; _gravity_session=BAh7CEkiGXdhcmRlbi51c2VyLnVzZXIua2V5BjoGRVRbCEkiCVVzZXIGOwBGWwZvOhNCU09OOjpPYmplY3RJZAY6CkBkYXRhWxFpVGlpaQHaaTdpAfZpSmkBh2kAaQdpAGkjaS1JIhlGeGEyM2RlcDZvMkwzaWNpU0ZEOQY7AFRJIg9zZXNzaW9uX2lkBjsARkkiJTQwMTExMGVjZTdjY2JhODUyYzdlZjcyNGZmYTY1YThmBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMXdxVVgzbHM2OFozWXk1djB2UC9CUHlrb2lyL0pCUTFoa1o1MDFtU0JndTA9BjsARg%3D%3D--1d806824d476b8b14d8e51cc70a14f911bc9c2b5'))
    f = opener.open("http://art.sy/api/v1/search/filtered?price_range=-1:1000000000000&sort=-date_added&page=%i" % page)
    j = json.load(f)
  except HTTPError:
    continue
  
  if len(j) <= 0:
    done = True
    break

  newWorks = 0
  for work in j:
    if work["price"] <> "":
      try:
        works.append(Work(work["artist"]["name"], work["title"], work["price"]))
        newWorks += 1
      except TypeError:
        pass

  print "Added %i works from page %i" % (newWorks, page)
  page += 1
  
# Sort by price
works.sort(key=lambda x: x.price, reverse=True)

for work in works:
  print "%s by %s ($%i)" % (work.title, work.artist, work.price)





# Currencies:
# Dollar
# Euro
# Yen
# Pound