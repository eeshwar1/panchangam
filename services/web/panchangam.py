
from datetime import date, timedelta, datetime
import time
import requests
from bs4 import BeautifulSoup
import json

__DEBUG = False

__DEFAULT_LOCATION="4684888"

__locations = [ {"id": "5128581", "name": "New York, United States"},
                {"id": "4684888", "name": "Dallas, United States"},
                {"id": "5419384", "name": "Denver, United States"},
                {"id": "5368361", "name": "Los Angeles, United States"},
                {"id": "1254163", "name": "Thiruvananthapuram, India"},
                {"id": "1264527", "name": "Chennai, India"},
                {"id": "2643743", "name": "London, United Kingdom"} ]

def get_details(location=__DEFAULT_LOCATION):
    
    return json.dumps(__fetch_data_from_web(date.today(), location))
        
def get_details_for_date(date, location=__DEFAULT_LOCATION):

    return json.dumps(__fetch_data_from_web(date, location))

def __fetch_data_from_web(date, location):

    dataItems = ["Sunrise","Sunset","Nakshathram","Tithi",
                "Rahu Kalam","Gulikai Kalam","Yamaganda"]

    URL_BASE = "https://www.drikpanchang.com/tamil/tamil-month-panchangam.html?"

    URL = URL_BASE + "geoname-id="+ location + "&date="

    dateValue = date.strftime("%d/%m/%Y")

    dateStr = date.strftime("%Y-%m-%d")

    response = {}

    URL_string = URL + dateValue

    page = get_page_data(URL_string)

    soup = BeautifulSoup(page.content, "html.parser")

    response["str_date"] = dateStr

    response["date_text"] = date.strftime("%a %b %d, %Y")

    prevDate = date - timedelta(days = 1)
    nextDate = date + timedelta(days = 1)

    response["prev_date_text"] = prevDate.strftime("%a %b %d, %Y")
    response["next_date_text"] = nextDate.strftime("%a %b %d, %Y")

    divTamilDate = soup.find("div", {"class": "dpPHeaderLeftTitle"})

    detailDivs = divTamilDate.find_next_siblings("div")

    textTamilDateDetails = ""

    for div in detailDivs:
        textTamilDateDetails += div.text + " "
        
    (response["tamil_date_details"], yugam) = __edit_tamil_date_details(textTamilDateDetails)
    response["last_refresh"] = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

    response["geo_location"] = location

    response["locations"] = __locations

    for item in dataItems:
        item_data = __find_data_web(soup, item)
        
        response[item] = item_data
    
    shaka_samvat = __find_data_web(soup, "Shaka Samvat")
    response["date_tamil"]= divTamilDate.text + ", " + shaka_samvat + ", " + yugam

    response["gowri_details"] = __fetch_gowri_details_for_date(date, location)["data"]

    return response
        
def __find_data_web(soup, str_type):

    return_text = ""
    results = soup.find(string=str_type).parent

    if results.name != "span":
        results = results.parent

    spans = results.find_next_siblings("span")

    for span in spans:
        return_text += span.text
        
    return return_text

def __edit_tamil_date_details(detail_text):

    idx = detail_text.find("Shaka Samvata")
    
    pos_last_comma = detail_text.rindex(",")
    yugam = detail_text[pos_last_comma + 2:].strip()

    if idx > 0:
        edited_detail_text = detail_text[:idx - 5] + (detail_text[idx + 13:pos_last_comma - 1])
    else:
        edited_detail_text = detail_text

    return (edited_detail_text.strip(), yugam)

def get_page_data(URL_string):

    try: 
        page = requests.get(URL_string)
    except requests.exceptions.Timeout:
        time.sleep(1)
        page = requests.get(URL_string)

    return page

def get_gowri_details(location=__DEFAULT_LOCATION):
    
    return json.dumps(__fetch_gowri_details_for_date(date.today(), location))

def get_gowri_details_for_date(date, location=__DEFAULT_LOCATION):
    
    return json.dumps(__fetch_gowri_details_for_date(date, location))

def __fetch_gowri_details_for_date(date, location):

    URL_BASE = "https://www.drikpanchang.com/tamil/tamil-gowri-panchangam.html?"

    URL = URL_BASE + "geoname-id="+ location + "&date="

    dateValue = date.strftime("%d/%m/%Y")

    response = {}

    URL_string = URL + dateValue

    page = get_page_data(URL_string)

    soup = BeautifulSoup(page.content, "html.parser")

    divMuhurthaCards = soup.find_all("div", {"class": "dpMuhurtaCard"})

    muhurthamData = []

    for muhurthamCard in divMuhurthaCards:
        muhurthamData.append(__get_muhurtham_data(muhurthamCard))

    response["data"] = muhurthamData
    
    return response


def __get_muhurtham_data(muhurthamCard):
 
    muhurthamDataItem = {}

    muhurthamNameSpan = muhurthamCard.findChild("span")
    
    muhurthamDataItem["type"]  = muhurthamNameSpan.text
    
    muhurthamTimeSpan = muhurthamNameSpan.find_parent("div").next_sibling.findChild("span")
    
    muhurthamDataItem["time"] = muhurthamTimeSpan.text

    divMuhurthaRows = muhurthamCard.findChildren("div", { "class": "dpMuhurtaRow" })

    muhurthamList = []
    muhurthamItem = {}

    for divMuhurthaRow in divMuhurthaRows:
        divMuhurthaName = divMuhurthaRow.findChild("div", { "class": "dpMuhurtaName" })
        divMuhurthaTime = divMuhurthaRow.findChild("div", { "class": "dpMuhurtaTime" })

        muhurthamItem = {}
        muhurthamItem["name"] = divMuhurthaName.findChild("span").text
        muhurthaTimeSpansRoot = divMuhurthaTime.findChild("span")
        muhurthaTimeSpans = muhurthaTimeSpansRoot.findChildren("<span>", recursive=False)

        muhurthamName = muhurthamItem["name"]


        if muhurthamName.endswith("Good") or \
        muhurthamName.endswith("Best") or \
        muhurthamName.endswith("Gain") or \
        muhurthamName.endswith("Wealth"):
            muhurthamItem["tag"] = "good"
        else:
            muhurthamItem["tag"] = "bad"

        muhurthaTime = muhurthaTimeSpansRoot.text

        for muhurthaTimeSpan in muhurthaTimeSpans:
            print(muhurthaTimeSpan)
            muhurthaTime += muhurthaTimeSpan.text

        muhurthamItem["time"] = (muhurthaTime)

        muhurthamList.append(muhurthamItem)
    
    muhurthamDataItem["muhurtham_list"]  = muhurthamList
    return muhurthamDataItem

if __name__ == "__main__":
  data = get_details()
  print(data)
