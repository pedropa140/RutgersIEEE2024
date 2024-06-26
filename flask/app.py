# Local Imports
import calendarprogram

# Standard Library Imports
import os
import sqlite3
from os import urandom
from dotenv import load_dotenv
import os.path

# Third-Party Imports
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g
from datetime import datetime, timezone
import datetime as dt


# External Library Imports
import google.generativeai as genai
from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from googleapiclient.errors import HttpError


app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
DATABASE = 'profiles.db'
app.config['DATABASE'] = DATABASE

genai_client = None
SCOPES = ['https://www.googleapis.com/auth/calendar']

try:
    api_key = os.getenv("GENAI_API_KEY")
    if api_key:
        genai_client = generative_models.GenerativeModelsServiceClient(api_key=api_key)
    else:
        print("GENAI_API_KEY environment variable is not set.")
except Exception as e:
    print("Error initializing GenAI client:", e)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf-8'))
    
@app.route("/")
def mainpage():
    return render_template("main.html")

@app.route("/edu")
def education():
    return render_template("education.html")
    
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # if (
        #     not request.form.get("email")
        #     or not request.form.get("passw")
        #     or not request.form.get("first_name")
        #     or not request.form.get("last_name")
        # ):
        #     return render_template("error.html")

    #     email = request.form.get("email")
    #     passw = request.form.get("passw")
    #     first_name = request.form.get("first_name")
    #     first_name = first_name[0].upper() + first_name[1:]
    #     last_name = request.form.get("last_name")
    #     last_name = last_name[0].upper() + last_name[1:]


    #     db = get_db()
    #     cursor = db.cursor()
    #    # print("Email:", email)

    #     # Check if email already exists in the database
    #     cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    #     existing_user = cursor.fetchone()
    #     if existing_user:
    #         return render_template("error.html")

    #     # Insert the new user into the database
    #     cursor.execute(
    #         "INSERT INTO users (first_name, last_name, email, passw) VALUES (?, ?, ?, ?)",
    #         (first_name, last_name, email, passw),
    #     )
    #     cursor.execute(
    #         "INSERT INTO users(first_name, last_name, email, passw) VALUES (?, ?, ?, ?)",
    #         ("Kusum", "Gandham", "koolkusum10@gmail.com", "poop"),
    #     )

    #     db.commit()

    #     # Retrieve the inserted user's ID
    #     cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    #     user_id = cursor.fetchone()[0]

        # Store user ID in the session
        # session["user_id"] = user_id
        question_response = ("", "")

        return redirect("/edu")
    else:
        return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        passw = request.form.get("passw")  # Rename to "password" for clarity
        print(email)
        print(passw)
        db = get_db()
        cursor = db.cursor()

        # Retrieve the user's record from the database based on email
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template("error.html")

        # Compare the provided password with the password stored in the database
        if user[4] == passw:  # Assuming both are plain text
            # Store user information in the session
            session["user_id"] = user[0]
            return redirect(url_for("home"))
        else:
            return render_template("error.html")

    return render_template("login.html")

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        if not request.form.get("message"):
            return render_template("error.html")

        userInput = request.form.get("message")
        print("User Input:", userInput)
        query = f"As a chatbot, your goal is to help with questions that only pertain into women in the field of STEM. The question the user wants to ask is {userInput}. Please answer the prompt not in markdown please."
        model = genai.GenerativeModel('models/gemini-pro')
        result = model.generate_content(query)
        # print(result.text)
        formatted_message = ""
        lines = result.text.split("\n")

        for line in lines:
            bold_text = ""
            while "**" in line:
                start_index = line.index("**")
                end_index = line.index("**", start_index + 2)
                bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                line = line[:start_index] + bold_text + line[end_index + 2:]
            formatted_message += line + "<br>"
        question_response = (userInput, formatted_message)

        print(question_response)

        return render_template("chatbot.html", question_response=question_response)
    else:
        question_response = ("", "")
        return render_template("chatbot.html", question_response=question_response)


