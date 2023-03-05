from datetime import datetime
from bs4 import BeautifulSoup
import csv
import time
from fake_useragent import UserAgent
import re
import requests 

def english_months_converter(malay_month):
    if "Januari" in malay_month:
        malay_month = malay_month.replace('Januari', 'January')
    elif 'Februari' in malay_month:
        malay_month = malay_month.replace('Februari', 'February')
    elif 'Mac' in malay_month:
        malay_month = malay_month.replace('Mac', 'March')
    elif 'Mei' in malay_month:
        malay_month = malay_month.replace('Mei', 'May')
    elif 'Jun' in malay_month:
        malay_month = malay_month.replace('Jun', 'June')
    elif 'Julai' in malay_month:
        malay_month = malay_month.replace('Julai', 'July')
    elif 'Ogos' in malay_month:
        malay_month = malay_month.replace('Ogos', 'August')
    elif 'Oktober' in malay_month:
        malay_month = malay_month.replace('Oktober', 'October')
    elif 'Disember' in malay_month:
        malay_month = malay_month.replace('Disember', 'December')    
    return malay_month

date_pattern = r"(\d{1,2} [a-zA-Z]+ \d{4})"
time_pattern = r"(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<meridiem>am|pm)"

# Jan 2020 - Dec 2022 is in total 86 pages 

pages_to_get = 1

# Writing to a file 
with open('sinarharian.csv', 'w', newline='') as f:
  writer = csv.writer(f)
  headers = ["Title", "Date", "Time", "Link", "Description"]
  writer.writerow(headers)

  # automatic goes to the next page from 1... n; python exclusive end 

  for page in range(1,pages_to_get+1):
    print('Processing Page: ', page)
    url = 'https://www.sinarharian.com.my/carian?query=vaksin&pgno='+str(page)

    try:
      # response is equivalent to enter a key in chrome 
      # prevent ip-block by adding fake devices accessing web pages 
      response = requests.get(url, headers={'User-Agent': UserAgent().random})

      # this link give valid status code: 200 --> web scrap pass 
      # print(page.status_code)

    except Exception as e:
      error_type, error_obj, error_info = sys.exc_info()
      print('Error Link: ', url)
      print(error_type, 'Line: ', error_info.tb_lineno)

      # ignore this paage and move on to next one
      continue 

    # delay by 2 seconds to prevent ip block
    time.sleep(2)

    soup = BeautifulSoup(response.text, 'html.parser')
    # inspect element attribute type and its names to take their information

    attrs_code = 'col-md-8 col-content'
    links = soup.find_all('div', attrs={'class':attrs_code})
    # print(len(links))

    # Check each page has 10 links
    print(f'Page {page} has {len(links)} links')


    # need to get the first 6 articles, as the other 4 are the 'popular section'
    for link in links:
      
      # Within div tag, find article-title tag, get its title text

      # Ex: Anwar dedah perolehan vaksin tanpa persetujuan Peguam Negara
      article_title = link.find('div', attrs='article-title').text

      # Ex: 11 Januari 2021 07:38pm
      time_date_properties = link.find('div', attrs='timespan').text

      # converted: 12 January 2021 01:15pm
      date_converted = english_months_converter(time_date_properties)

      date_match = re.search(date_pattern, date_converted)
      time_match = re.search(time_pattern, date_converted)


      if date_match and time_match:
            date_extract = date_match.group(1)
            time_extract = time_match.group()

      # Ex: 2021-01-12
      dateobj = datetime.strptime(date_extract,'%d %B %Y').date()
      
     # 2:11 pm --> 14:11:00
      timeobj = datetime.strptime(time_extract, '%I:%M%p').time()

      # Extract value of href attribute from 'a' tag using dictionary-style access
      web_address = link.find('div', attrs='article-desc').find('a')['href']


      short_description = link.find('div', attrs='article-desc').text

      # write each as a row in csv file
      writer.writerow([article_title, dateobj, timeobj, web_address, short_description])

    print('CSV file saved successfully for Page: ' + str(page))




