import pandas as pd
import requests 
from bs4 import BeautifulSoup
import  os

class Scraper:
    def __init__(self,location,url,maxItems,outputType,filename):
        self.url = url
        self.maxItems = maxItems
        self.location = location
        self.outputType = outputType
        self.filename = filename
        self.dataFrame = pd.DataFrame(columns=["ID","Name","Price","Image","Image URL"])
        
    def scrape(self,url):  
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


    def savetoSQL(self):
        statements = [] 
        create_statement = pd.io.sql.get_schema(self.dataFrame.reset_index(), self.self.filename)  
        statements.append(create_statement)
        for index, row in self.dataFrame.iterrows():       
            statements.append('INSERT INTO '+self.filename+' ('+ str(', '.join(self.dataFrame.columns))+ ') VALUES '+ str(tuple(row.values)))        
        text = "\n\n".join(statements)
        file = open(self.filename+".sql","w")
        file.write(text)
        file.close()

    def saveToFile(self,ext):
        if ext == "JSON":
            self.dataFrame.to_json(self.filename+".json")
        elif ext == "CSV":
            self.dataFrame.to_csv(self.filename+".csv")
        elif ext == "EXCEL":
            self.dataFrame.to_excel( self.filename+".xlsx", sheet_name=self.filename)
        elif ext == "SQL":
            self.savetoSQL(self.dataFrame,self.filename)

    def save(self):
        types = {1:"JSON",2:"CSV",3:"EXCEL",4:"SQL"}
        self.saveToFile(types[self.outputType])


    def amazonScrapper(self):
        url_pages = [self.url]
        page_number = 1
        product_ID = 1
        if os.path.exists(self.location):
            os.rmdir(self.location)
        os.mkdir(self.location)
        for url in url_pages:
            html_text = self.scrape(url)
            soup = BeautifulSoup(html_text,'html.parser')
            product_name = soup.find_all('div', class_='sg-row')
            pages= soup.find_all('ul', class_='a-pagination')
            while(len(pages) == 0 or len(product_name) == 0):
                html_text = self.scrape(url)
                soup = BeautifulSoup(html_text,'html.parser')
                pages= soup.find_all('ul', class_='a-pagination')
                product_name = soup.find_all('div', class_='sg-row')

            for link in pages:
                all_sub_pages = link.find_all('li',class_ = 'a-normal')
                for page in all_sub_pages:
                    a_tag = page.find('a')
                    if int(a_tag.text) == page_number + 1:
                        url_pages.append("https://www.amazon.in"+a_tag['href'])
                        page_number += 1

            # while(len(product_name) == 0):
            #     html_text = self.scrape(url)
            #     soup = BeautifulSoup(html_text,'html.parser')

            for p_name in product_name:

                images = p_name.find_all('img',class_ ='s-image')
                price = p_name.find_all('span',class_ = 'a-price-whole')
                if(len(images) != 0 and len(price) != 0):
                    product_name_from_web =  images[0]['alt']
                    download_path =  images[0]['src']
                    imagePath = download_path.split('/')[-1].split('?')[0]
                    price_value = price[0].text.replace(".","").replace(",","")

                    row = pd.Series(data=[product_ID,product_name_from_web,price_value,f'{ self.location+"/"+imagePath}',download_path],index=["ID","Name","Price","Image","Image URL"],name=product_ID)
                    self.dataFrame = self.dataFrame.append(row)
                    product_ID += 1
                    file = open( self.location+"/"+imagePath,'wb')
                    file.write(requests.get(download_path).content)
                    file.close()
                    if product_ID > self.maxItems:
                        self.save()
                        return self.dataFrame 