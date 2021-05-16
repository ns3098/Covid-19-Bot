

from typing import Any, Text, Dict, List
from jsonpath import jsonpath
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from rasa_sdk.events import SlotSet
import re


class ActionCheckpreviousValue(Action):

    def name(self) -> Text:
        return 'actions_check_prev_value_of_state_pin'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        prev_val = tracker.get_slot('prev_selected')
        if prev_val:
            prev_val = prev_val.split('@')[1]
            text = f'Sure, do you want me to fetch cases for {prev_val}?'
        else:
            text = "Enter the State/Pincode name to see the details" 
        dispatcher.utter_message(text)
        return []


class ActionUserName(Action):

    def name(self) -> Text:
        return "actions_name_show"

    def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("name")
        if not username :
            dispatcher.utter_message(" Hi! What is your name?")
        else:
            dispatcher.utter_message(f'Hello {username}, how can I help?')

        return []


state_map = {
                        "Andaman & Nicobar": "Andaman and Nicobar Islands",
                        "Chattisgarh": "Chhattisgarh",
                        "Jammu & Kashmir": "Jammu and Kashmir",
                        "Pondicherry": "Puducherry",
                        "Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu"
                    }

covid_api = 'https://api.covid19india.org/data.json'
postal_api = 'https://api.postalpincode.in/pincode/'
state_dist_wise = 'https://api.covid19india.org/state_district_wise.json'


