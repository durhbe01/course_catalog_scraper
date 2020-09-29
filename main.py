import csv
import urllib.request
from bs4 import BeautifulSoup

with open('pages.csv') as pageList:
  listReader = csv.reader(pageList, delimiter=',')
  # Temporory counter to stop the program from carrying out many requests
  f = open("output.html", "a")
  count = 0
  for row in listReader:
    above_featured = False
    if row[0] == "URL":
      continue
    if row[2] == 'Until Featured course header':
      above_featured = True
    if count >= 0:
      page = urllib.request.urlopen(row[0])
      print(row[0])
      count += 1
      soup = BeautifulSoup(page.read(), 'html.parser')
      content = soup.find('div', {'id':'content'})
      try:
        columns = content.find_all('div', {'class': 'column'})
        test = columns[1]
      except IndexError:
        print("index")
      if above_featured:
        above_featured = columns[1].find('div', {'class': 'gb-u-spacing-bottom'})
        f.write(str(above_featured))
      else:
        try:
          f.write(str(columns[1]))
        except IndexError:
          print(str(columns))
  f.close()

