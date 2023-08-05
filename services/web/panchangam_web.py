from flask import Flask, render_template, request
from flask_classful import FlaskView, route
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json

import panchangam

app = Flask(__name__)
    
class PanchangamView(FlaskView):

    root_base = "/"
    
    @route("/",methods=['GET','POST'])
    def index(self):
        
        if request.method == "GET":
        
            self.date = date.today()
            self.location = "4684888"
            response_data = json.loads(panchangam.get_details_for_date(self.date, self.location))

        else:
            
            self.location = request.form.get("location")

            strDate = request.form.get('date')
            strPickedDate = request.form.get('picked-date')
            
            dateValue = datetime.strptime(strDate, "%Y-%m-%d").date()
            pickedDateValue = datetime.strptime(strPickedDate, "%Y-%m-%d").date()
            
            if request.form.get('previous') == "Previous":
                self.date = dateValue - timedelta(days=1)
            elif request.form.get('next') == "Next":
                self.date = dateValue + timedelta(days=1)
            elif request.form.get('today') == "Today":
                self.date = date.today()
            elif request.form.get('go') == "Go":
                self.date = pickedDateValue

            response_data = json.loads(panchangam.get_details_for_date(self.date, self.location))
            
    
        return render_template("index.html", title="Panchangam", data=response_data)
       
    
    @route("json",methods=['GET','POST'])
    def dailysheet(self):
        
        self.date = date.today()

        if request.method == "GET":  
            self.location = "4684888"   
        else:
            self.location = request.form.get("location")

        response_data = json.loads(panchangam.get_details_for_date(self.date, self.location))
        
        response = app.response_class(
            response=json.dumps(response_data),
            status=200,
            mimetype='application/json'
        )
        
        return response
    
    @route("/gowri",methods=['GET','POST'])
    def gowri_details(self):
        
        self.date = date.today()

        if request.method == "GET":  
            self.location = "4684888"   
        else:
            self.location = request.form.get("location")

        response_data = json.loads(panchangam.get_gowri_details_for_date(self.date, self.location))
        
        response = app.response_class(
            response=json.dumps(response_data),
            status=200,
            mimetype='application/json'
        )
        
        return response
    
    @route("<strdate>",methods=['GET','POST'])
    @route("<strdate>/json",methods=['GET','POST'])
    def dailysheet_for_date(self, strdate):
        
        if request.method == "GET":  
            self.location = "4684888"   
        else:
            self.location = request.form.get("location")
    
        self.date = datetime.strptime(strdate, "%m-%d-%Y").date()
        response_data = json.loads(panchangam.get_details_for_date(self.date, self.location))
        
        response = app.response_class(
            response=json.dumps(response_data),
            status=200,
            mimetype='application/json'
        )
        
        return response
    
PanchangamView.register(app, route_base="/")
    
if __name__ == "__main__":
    
    app.run(host="127.0.0.1",port=8000)
