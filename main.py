import csv
import urllib.request
from bs4 import BeautifulSoup

with open('pages.csv') as pageList:
  listReader = csv.reader(pageList, delimiter=',')
  # Temporory counter to stop the program from carrying out many requests
  f = open("output.html", "a")
  count = 0
  for row in listReader:
    if row[0] == "URL":
      continue
    if count < 1:
      page = urllib.request.urlopen(row[0])
      print(row[0])
      count += 1
      soup = BeautifulSoup(page.read(), 'html.parser')
      content = soup.find('div', {'id': 'content'})
      columns = content.findChildren('div', {'class': 'column'})
      f.write(str(columns))
      print(columns[1])
    f.close()

