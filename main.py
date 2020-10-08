import csv
import urllib.request
import urllib.parse
import re
from datetime import date
from bs4 import BeautifulSoup

gbc_link = "https://www.gettysburg.edu"

def gen_dept(name, link):
    result = f'<li>{name}'
    result += '<ul>'
    result += '<li>'
    result += gen_link('Program Description', link)
    result += '</li>'
    result += '<li>'
    result += gen_link('Program Requirements', f'{link}/major-minor')
    result += '</li>'
    result += '<li>'
    result += gen_link('Courses', f'{link}/courses')
    result += '</li>'
    result += '</ul></li>'
    return result

def gen_link(text, link):
    query = ""
    if "?id=" in link:
      query = link.split('?')[1][3:]
      link = link.split('?')[0]
    return f'<a href="{local_link_from_relative(link, query=query)}">{text}</a>'

def local_link_from_relative(link, query=""):
    # Remove Leading "/"
    link = link[1:]

    # Remove trailing "/" if present
    if link[-1] == "/":
        link = link[:-1]

    # Replace forward slashes with hyphens and prepend hash sign
    if query != "":
      link = f'#{link.replace("/", "-")}-{translate_url_query(query)}'
    else:
      link = f'#{link.replace("/", "-")}'
    return link

def translate_url_query(query):
  if query != "":
    return query.replace('&', '-').replace('+', '-')
  return ""

def generate_toc(year1, year2):
    result = ""

    # Top Headings (Title, Date, Link to GBC Website)
    heading = f'<h1>{year1}-{year2} Course Catalog</h1>'
    college_link = f'<p><a href="{gbc_link}">Gettysburg College</a></p>'
    mdy_date = date.today().strftime("%m/%d/%Y")
    catalog_link = f'<p><a href="{gbc_link}/academic-programs/curriculum/catalog">Catalog</a> generated on {mdy_date}</p>'
    result += heading + college_link + catalog_link

    result += '<h2 id="toc">Contents</h2>'

    # Context manager for table of contents csv
    with open("toc.csv") as toc_csv:
        toc_reader = csv.reader(toc_csv, delimiter=',')
        past_first_row = False
        for row in toc_reader:
            # Check for content in columns
            level2_header_present = row[0] != ""
            level3_header_present = row[1] != ""
            is_dept_row = row[4]

            # Skip first row
            if row[0] == "Level 2 Heading":
                result += "<ol>"
                continue

            # Carry out department specific behavior (Program + Course subheadings)

            if level2_header_present:
                if past_first_row:
                  result += "</ol></li>"
                result += "<li>"
                result += gen_link(f'{row[0]}', row[5])
                result += "<ol>"
                past_first_row = True
            if is_dept_row:
                result += gen_dept(row[1], row[5])
                continue
            if level3_header_present:
                result += gen_link(f'<li>{row[1]}</li>', row[5])
    return result

def gen_content():
    result = ""

    with open('pages.csv') as page_list:
        pages_reader = csv.reader(page_list, delimiter=',')

        # Uncomment to test
        #rows_to_test = 60

        for row in pages_reader:
            # Flags to set for each page
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
                result += f'<h2>{title}</h2>'

            # Fetch the page
            page = urllib.request.urlopen(row[0])
            print(f'Fetching page: {row[0]}')
            soup = BeautifulSoup(page.read(), 'html.parser')

            # Extract the path from the url
            url_path = urllib.parse.urlparse(row[0]).path
            id_prefix = url_path[1:].replace('/', '-')
            page_id = id_prefix
            page_query = urllib.parse.urlparse(row[0]).query

            content = soup.find('div', {'id': 'content'})

            # Find + correct links
            all_links = content.find_all('a')
            for link in all_links:
                if link.has_attr('href'):
                    # Change relative links to id-based links
                    if link['href'][0] == "/":
                        link_url = urllib.parse.urlparse(link['href'])
                        link_url_path = link_url.path
                        link_url_query = link_url.query
                        link['href'] = local_link_from_relative(link_url_path, link_url_query)
                    # Change existing skip links to new links with prefix based
                    # what page they are from
                    elif link['href'][0] == "#":
                        old_id = link['href'][1:]
                        new_id = f"#{page_id}{old_id}"
                        link['href'] = new_id

            # Find all elements with ids
            all_elems_with_ids = content.find_all(id=re.compile(".+"))
            for elem in all_elems_with_ids:
                elem["id"] = id_prefix + elem["id"]

            # Remove svgs
            for svg_item in content.find_all('svg'):
                svg_item.decompose()

            page_content = None
            try:
                columns = content.find_all('div', {'class': 'column'})
                page_content = columns[1]
            # BUG: When index error is catched, there are type errors in the exception code.
            # Handle the case when the content element is a main instead of a div
            except IndexError:
                # Handle the case when the columns are not all divs
                page_content = content.find('main', {'class', 'column'})


            # Add an id to the content to allow skip linking to it
            if page_query != "":
              page_content['id'] = page_id + '-' + translate_url_query(page_query)[3:]
              print(page_content['id'])
            else:
              page_content['id'] = page_id[:-1]
            result += str(page_content)

            # This is the old way that I used to grab the content above the
            # "Featured Courses" header
            """
            if above_featured:

                above_featured = columns[1].find(
                    'div', {'class': 'gb-u-spacing-bottom'})
                result += str(above_featured)
            else:
                result += str(columns[1])
                """

            # Uncomment to test with the first rows_to_test rows in the csv file
            #rows_to_test -= 1
            #if rows_to_test < 0:
            #   break
    return result


with open("output.html", "a") as output:
    output.write(generate_toc(2019, 2020))
    output.write(gen_content())