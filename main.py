import csv
import urllib.request
import urllib.parse
import re
from bs4 import BeautifulSoup

with open('pages.csv') as pageList:
  listReader = csv.reader(pageList, delimiter=',')
  f = open("output.html", "a")
  for row in listReader:
    # Flags to set for each page
    above_featured = False
    title = None

    # Ignore header row
    if row[0] == "URL":
      continue

    # Check to see if page has "featured course" header or "title"
    if row[2] == 'Until Featured course header':
      above_featured = True
    elif row[1] != '':
      title = row[1]

    # Insert title header if provided
    if title != None:
      f.write(f'<h2>{title}</h2>')

    # Fetch the page
    page = urllib.request.urlopen(row[0])
    print(row[0])
    soup = BeautifulSoup(page.read(), 'html.parser')

    # Extract the path from the url
    url_path = urllib.parse.urlparse(row[0]).path
    id_prefix = url_path[1:].replace('/', '-')
    page_id = id_prefix
    print("URL PATH")
    print(id_prefix)

    content = soup.find('div', {'id':'content'})

    # Find + correct links
    all_links = content.find_all('a')
    for link in all_links:
      if link.has_key('href'):
        if link['href'][0] == "/":
          link_url_path = urllib.parse.urlparse(link['href']).path
          if link_url_path[-1] == '/':
            link_url_path = link_url_path[:-1]
          id_content = link_url_path[1:].replace('/', '-')
          final_id = f"#{id_content}"
          link['href'] = final_id
          print(link['href'])
        elif link['href'][0] == "#":
          old_id = link['href'][1:]
          new_id = f"#{page_id}{old_id}"
          link['href'] = new_id

    # Find all elements with ids
    all_elems_with_ids = content.find_all(id=re.compile(".+"))
    for elem in all_elems_with_ids:
      elem["id"] = id_prefix + elem["id"]
      print(elem["id"])

    try:
      columns = content.find_all('div', {'class': 'column'})
      test = columns[1]
    except IndexError:
      # Handle the case when the columns are not all divs
      print("index")
      column = content.find('main', {'class', 'column'})
      column['id'] = page_id
      f.write(str(column))
      continue
    if above_featured:
      
      above_featured = columns[1].find('div', {'class': 'gb-u-spacing-bottom'})
      f.write(str(above_featured))
    else:
      #try:
      f.write(str(columns[1]))
      #except IndexError:
      #  print(str(columns))
  f.close()