import streamlit as st
import json
import os
from datetime import datetime, date
import requests

# Set page config
st.set_page_config(page_title="LifeBoard", layout="wide")

# File paths
TASK_FILE = "tasks.json"
EVENT_FILE = "events.json"
BUDGET_FILE = "budget.json"
REMINDER_FILE = "reminders.json"

# Helper functions
def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

def ask_refresh():
    if st.button("🔄 Refresh to see changes"):
        st.experimental_rerun()

# Fallback for older Streamlit
if not hasattr(st, "experimental_rerun"):
    def fake_rerun():
        st.stop()
    st.experimental_rerun = fake_rerun

# Header
st.title("🧠 LifeBoard Dashboard")
st.subheader("Your daily life, organized in one place.")

# TASKS
st.header("📝 Task List")
tasks = load_data(TASK_FILE)
new_task = st.text_input("Add a new task")
if st.button("Add Task"):
    if new_task.strip():
        tasks.append({"task": new_task.strip(), "done": False})
        save_data(tasks, TASK_FILE)
        st.success("Task added. Please refresh the app to see the changes.")
        ask_refresh()
    else:
        st.warning("Task cannot be empty")

indexes_to_delete = []
for i, task in enumerate(tasks):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        checked = st.checkbox(task["task"], value=task["done"], key=f"task_{i}")
        tasks[i]["done"] = checked
    with col2:
        if st.button("❌", key=f"del_{i}"):
            indexes_to_delete.append(i)

if indexes_to_delete:
    for index in sorted(indexes_to_delete, reverse=True):
        tasks.pop(index)
    save_data(tasks, TASK_FILE)
    st.success("Tasks deleted. Please refresh the app to see the changes.")
    ask_refresh()

# WEATHER
st.header("🌦️ Weather")
API_KEY = "8a45e14ad4579bb108a28346e5468831"
city = st.text_input("Enter your city", "New York")
if st.button("Get Weather"):
    if API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        st.warning("Please add your OpenWeatherMap API key.")
    else:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
        if response.status_code == 200:
            data = response.json()
            st.markdown(f"### {city.title()}")
            st.markdown(f"**Temperature:** {data['main']['temp']}°C")
            st.markdown(f"**Condition:** {data['weather'][0]['description'].title()}")
        else:
            st.error("Weather info not found. Please check the city name.")

# QUOTE
st.header("💬 Quote of the Day")
if st.button("Get Quote"):
    try:
        res = requests.get("https://zenquotes.io/api/random")
        if res.status_code == 200:
            quote_data = res.json()[0]
            st.info(f"_{quote_data['q']}_\n\n— {quote_data['a']}")
        else:
            st.warning("Could not fetch quote. Try again later.")
    except:
        st.warning("Error getting quote. Try again later.")

# EVENTS
st.header("⏳ Countdown Timer Event")
events = load_data(EVENT_FILE)
event_name = st.text_input("Event Name")
event_date = st.date_input("Event Date")

if st.button("Add Event"):
    if event_name.strip():
        new_event = {
            "name": event_name.strip(),
            "datetime": event_date.strftime("%Y-%m-%d")
        }
        events.append(new_event)
        save_data(events, EVENT_FILE)
        st.success("Event added. Please refresh the app to see the changes.")
        ask_refresh()
    else:
        st.warning("Event name cannot be empty.")

