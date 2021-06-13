#!/usr/bin/env python
# coding: utf-8

# # Amazon Web Scrapper

# ### Three things you  will need:
# - Name of directory in which you want to store all the images of products
# - The URL of product's main page
# - the total number of products you want.

# ## Types of Output
# 1. JSON
# 2. CSV
# 3. EXCEL
# 4. SQL

# In[1]:


import pandas as pd
import requests 
from bs4 import BeautifulSoup
import  os
import curses


# In[2]:


def scrape(url):  
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
    r = requests.get(url, headers=headers)
    if r.status_code > 500:
        return None
    return r.text


# In[3]:


def savetoSQL(data,filename):
    table_name = input("Enter The Name of Table:")
    statements = [] 
    create_statement = pd.io.sql.get_schema(data.reset_index(), table_name)  
    statements.append(create_statement)
    for index, row in data.iterrows():       
        statements.append('INSERT INTO '+table_name+' ('+ str(', '.join(data.columns))+ ') VALUES '+ str(tuple(row.values)))        
    text = "\n\n".join(statements)
    file = open(filename+".sql","w")
    file.write(text)
    file.close()


# In[4]:


def saveToFile(data,ext,filename):
    if ext == "JSON":
        data.to_json(filename+".json")
    elif ext == "CSV":
        data.to_csv(filename+".csv")
    elif ext == "EXCEL":
        data.to_excel( filename+".xlsx", sheet_name=root)
    elif ext == "SQL":
        savetoSQL(data,filename)


# In[5]:


def save(data):
    types = {1:"JSON",2:"CSV",3:"EXCEL",4:"SQL"}
    print('''Choose Type to Store Data:
    1.JSON
    2.CSV
    3.EXCEL
    4.SQL''')
    choice = 0
    while not (choice >0 and choice <5):
        try:
            choice = int(input(">>>"))
        except:
            print("Enter The Valid Input!")
    filename = input("Enter The Name of File(without extension) :")
    saveToFile(data,types[choice],filename)


# In[6]:


def amazonScrapper():
    # reprinting the screen
    stdscr = curses.initscr()

    root = input("Entet The Folder in which you want to save all the product images :")
    first =input('Enter The URL:')
    max_items = int(input('Enter Max Items:'))

    url_pages = [first]

    page_number = 1
    os.mkdir(root)

    product_ID = 1
    index = 0

    data = pd.DataFrame(columns=["ID","Name","Price","Image","Image URL"])
    print("Fetching Products....")

    for url in url_pages:
        html_text = scrape(url)
        soup = BeautifulSoup(html_text,'html.parser')
        product_name = soup.find_all('div', class_='sg-row')

        pages= soup.find_all('ul', class_='a-pagination')

        while(len(pages) == 0):
            html_text = scrape(url)
            soup = BeautifulSoup(html_text,'html.parser')
            pages= soup.find_all('ul', class_='a-pagination')

        for link in pages:
            all_sub_pages = link.find_all('li',class_ = 'a-normal')
            for page in all_sub_pages:
                a_tag = page.find('a')
                if int(a_tag.text) == page_number + 1:
                    url_pages.append("https://www.amazon.in"+a_tag['href'])
                    page_number += 1

        while(len(product_name) == 0):
            html_text = scrape(url)
            soup = BeautifulSoup(html_text,'html.parser')
            product_name = soup.find_all('div', class_='sg-row')

        for p_name in product_name:
            images = p_name.find_all('img',class_ ='s-image')
            price = p_name.find_all('span',class_ = 'a-price-whole')
            if(len(images) != 0 and len(price) != 0):
                product_name_from_web =  images[0]['alt']
                download_path =  images[0]['src']
                imagePath = download_path.split('/')[-1].split('?')[0]
                price_value = price[0].text.replace(".","")
                stdscr.addstr(0, 0, "Fetching Products...." + str(product_ID))
                stdscr.refresh()

                row = pd.Series(data=[product_ID,product_name_from_web,price_value,f'{ root+"/"+imagePath}',download_path],index=["ID","Name","Price","Image","Image URL"],name=product_ID)
                data = data.append(row)
                product_ID += 1

                file = open( root+"/"+imagePath,'wb')
                file.write(requests.get(download_path).content)
                file.close()
                if product_ID > max_items:
                    save(data)
                    return


# In[7]:

amazonScrapper()

