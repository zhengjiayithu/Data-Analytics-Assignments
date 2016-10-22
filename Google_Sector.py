# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 16:54:43 2016

@author: Jiayi ZHENG
"""

def google_sector_report():
    import requests
    import json
    from bs4 import BeautifulSoup
    output = dict()    
    # Get data from sector change summary page   
    url = 'https://www.google.com/finance'
    response = requests.get(url)
    # If the data grab was successful    
    if response.status_code == 200:
        output['STATUS'] = 'GOOD'
        result = dict()
        page = BeautifulSoup(response.content, 'lxml')
        # Find the sector summary division
        summary = page.find('div', id='secperf').find('table')
        # Find table row for each sector
        sectors = summary.find_all('tr', recursive=False)
        # Get name, link and change data of each sector
        for sector in sectors[1:]:
            sector_dict = dict()
            gainer = dict()
            loser = dict()
            name_tag = sector.find('a')
            sector_name = name_tag.get_text()
            sector_link = 'https://www.google.com' + name_tag.get('href')
            change = sector.find('span').get_text()
            sector_dict['change']  = float(change.replace('%',''))
            # Get biggest gainer and loser data
            sector_response = requests.get(sector_link)
            if sector_response.status_code == 200:
                detail_page = BeautifulSoup(sector_response.content, 'lxml')
                top_movers = detail_page.find('table', class_='topmovers')
                # check if there are gainers
                if_gainers = top_movers.find(text='Gainers (% price change)')
                # if there are gainers, find the biggest gainer
                if if_gainers is not None:
                    biggest_gainer = if_gainers.find_next('tr')
                    gainer_name = biggest_gainer.find('a').get_text()
                    gainer_change = biggest_gainer.find_all('span')[1].get_text()
                    gainer['equity'] = gainer_name
                    gainer['change'] = float(gainer_change.strip('()').replace('%',''))
                else:
                    gainer['equity'] = ''
                    gainer['change'] = None                   
                # check if there are losers
                if_losers = top_movers.find(text='Losers (% price change)')
                # if there are losers, find the biggest loser
                if if_losers is not None:
                    biggest_loser = if_losers.find_next('tr')
                    loser_name = biggest_loser.find('a').get_text()
                    loser_change = biggest_loser.find_all('span')[1].get_text()
                    loser['equity'] = loser_name
                    loser['change'] = float(loser_change.strip('()').replace('%',''))
                else:
                    loser['equity'] = ''
                    loser['change'] = None                                
            sector_dict['biggest gainer'] = gainer.copy()
            sector_dict['biggest loser'] = loser.copy()
            result[sector_name] = sector_dict.copy()
        output['result'] = result
    # If the data grab failed
    else:
        output['STATUS'] = 'BAD'
    # dict -> json
    json = json.dumps(output, indent=4, separators=(',', ': '))
    return json

print(google_sector_report())
