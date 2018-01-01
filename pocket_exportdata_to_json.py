# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import collections as cl
import json

"""
The export data is converted into json file of this structure.

///////////////
{
  title: {
    "title": title,
    "url": url,
    "time_added": add time(timestamp),
    "tags": tags
  }
}
///////////////
"""

with open('ril_export.html', 'r') as f:
    html = f.read();

soup = BeautifulSoup(html, 'lxml')
plist = soup.find_all("li")
d = cl.OrderedDict()
for i in plist:
    d[i.text] = cl.OrderedDict({"title":i.text,
                                "url":i.a["href"],
                                "tags":i.a["tags"],
                                "time_added":i.a["time_added"]})

with open('pocket_data.json', 'w') as w:
    json.dump(d, w)
