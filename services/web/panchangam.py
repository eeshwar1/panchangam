from flask import Flask, render_template, request
from flask_classful import FlaskView, route
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json


app = Flask(__name__)
    
class PanchangamView(FlaskView):

    root_base = "/"
    URL_BASE = "https://www.drikpanchang.com/tamil/tamil-month-panchangam.html?"
    dataItems = ["Sunrise","Sunset","Shaka Samvat","Nakshathram","Tithi",
                 "Rahu Kalam","Gulikai Kalam","Yamaganda",]
    
    locations = [   {"id": "5128581", "name": "New York, United States"},
                    {"id": "4684888", "name": "Dallas, United States"},
                    {"id": "5419384", "name": "Denver, United States"},
                    {"id": "5368361", "name": "Los Angeles, United States"},
                    {"id": "1254163", "name": "Thiruvananthapuram, India"},
                    {"id": "2643743", "name": "London, United Kingdom"} ]
    
    @route("/",methods=['GET','POST'])
    def index(self):
        
        if request.method == "GET":
        
            self.date = date.today()
            self.location = "4684888"
            self.URL=self.URL_BASE + "geoname-id="+ self.location + "&date="
            response_data = self.fetch_data()

        else:
            
            self.location = request.form.get("location")
            self.URL=self.URL_BASE + "geoname-id="+ self.location + "&date="

            strDate = request.form.get('date')
            strPickedDate = request.form.get('picked-date')
            
            dateValue = datetime.strptime(strDate, "%Y-%m-%d").date()
            pickedDateValue = datetime.strptime(strPickedDate, "%Y-%m-%d").date()
            
            if request.form.get('previous') == "Previous":
               #  print("previous")
                self.date = dateValue - timedelta(days=1)
            elif request.form.get('next') == "Next":
              #  print("next")
                self.date = dateValue + timedelta(days=1)
            elif request.form.get('today') == "Today":
               # print("today")
                self.date = date.today()
            elif request.form.get('go') == "Go":
               #  print("go")
                self.date = pickedDateValue
                    
            
            response_data = self.fetch_data()
            
            
        return render_template("index.html", title="Panchangam", data=response_data)
       
    
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
        
        # self.date = date.today()
        
        return self.fetch_data_for_date(self.date)

    def edit_tamil_date_details(self, detail_text):
        idx = detail_text.find("Shaka Samvata")
        
        if idx > 0:
            edited_detail_text = detail_text[:idx - 5] + (detail_text[idx + 13:])
        else:
            edited_detail_text = detail_text

        return edited_detail_text
      
    def fetch_data_for_date(self, date):
        
        self.date = date
        dateValue = date.strftime("%d/%m/%Y")
        
        dateStr = date.strftime("%Y-%m-%d")
        
        response = {}
        
        URL_string = self.URL + dateValue

        page = requests.get(URL_string)

        self.soup = BeautifulSoup(page.content, "html.parser")
        
        response["str_date"] = dateStr
        
        # response["date_text"] = self.date.strftime("%a %b %d, %Y")
        
        response["date_text"] = self.date.strftime("%d %b %Y")
        
        
        prevDate = self.date - timedelta(days = 1)
        nextDate = self.date + timedelta(days = 1)
        
        response["prev_date_text"] = prevDate.strftime("%a %b %d, %Y")
        response["next_date_text"] = nextDate.strftime("%a %b %d, %Y")
        
        
        divTamilDate = self.soup.find("div", {"class": "dpPHeaderLeftTitle"})

        response["date_tamil"]= divTamilDate.text
        
        detailDivs = divTamilDate.find_next_siblings("div")

        textTamilDateDetails = ""

        for div in detailDivs:
            textTamilDateDetails += div.text + " "
            
        response["tamil_date_details"] = self.edit_tamil_date_details(textTamilDateDetails)
        response["geo_location"] = self.location
        response["last_refresh"] = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
        
        response["locations"] = self.locations
        response["num_locations"] = len(self.locations)

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
    
    
    
PanchangamView.register(app, route_base="/")
    
if __name__ == "__main__":
    
    app.run(host="127.0.0.1",port=8000)