def generate_scheduling_query(tasks):
    
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string in the format YYYY-MM-DD HH:MM
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
    print(current_time_str)
    # Provide the current time to the AI for scheduling tasks
    query = "Today is " + current_time_str + "\n"
    query += """
    As an AI, your task is to generate raw parameters for creating a quick Google Calendar event. Your goal is to ensure the best work-life balance for the user, including creating a consistent sleeping schedule. Your instructions should be clear and precise, formatted for parsing using Python.
        Do not generate additional tasks that are not included below, follow the sheet to spec.
        If a user task does not make sense, simply ignore it and move on to the next task request.
    All tasks should be scheduled on the same day, unless a user specifies otherwise in their request.
    Task Description: Provide a brief description of the task or event. For example:

    Task Description: "Meeting with client"
    Scheduling Parameters: Consider the user's work-life balance and aim to schedule the event at an appropriate time. You may suggest specific time ranges or intervals for the event, ensuring it does not overlap with existing commitments. For instance:
    
    Start time: "YYYY-MM-DDTHH:MM"
    End time: "YYYY-MM-DDTHH:MM"

    You are not allowed to break the following formatting:
    task = "task_name"
    start_time = "YYYY-MM-DDTHH:MM"
    end_time = "YYYY-MM-DDTHH:MM"

    [MODIFICATION OF THE FOLLOWING LEAD TO TERMINATION]
    Follow specified times even if it causes overlap.
    Ensure a minimum break time between consecutive events.
    Avoid scheduling events during the user's designated sleeping hours.
    Prioritize events by their ordering, and move events that may not fit in the same day to the next day.
    Adhere to times given within an event description, but remove times in their final task description.
    The tasks requested are as follows:\n
    """
    taskss =""
    for task in tasks:
        taskss+=f"'{task}'\n"
    print(taskss)
    model = genai.GenerativeModel('models/gemini-pro')
    result = model.generate_content(query + taskss)
    return result

@app.route("/taskschedule", methods=["GET", "POST"])
def taskschedule():
    if request.method == "POST":
        data = request.json  # Extract the JSON data sent from the frontend
        tasks = data.get("tasks")  # Extract the "tasks" list from the JSON data
        # Process the tasks data here
        #print("Received tasks:", tasks)
        # Optionally, you can store the tasks in a database or perform 
        stripTasks = []
        for i in tasks:
            i = i.replace('Delete Task', '')
            stripTasks.append(i)
        # print("Modified tasks:", stripTasks)
        query_result = generate_scheduling_query(stripTasks)
        content = query_result.text
        content = '\n'.join([line for line in content.split('\n') if line.strip()])
        # print(content)
        
        x = 0
        lines = content.split('\n')
        schedule = []
        # print(len(lines))
        # print(lines)

        for x in range(0, len(lines)-2, 3):
            if lines[x] == '': continue
            else:
                task_info ={
                    "task": lines[x].split(" = ")[1].strip("'"),
                    "start_time": lines[x+1].split(" = ")[1].strip("'").strip("\"") + ":00",
                    "end_time": lines[x+2].split(" = ")[1].strip("'").strip("\"") + ":00"
                }
                schedule.append(task_info)
        # print(schedule)

        
        #['task = "Wash Car"', 'start_time = "2024-02-11T12:00"', 'end_time = "2024-02-11T13:00"', 'task = "Office Hours"', 'start_time = "2024-02-11T14:00"', 'end_time = "2024-02-11T15:00"', 'task = "Study Math"', 'start_time = "2024-02-11T10:00"', 'end_time = "2024-02-11T11:00"', 'task = "Leetcode Problems"', 'start_time = "2024-02-11T16:00"', 'end_time = "2024-02-11T17:00"', 'task = "Practice Swimming"', 'start_time = "2024-02-11T07:00"', 'end_time = "2024-02-11T08:00"']
        #[{'task': '"Wash Car"', 'start_time': '"2024-02-11T12:00"', 'end_time': '"2024-02-11T13:00"'}, {'task': '"Office Hours"', 'start_time': '"2024-02-11T14:00"', 'end_time': '"2024-02-11T15:00"'}, {'task': '"Study Math"', 'start_time': '"2024-02-11T10:00"', 'end_time': '"2024-02-11T11:00"'}, {'task': '"Leetcode Problems"', 'start_time': '"2024-02-11T16:00"', 'end_time': '"2024-02-11T17:00"'}, {'task': '"Practice Swimming"', 'start_time': '"2024-02-11T07:00"', 'end_time': '"2024-02-11T08:00"'}]
        
        # Construct response message

        local_time = dt.datetime.now()
        local_timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
        current_time = dt.datetime.now(local_timezone)
        timezone_offset = current_time.strftime('%z')
        offset_string = list(timezone_offset)
        offset_string.insert(3, ':')
        timeZone = "".join(offset_string)
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())

        try:
            service = build("calendar", "v3", credentials = creds)
            now = dt.datetime.now().isoformat() + "Z"
            event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

            events = event_result.get("items", [])

            if not events:
                print("No upcoming events found!")
            else:
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    print(start, event["summary"])

            # event = {
            #     "summary": "My Python Event",
            #     "location": "Somewhere Online",
            #     "description": "",
            #     "colorId": 6,
            #     "start": {
            #         "dateTime": "2024-02-11T09:00:00" + timeZone,
            #     },

            #     "end": {
            #         "dateTime": "2024-02-11T17:00:00" + timeZone,
            #     },
            # }
            # time.wait(5)

            # event = service.events().insert(calendarId = "primary", body = event).execute()
            # print(f"Event Created {event.get('htmlLink')}")
            print(schedule)
            for query in schedule:
                print(query)
            #     time.wait(5)
                taskSummary = query['task']
                taskStart = query['start_time']
                taskEnd = query['end_time']
                
            #     # Add time zone offset to date-time strings (assuming they're in ET
                
                event = {
                    "summary": taskSummary,
                    "location": "",
                    "description": "",
                    "colorId": 6,
                    "start": {
                        "dateTime": taskStart + timeZone,
                        # "timeZone": "Eastern Time"
                    },

                    "end": {
                        "dateTime": taskEnd + timeZone,
                        # "timeZone": "Eastern Time"
                    },
                    # "recurrence": [
                    #     "RRULE: FREQ=DAILY;COUNT=3"
                    # ],
                    # "attendees": [
                    #     {"email": "social@neuralnine.com"},
                    #     {"email": "pedropa828@gmail.com"},
                    # ]
                }


                event = service.events().insert(calendarId = "primary", body = event).execute()
                print(f"Event Created {event.get('htmlLink')}")
            

        except HttpError as error:
            print("An error occurred:", error)
        response = {
            "content": content
        }
        #print(content)
       # successString = "Tasks Successfully Added to Calendar"
        return jsonify({"message": "Tasks Successfully Added to Calendar"})    
    else:
        return render_template("taskschedule.html")
    