class Actioncoronastats(Action):

    def name(self) -> Text:
        return "actions_show_stats"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        
        STATE = tracker.get_slot("state")
        PINCODE = tracker.get_slot("pincode")

        prev_val = tracker.get_slot('prev_selected')

        if tracker.latest_message['intent'].get('name')=='deny':

            resp = requests.get(covid_api)
            resp = resp.json()

            total_data = jsonpath(resp, '$..statewise[?(@.state=="Total")]')[0]  # Use jsonpath to acess data

            text = "Now Showing Nationwide Cases --> " + " Since Last 24 Hours : "+ "\n" + "Active: " + total_data[
                    "active"] + " \n" + "Confirmed: " + total_data["confirmed"] + " \n" + "Recovered: " + total_data[
                              "recovered"] + " \n" + "Deaths: " + total_data["deaths"] + " \n"

            dispatcher.utter_message(text)
            return []

        elif tracker.latest_message['intent'].get('name')=='affirm':
            

            value = prev_val.split("@") if prev_val else None

            if not value:
                dispatcher.utter_message("Ohh oo I didn't understand.")
                return []

            if value[0] == 'pincode':
                
                resp = requests.get(postal_api + value[1])
                resp = resp.json()

                district = jsonpath(resp, f'$..PostOffice.*.District')[0]  # Use jsonpath to acess data
                district = re.sub("\(.*?\)","",district).replace('&', 'and') 

                state = jsonpath(resp, '$..PostOffice.*.State')[0]
                state = re.sub("\(.*?\)","",state).replace('&', 'and')

                state = state_map.get(state, state).title()
                
                res = requests.get(state_dist_wise)
                res = res.json()

                state_data =  res[state]['districtData'][district.title()]

                text = "Showing Cases For --> " + district + " (" + state + ") " + " Since Last 24 Hours : "+ "\n"+  "\n" +  "\n"+ "Active: " + str(state_data["active"]) + " \n" + "Confirmed: " + str(state_data["confirmed"]) + " \n" + "Recovered: " + str(state_data["recovered"]) + " \n" + "Deaths: " + str(state_data["deceased"])+" \n"+ "\n" + "\n"+ "    Cases Reported  "+ "\n" +  " \n" + "Confirmed Today: " + str(state_data["delta"]["confirmed"]) + " \n" + "Recovered Today: " + str(state_data["delta"]["recovered"]) + " \n" + "Deaths Today: " + str(state_data["delta"]["deceased"])

                dispatcher.utter_message(text)
            
            else:
                
                state = value[1].title()
                state = 'Total' if state == 'India' else state
                resp = requests.get(covid_api)
                resp = resp.json()  
                total_data = jsonpath(resp, f'$..statewise[?(@.state=="{state}")]')[0]

                text = "Showing Cases For --> " + state + " Since Last 24 Hours : "+ "\n" + "Active: " + total_data[
                    "active"] + " \n" + "Confirmed: " + total_data["confirmed"] + " \n" + "Recovered: " + total_data[
                              "recovered"] + " \n" + "Deaths: " + total_data["deaths"]

                dispatcher.utter_message(text)
            return []
        
        else:
            try:
                latest_slots = tracker.latest_message['entities']
                All_States = [
                    "Total", "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh",
                    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand",
                    "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha",
                    "Puducherry", "Punjab", "Rajasthan", "Sikkim", "State Unassigned", "Tamil Nadu", "Telangana", "Tripura",
                    "Uttar Pradesh", "Uttarakhand","West Bengal"
                    ]
                if latest_slots[0]['entity'] == 'state':
                    STATE = latest_slots[0]["value"]
                    if STATE.title() == 'India':
                        STATE = 'Total'
                    if STATE not in All_States:
                        dispatcher.utter_message("Ohh oo seems like you entered wrong State name. Take some help from here :\n\n" + ', '.join(All_States) + '\n\n')
                        return []
                    
                    resp = requests.get(covid_api).json()
                    state_data = jsonpath(resp, f'$..statewise[?(@.state=="{STATE}")]')[0]
                    STATE = STATE if STATE!='Total' else 'India'
                    text = "Showing Cases For --> " + STATE + " Since Last 24 Hours : "+ "\n" + "Active: " + state_data["active"] + " \n" + "Confirmed: " + state_data["confirmed"] + " \n" + "Recovered: " + state_data["recovered"] + " \n" + "Deaths: " + state_data["deaths"] + " \n" + "As Per Data On: " + state_data["lastupdatedtime"]

                    dispatcher.utter_message(text)
                    return [SlotSet("prev_selected", 'state' + "@" + STATE)]
                    
                elif latest_slots[0]['entity'] == 'pincode':
                    PINCODE = latest_slots[0]["value"]
                    res = requests.get(postal_api + PINCODE).json()
                    msg = jsonpath(res, '$..Message')[0] != 'No records found'
                    if msg:
                        district = jsonpath(res, f'$..PostOffice.*.District')[0]  # Use jsonpath to acess data
                        district = re.sub("\(.*?\)","",district).replace('&', 'and') 
                        state = jsonpath(res, '$..PostOffice.*.State')[0]
                        state = re.sub("\(.*?\)","",state).replace('&', 'and')
                        
                        state = state_map.get(state, state).title()
                        res = requests.get(state_dist_wise)
                        res = res.json()
                        state_data =  res[state]['districtData'].get(district, '')
                        if state_data:
                            text = "Showing Cases For --> " + district + " (" + state + ") " + "Since Last 24 Hours : "+ "\n"+  "\n" +  "\n"+ "Active: " + str(state_data["active"]) + " \n" + "Confirmed: " + str(state_data["confirmed"]) + " \n" + "Recovered: " + str(state_data["recovered"]) + " \n" + "Deaths: " + str(state_data["deceased"])+" \n"+ "\n" + "\n"+ "Cases Reported"+ "\n" +  " \n" + "Confirmed Today: " + str(state_data["delta"]["confirmed"]) + " \n" + "Recovered Today: " + str(state_data["delta"]["recovered"]) + " \n" + "Deaths Today: " + str(state_data["delta"]["deceased"])
                        else:
                            text = f'Sorry! Data for {district} ({state}) District is not present. Not remembering for furthur use.'
                        dispatcher.utter_message(text)
                        return [SlotSet('prev_selected', 'pincode' + "@" + PINCODE)] if state_data else []

                    else:
                        dispatcher.utter_message("Ohh oo seems like you entered wrong PinCode. Please Check again then try. Not remembering it for furthur use.")

                else:
                    dispatcher.utter_message("Ohh oo seems like I was unable to understand whether it's a State or Pincode :( . Please check that you have entered correct value. So that I can help. \n")

                return []
            except Exception as e:
                dispatcher.utter_message("I am sorry something went wrong from my side. I am not so smart as of now. Trying to learn from humans.")
                return []