st.markdown("### Your Events")
for i, event in enumerate(events):
    col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
    try:
        if " " in event["datetime"]:
            dt = datetime.strptime(event["datetime"], "%Y-%m-%d %H:%M:%S").date()
        else:
            dt = datetime.strptime(event["datetime"], "%Y-%m-%d").date()

        days_left = (dt - date.today()).days

        with col1:
            st.markdown(f"**{event['name']}** - {days_left} days left")

        with col2:
            if st.button("✏️ Edit", key=f"edit_event_{i}"):
                with st.expander(f"Edit Event: {event['name']}"):
                    new_name = st.text_input(f"New name", value=event["name"], key=f"name_{i}")
                    new_date = st.date_input(f"New date", value=dt, key=f"date_{i}")
                    if st.button("💾 Save", key=f"save_{i}"):
                        events[i] = {
                            "name": new_name.strip(),
                            "datetime": new_date.strftime("%Y-%m-%d")
                        }
                        save_data(events, EVENT_FILE)
                        st.success("Event updated. Please refresh the app to see the changes.")
                        ask_refresh()

        with col3:
            if st.button("❌ Delete", key=f"del_event_{i}"):
                events.pop(i)
                save_data(events, EVENT_FILE)
                st.success("Event deleted. Please refresh the app to see the changes.")
                ask_refresh()

    except Exception as e:
        st.warning(f"Could not parse event '{event['name']}': {e}")

# BUDGET TRACKER
st.header("💰 Budget Tracker")
budget = load_data(BUDGET_FILE)

# Initialize editing state
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "edit_desc" not in st.session_state:
    st.session_state.edit_desc = ""
if "edit_amount" not in st.session_state:
    st.session_state.edit_amount = 0.0

# Add transaction
col1, col2 = st.columns(2)
with col1:
    desc = st.text_input("Description", key="budget_desc")
with col2:
    amount = st.number_input("Amount (+income / -expense)", key="budget_amount")

if st.button("Add Transaction"):
    if desc.strip():
        budget.append({"desc": desc.strip(), "amount": float(amount), "date": str(date.today())})
        save_data(budget, BUDGET_FILE)
        st.success("Transaction added. Please refresh the app to see the changes.")
        ask_refresh()
    else:
        st.warning("Description cannot be empty.")

st.markdown("---")
st.subheader("Transaction History")
indexes_to_delete = []

for i, item in enumerate(budget):
    col1, col2, col3, col4 = st.columns([0.4, 0.3, 0.2, 0.1])

    if st.session_state.edit_index == i:
        # Edit mode
        with col1:
            new_desc = st.text_input(f"Edit Description {i}", value=st.session_state.get("edit_desc", item["desc"]), key=f"edit_desc_{i}")
        with col2:
            new_amount = st.number_input(f"Edit Amount {i}", value=st.session_state.get("edit_amount", float(item["amount"])), key=f"edit_amount_{i}")
        with col3:
            if st.button("💾 Save", key=f"save_{i}"):
                if new_desc.strip():
                    budget[i] = {
                        "desc": new_desc.strip(),
                        "amount": float(new_amount),
                        "date": item["date"],
                    }
                    save_data(budget, BUDGET_FILE)
                    st.success("Transaction updated. Please refresh the app to see the changes.")
                    st.session_state.edit_index = None
                    ask_refresh()
                else:
                    st.warning("Description cannot be empty.")
        with col4:
            if st.button("❌ Cancel", key=f"cancel_{i}"):
                st.session_state.edit_index = None
                st.info("Edit cancelled.")
    else:
        # Display mode
        with col1:
            st.markdown(f"**{item['date']}** - {item['desc']}")
        with col2:
            st.markdown(f"${float(item['amount']):.2f}")
        with col3:
            if st.button("✏️ Edit", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.session_state.edit_desc = item["desc"]
                st.session_state.edit_amount = float(item["amount"])
                st.experimental_rerun()
        with col4:
            if st.button("❌ Delete", key=f"del_{i}"):
                indexes_to_delete.append(i)

if indexes_to_delete:
    for idx in sorted(indexes_to_delete, reverse=True):
        budget.pop(idx)
    save_data(budget, BUDGET_FILE)
    st.success("Transaction(s) deleted. Please refresh the app to see the changes.")
    ask_refresh()

# Net balance
total = sum(float(item["amount"]) for item in budget)
st.metric("Net Balance", f"${total:.2f}")