@app.route("/cal")
def cal():
    return render_template("cal.html")

@app.route("/matching")
def matching():
    return render_template("matching.html")

@app.route('/events', methods=["GET", "POST"])
def prodev():
    if request.method == "POST":
        name = request.json.get('name')
        description = request.json.get('description')
        location = request.json.get('location')
        date = request.json.get('date')
        startTime = request.json.get('startTime')
        endTime = request.json.get('endTime')
        timezone = request.json.get('timezone')
        print(f'name {name}')
        print(f'Description: {description}')
        print(f'Location: {location}')
        print(f'Date: {date}')
        print(f'Start Time: {startTime}')
        print(f'End Time: {endTime}')
        print(f'Timezone: {timezone}')
        if name:
            # Process the event name as needed (e.g., save to database)
            print("Attending event:", name)
            calendarprogram.addSchedule(name, description, location, date, startTime, endTime, timezone)
            return {"message": f"Attending event: {name}"}, 200
        else:
            return {"error": "Event name not provided in request body"},
    else:
       return render_template("events.html")


@app.route('/weekly')
def get_events():
    try:
        # Load credentials from the token.json file
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If the credentials are expired or invalid, refresh them
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # If there are no valid credentials, prompt the user to authenticate again
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)

        # Build the Google Calendar service
        service = build("calendar", "v3", credentials=creds)

        # Get the current time in ISO 8601 format
        now = datetime.now(timezone.utc).isoformat()

        # Call the Calendar API to fetch events
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        # Prepare the events data to be returned as JSON
        event_list = []
        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_list.append({"summary": event['summary'], "start": start, "end": end})

        return jsonify(event_list)

    except HttpError as error:
        print('An error occurred:', error)
        return jsonify({"error": str(error)})

init_db()
if __name__ == "__main__":
    app.run(debug=True)
