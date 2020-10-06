# Course Catalog Web Scraper

This script grabs all of the relevant content for the course catalog from the gettysburg.edu
website and compiles into a single HTML file. It extracts all of the urls from a csv of the with
the given format.

Additionally, it uses another csv to generate the table of contents. To add a new page to the table
of contents, add a new row in this csv, filling in the corresponding columns for what level of
header it is.

When grabbing the content from each page, this script assigns the section a new id created from its
url path for the sake of linking to it throughout the document. Additionally, all non-external
links re-created to link to the aforementioned id.

Pages are added to the final HTML file in the order they are listed in the csv.
