# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 10:14:37 2016

@author: Jiayi ZHENG
"""

# Get the url which includes country information.
def get_address(address_string, country='ALL'):
    address = '_'.join(address_string.split(' '))
    if country != 'ALL':
        country = '_'.join(country.split(' '))
        address = address + ',_' + country
    return address

# JSON
def get_geolocation_json(address_string,country='ALL',types=False):
    address = get_address(address_string, country)
#==============================================================================
#     for result in data['results']:
#         if not country == 'ALL':
#             if not country in [x['long_name'] for x in result['address_components'] if 'country' in x['types']]:
#                 continue
#==============================================================================
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s' % (address)
    import requests
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if types==False:
            x_list = [(x['formatted_address'],x['geometry']['location']['lat'],x['geometry']['location']['lng']) for x in json_data['results']]
        else:
            x_list = [(x['formatted_address'],x['geometry']['location']['lat'],x['geometry']['location']['lng'], x['types']) for x in json_data['results']]
        return x_list            
    else:
        print ('Error!!!')
        return None

# XML
def get_geolocation_xml(address_string,country='ALL',types=False):
    address = get_address(address_string, country)
#==============================================================================
# ### Should use type to check the country argument.
#     for child in root.findall('result'):
#         #[x.find('long_name').text for x in root.findall('address_component') if x.find('type').text == 'country']
#         clist = [x.find('long_name').text for x in child.findall('address_component') if x.find('type').text == 'country']
#         if not country == "ALL" and not country in clist: continue
#==============================================================================
    url = 'https://maps.googleapis.com/maps/api/geocode/xml?address=%s' % (address)
    import requests
    from lxml import etree
    response = requests.get(url)
    if response.status_code == 200:
        data = response.content
        root = etree.XML(data)
        if types==False:
            x_list = [(element.find('formatted_address').text, element.find('geometry/location/lat').text,  element.find('geometry/location/lng').text) for element in root.findall('result')]
        else:
            x_list = [(element.find('formatted_address').text, element.find('geometry/location/lat').text,  element.find('geometry/location/lng').text, [(e.text) for e in element.findall('type')]) for element in root.findall('result')]
        return x_list            
    else:
        print ('Error!!!')
        return None

def get_geolocation_data(address_string,format='JSON',country='ALL',types=False):
    if format=='JSON':
        return get_geolocation_json(address_string, country, types)
    elif format=='XML':
        return get_geolocation_xml(address_string, country, types)
    else:
        print ('Error!!!')
        return None   
        
#==============================================================================
# def get_xml_data(response,country,types):
#     from lxml import etree
#     root = etree.XML(response.content)
#     result_list = list()
#     for child in root.findall('result'):
#         #[x.find('long_name').text for x in root.findall('address_component') if x.find('type').text == 'country']
#         clist = [x.find('long_name').text for x in child.findall('address_component') if x.find('type').text == 'country']
#         if not country == "ALL" and not country in clist: continue
#         address = child.find('formatted_address').text
#         lat = child.find('geometry/location/lat').text
#         lng = child.find('geometry/location/lng').text
#         if types:
#             type_list = list()
#             for element in child.findall('type'):
#                 type_list.append(element.text)
#             result_list.append((address,lat,lng,type_list))
#         else:
#             result_list.append((address,lat,lng))
#     return result_list
# 
# def get_json_data(response,country,types):
#     data = response.json()
#     result_list = list()
#     for result in data['results']:
#         if not country == 'ALL':
#             if not country in [x['long_name'] for x in result['address_components'] if 'country' in x['types']]:
#                 continue
#         address = result['formatted_address']
#         lat = result['geometry']['location']['lat']
#         lng = result['geometry']['location']['lng']
#         if types:
#             result_list.append((address,lat,lng,result['types']))
#         else:
#             result_list.append((address,lat,lng))
#     return result_list
#             
#     
# def get_geolocation_data(address_string,format="JSON",country="ALL",types=False):
#     format = format.lower()
#     address = '_'.join(address_string.split())
#     url = 'https://maps.googleapis.com/maps/api/geocode/%s?address=%s' %(format,address)
#     try:
#         import requests
#         response=requests.get(url)
#         if not response.status_code == 200: return None
#         func='get_'+format+'_data'
#         return globals()[func](response,country,types)
#     except:
#         return None
#==============================================================================

"""
globals()[func]
"""
