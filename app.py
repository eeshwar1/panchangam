from flask import Flask
from flask_classful import FlaskView, route
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)
    
class PanchangamView(FlaskView):

    URL = "https://www.drikpanchang.com/tamil/tamil-month-panchangam.html?geoname-id=4684888&date="
    dataItems = ["Sunrise","Sunset","Nakshathram","Tithi",
                 "Rahu Kalam","Gulikai Kalam","Yamaganda"]
    
    def index(self):
        
        return self.dailysheet()
    
    
    
    @route("json")
    def dailysheet(self):
        self.date = date.today()
        
        response_data = self.fetch_data()
        
        response = app.response_class(
            response=json.dumps(response_data),
            status=200,
            mimetype='application/json'
        )
        
        return response
    
    @route("<strdate>")
    @route("<strdate>/json")
    def dailysheet_for_date(self, strdate):
        
        self.date = datetime.strptime(strdate, "%m-%d-%Y").date()
        response_data = self.fetch_data()
        
        response = app.response_class(
            response=json.dumps(response_data),
            status=200,
            mimetype='application/json'
        )
        
        return response
        
    def fetch_data(self):
        
        return self.fetch_data_for_date(self.date)
        
    def fetch_data_for_date(self, date):
        
        self.date = date
        dateValue = date.strftime("%d/%m/%Y")
        
        response = {}
        
        URL_string = self.URL + dateValue

        page = requests.get(URL_string)

        self.soup = BeautifulSoup(page.content, "html.parser")
        
        textCurrentDate = self.date.strftime("%a %b %d, %Y")
        
        response["current_date"] = textCurrentDate
        
        divTamilDate = self.soup.find("div", {"class": "dpPHeaderLeftTitle"})

        response["current_date_tamil"]= divTamilDate.text
        
        detailDivs = divTamilDate.find_next_siblings("div")

        textTamilDateDetails = ""

        for div in detailDivs:
            textTamilDateDetails += div.text + " "
            
        response["tamil_date_details"] = textTamilDateDetails
        
        self.dataValues = []
        
        for item in self.dataItems:
            item_data = self.find_data(item)
            self.dataValues.append(item_data)
            
            response[item] = item_data
            
        return response
                    
    def find_data(self, str_type):

        return_text = ""
        results = self.soup.find(text=str_type).parent
        
        if results.name != "span":
            results = results.parent

        spans = results.find_next_siblings("span")

        for span in spans:
            return_text += span.text
            
        return return_text
   

PanchangamView.register(app)
    
if __name__ == "__main__":
    
    app.run(host="127.0.0.1",port=8000)
