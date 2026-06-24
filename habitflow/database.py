import json
import os
import datetime

DATA_FILE="habits.json"
def initialize():
    if not os.path.exists(DATA_FILE):
        save_data({"habits":[]})

def save_data(data):
    with open(DATA_FILE,"w") as f:
        json.dump(data,f,indent=4)
def load_data():
    with open(DATA_FILE,"r") as f:
        return json.load(f)
    
def get_all_habits():
    data=load_data()
    return data["habits"]
def add_habits(name,category,reminder_days,reminder_time):
    data=load_data()
    habit={
        "id":len(data["habits"])+1,
        "name":name,
        "category":category,
        "reminder_days":reminder_days,
        "reminder_time":reminder_time,
        "completions":[],
        "created_at": str(datetime.date.today())
    }
    data["habits"].append(habit)
    save_data(data)

def mark_done(habit_id):
    data=load_data()
    today = str(datetime.date.today())
    for habit in data["habits"]:
        if habit["id"]==habit_id:
            if today not in habit["completions"]:
                habit["completions"].append(today)
            save_data(data)

def delete_habit(habit_id):
    data=load_data()
    new_list=[]
    for habit in data["habits"]:
        if habit["id"]!=habit_id:
            new_list.append(habit)

    data["habits"]=new_list
    save_data(data)

def edit_habit(habit_id,name,category,reminder_days,reminder_time):
    data=load_data()
    for habit in data["habits"]:
        if habit["id"]==habit_id:
            habit["name"]=name
            habit["category"]=category
            habit["reminder_days"]=reminder_days
            habit["reminder_time"]=reminder_time
    save_data(data) 

def get_streak(habit_id):
    data=load_data()
    for habit in data["habits"]:
        if habit["id"]==habit_id:
            completions =habit["completions"]
            streak=0
            check_day=datetime.date.today()

            while str(check_day) in completions:
                streak+=1
                check_day=check_day-datetime.timedelta(days=1)

            return streak
    return 0

