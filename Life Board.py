import streamlit as st
import json
import os
from datetime import datetime, date
import requests
from deep_translator import GoogleTranslator

# --------------------- CONFIG ---------------------
st.set_page_config(page_title="LifeBoard", layout="wide")

# File paths
TASK_FILE = "tasks.json"
EVENT_FILE = "events.json"
BUDGET_FILE = "budget.json"
REMINDER_FILE = "reminders.json"

# --------------------- TRANSLATION SYSTEM ---------------------
LANGUAGES = {
    "en": {
        "title": "🧠 LifeBoard Dashboard",
        "subtitle": "Your daily life, organized in one place.",
        "tasks": "📝 Task List",
        "add_task": "Add Task",
        "weather": "🌦️ Weather",
        "enter_city": "Enter your city",
        "get_weather": "Get Weather",
        "quote": "💬 Quote of the Day",
        "get_quote": "Get Quote",
        "event": "⏳ Countdown Timer Event",
        "add_event": "Add Event",
        "budget": "💰 Budget Tracker",
        "add_transaction": "Add Transaction",
        "net_balance": "Net Balance",
        "days_left": "days left",
        "your_events": "Your Events",
        "new_name": "New name",
        "new_date": "New date",
        "edit_event": "Edit Event",
        "event_added": "Event added. Refresh to view.",
        "event_deleted": "Event deleted.",
        "event_updated": "Event updated successfully.",
        "task_added": "Task added. Please refresh to see changes.",
        "task_empty": "Task cannot be empty.",
        "event_name_empty": "Event name cannot be empty.",
        "transaction_added": "Transaction added. Please refresh.",
        "description_empty": "Description cannot be empty.",
        "tasks_deleted": "Tasks deleted. Please refresh.",
        "transactions_deleted": "Transaction(s) deleted. Please refresh.",
        "task_delete_confirm": "Delete task",
        "edit": "Edit",
        "delete": "Delete",
        "save": "Save",
        "cancel": "Cancel",
        "refresh": "Refresh to see changes"
    },
    "hi": {
        "title": "🧠 लाइफबोर्ड डैशबोर्ड",
        "subtitle": "आपका दैनिक जीवन, एक ही स्थान पर व्यवस्थित।",
        "tasks": "📝 कार्य सूची",
        "add_task": "कार्य जोड़ें",
        "weather": "🌦️ मौसम",
        "enter_city": "अपना शहर दर्ज करें",
        "get_weather": "मौसम देखें",
        "quote": "💬 दिन का उद्धरण",
        "get_quote": "उद्धरण प्राप्त करें",
        "event": "⏳ काउंटडाउन टाइमर कार्यक्रम",
        "add_event": "कार्यक्रम जोड़ें",
        "budget": "💰 बजट ट्रैकर",
        "add_transaction": "लेन-देन जोड़ें",
        "net_balance": "कुल शेष राशि",
        "days_left": "दिन बचे",
        "your_events": "आपकी घटनाएँ",
        "new_name": "नया नाम",
        "new_date": "नयी तारीख",
        "edit_event": "कार्यक्रम संपादित करें",
        "event_added": "कार्यक्रम जोड़ा गया। देखने के लिए रिफ़्रेश करें।",
        "event_deleted": "कार्यक्रम हटाया गया।",
        "event_updated": "कार्यक्रम सफलतापूर्वक अपडेट हो गया।",
        "task_added": "कार्य जोड़ा गया। कृपया बदलाव देखने के लिए रिफ्रेश करें।",
        "task_empty": "कार्य खाली नहीं हो सकता।",
        "event_name_empty": "कार्य का नाम खाली नहीं हो सकता।",
        "transaction_added": "लेन-देन जोड़ा गया। कृपया रिफ्रेश करें।",
        "description_empty": "विवरण खाली नहीं हो सकता।",
        "tasks_deleted": "कार्य हटाए गए। कृपया रिफ्रेश करें।",
        "transactions_deleted": "लेन-देन हटाए गए। कृपया रिफ्रेश करें।",
        "task_delete_confirm": "कार्य हटाएँ",
        "edit": "संपादित करें",
        "delete": "हटाएँ",
        "save": "सहेजें",
        "cancel": "रद्द करें",
        "refresh": "बदलाव देखने के लिए रिफ्रेश करें"
    },
    "es": {
        "title": "🧠 Panel de LifeBoard",
        "subtitle": "Tu vida diaria, organizada en un solo lugar.",
        "tasks": "📝 Lista de tareas",
        "add_task": "Agregar tarea",
        "weather": "🌦️ Clima",
        "enter_city": "Ingresa tu ciudad",
        "get_weather": "Obtener clima",
        "quote": "💬 Cita del día",
        "get_quote": "Obtener cita",
        "event": "⏳ Temporizador de cuenta regresiva",
        "add_event": "Agregar evento",
        "budget": "💰 Rastreador de presupuesto",
        "add_transaction": "Agregar transacción",
        "net_balance": "Saldo neto",
        "days_left": "días restantes",
        "your_events": "Tus eventos",
        "new_name": "Nuevo nombre",
        "new_date": "Nueva fecha",
        "edit_event": "Editar evento",
        "event_added": "Evento agregado. Actualice para ver.",
        "event_deleted": "Evento eliminado.",
        "event_updated": "Evento actualizado correctamente.",
        "task_added": "Tarea agregada. Por favor, actualice para ver los cambios.",
        "task_empty": "La tarea no puede estar vacía.",
        "event_name_empty": "El nombre del evento no puede estar vacío.",
        "transaction_added": "Transacción agregada. Por favor, actualice.",
        "description_empty": "La descripción no puede estar vacía.",
        "tasks_deleted": "Tareas eliminadas. Por favor, actualice.",
        "transactions_deleted": "Transacción(es) eliminada(s). Por favor, actualice.",
        "task_delete_confirm": "Eliminar tarea",
        "edit": "Editar",
        "delete": "Eliminar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "refresh": "Actualizar para ver los cambios"
    }
}

# Sidebar language selector
st.sidebar.header("🌐 Language / भाषा / Idioma")
lang = st.sidebar.selectbox("Choose language", ["English", "हिंदी", "Español"], index=0)
lang_code = {"English": "en", "हिंदी": "hi", "Español": "es"}[lang]

# Translator function (used for system messages & dynamic API text)
def auto_translate(text, dest_lang):
    if dest_lang == "en" or not text:
        return text
    try:
        return GoogleTranslator(source="auto", target=dest_lang).translate(text)
    except Exception:
        return text  # fallback

# --------------------- HELPERS ---------------------
def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []


def save_data(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ask_refresh():
    if st.button("🔄 " + LANGUAGES[lang_code]["refresh"], key="refresh_btn"):
        st.rerun()

# --------------------- HEADER ---------------------
st.title(LANGUAGES[lang_code]["title"])
st.subheader(LANGUAGES[lang_code]["subtitle"])

# --------------------- TASKS ---------------------
st.header(LANGUAGES[lang_code]["tasks"])
tasks = load_data(TASK_FILE)

new_task = st.text_input(LANGUAGES[lang_code]["add_task"], key="new_task_input")
if st.button(LANGUAGES[lang_code]["add_task"], key="add_task_button"):
    if new_task.strip():
        tasks.append({"task": new_task.strip(), "done": False})
        save_data(tasks, TASK_FILE)
        st.success(auto_translate(LANGUAGES[lang_code]["task_added"], lang_code))
        ask_refresh()
    else:
        st.warning(auto_translate(LANGUAGES[lang_code]["task_empty"], lang_code))


task_delete_list = []
for i, task in enumerate(tasks):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        # show the task text as entered by user (do not auto-translate user content)
        checked = st.checkbox(task.get("task", ""), value=task.get("done", False), key=f"task_checkbox_{i}")
        tasks[i]["done"] = checked
    with col2:
        if st.button("❌", key=f"task_delete_btn_{i}"):
            task_delete_list.append(i)

if task_delete_list:
    for idx in sorted(task_delete_list, reverse=True):
        tasks.pop(idx)
    save_data(tasks, TASK_FILE)
    st.success(auto_translate(LANGUAGES[lang_code]["tasks_deleted"], lang_code))
    ask_refresh()

# --------------------- WEATHER ---------------------
st.header(LANGUAGES[lang_code]["weather"])
API_KEY = "8a45e14ad4579bb108a28346e5468831"
city = st.text_input(LANGUAGES[lang_code]["enter_city"], "New York", key="city_input")

if st.button(LANGUAGES[lang_code]["get_weather"], key="get_weather_button"):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=6)
        if response.status_code == 200:
            data = response.json()
            st.markdown(f"### {auto_translate(city.title(), lang_code)}")
            st.markdown(f"**{auto_translate('Temperature', lang_code)}:** {data['main']['temp']}°C")
            condition = auto_translate(data['weather'][0]['description'].title(), lang_code)
            st.markdown(f"**{auto_translate('Condition', lang_code)}:** {condition}")
        else:
            st.error(auto_translate("Weather info not found. Please check the city name.", lang_code))
    except Exception:
        st.error(auto_translate("Weather service error. Try again later.", lang_code))

# --------------------- QUOTE ---------------------
st.header(LANGUAGES[lang_code]["quote"])
if st.button(LANGUAGES[lang_code]["get_quote"], key="get_quote_button"):
    try:
        res = requests.get("https://zenquotes.io/api/random", timeout=6)
        if res.status_code == 200:
            quote_data = res.json()[0]
            quote = f"_{quote_data['q']}_\n\n— {quote_data['a']}"
            st.info(auto_translate(quote, lang_code))
        else:
            st.warning(auto_translate("Could not fetch quote. Try again later.", lang_code))
    except Exception:
        st.warning(auto_translate("Error getting quote. Try again later.", lang_code))

# --------------------- COUNTDOWN EVENTS (UPDATED, STABLE) ---------------------
st.header(LANGUAGES[lang_code]["event"])
events = load_data(EVENT_FILE)

# Add new event
# keep user-entered event names as-is; system messages are translated
new_event_name = st.text_input(LANGUAGES[lang_code]["add_event"], key="new_event_name")
new_event_date = st.date_input(LANGUAGES[lang_code]["new_date"], key="new_event_date")

if st.button(LANGUAGES[lang_code]["add_event"], key="add_event_btn"):
    if new_event_name.strip():
        events.append({"name": new_event_name.strip(), "datetime": new_event_date.strftime("%Y-%m-%d")})
        save_data(events, EVENT_FILE)
        st.success(auto_translate(LANGUAGES[lang_code]["event_added"], lang_code))
        st.rerun()
    else:
        st.warning(auto_translate(LANGUAGES[lang_code]["event_name_empty"], lang_code))

st.markdown("### " + auto_translate(LANGUAGES[lang_code]["your_events"], lang_code))

# Session state for event editing
if "event_edit_index" not in st.session_state:
    st.session_state.event_edit_index = None

for i, event in enumerate(events):
    # safe-guard event data
    try:
        dt = datetime.strptime(event.get("datetime", date.today().strftime("%Y-%m-%d")), "%Y-%m-%d").date()
    except Exception:
        dt = date.today()

    days_left = (dt - date.today()).days

    # layout columns
    col1, col2, col3 = st.columns([0.55, 0.25, 0.2])

    with col1:
        st.markdown(f"**{event.get('name','Unnamed Event')}** — {days_left} {auto_translate(LANGUAGES[lang_code]['days_left'], lang_code)}")

    # If this event is in edit mode
    if st.session_state.event_edit_index == i:
        with st.expander(auto_translate(LANGUAGES[lang_code]["edit_event"], lang_code), expanded=True):
            edit_name = st.text_input(auto_translate(LANGUAGES[lang_code]["new_name"], lang_code), value=event.get('name',''), key=f"edit_event_name_{i}")
            try:
                edit_date = st.date_input(auto_translate(LANGUAGES[lang_code]["new_date"], lang_code), value=dt, key=f"edit_event_date_{i}")
            except Exception:
                edit_date = dt

            save_col, cancel_col = st.columns(2)
            if save_col.button(LANGUAGES[lang_code]["save"], key=f"save_event_{i}"):
                events[i] = {"name": edit_name.strip(), "datetime": edit_date.strftime("%Y-%m-%d")}
                save_data(events, EVENT_FILE)
                st.success(auto_translate(LANGUAGES[lang_code]["event_updated"], lang_code))
                st.session_state.event_edit_index = None
                st.rerun()

            if cancel_col.button(LANGUAGES[lang_code]["cancel"], key=f"cancel_event_{i}"):
                st.session_state.event_edit_index = None
                st.rerun()

    else:
        with col2:
            if st.button(LANGUAGES[lang_code]["edit"], key=f"enter_edit_event_{i}"):
                st.session_state.event_edit_index = i
                st.rerun()
        with col3:
            if st.button(LANGUAGES[lang_code]["delete"], key=f"delete_event_{i}"):
                events.pop(i)
                save_data(events, EVENT_FILE)
                st.success(auto_translate(LANGUAGES[lang_code]["event_deleted"], lang_code))
                st.rerun()

# --------------------- BUDGET TRACKER ---------------------
st.header(LANGUAGES[lang_code]["budget"])
budget = load_data(BUDGET_FILE)

if "budget_edit_index" not in st.session_state:
    st.session_state.budget_edit_index = None

col1, col2 = st.columns(2)
with col1:
    desc = st.text_input(auto_translate("Description", lang_code), key="new_txn_desc")
with col2:
    amount = st.number_input(auto_translate("Amount (+income / -expense)", lang_code), key="new_txn_amount")

if st.button(LANGUAGES[lang_code]["add_transaction"], key="add_transaction_btn"):
    if desc.strip():
        budget.append({"desc": desc.strip(), "amount": float(amount), "date": str(date.today())})
        save_data(budget, BUDGET_FILE)
        st.success(auto_translate(LANGUAGES[lang_code]["transaction_added"], lang_code))
        st.rerun()
    else:
        st.warning(auto_translate(LANGUAGES[lang_code]["description_empty"], lang_code))

st.markdown("---")
st.subheader(auto_translate("Transaction History", lang_code))

budget_delete_list = []
for i, item in enumerate(budget):
    c1, c2, c3, c4 = st.columns([0.45, 0.25, 0.2, 0.1])

    if st.session_state.budget_edit_index == i:
        with c1:
            new_desc = st.text_input(f"Edit Description {i}", value=item.get('desc',''), key=f"budget_edit_desc_{i}")
        with c2:
            new_amount = st.number_input(f"Edit Amount {i}", value=float(item.get('amount',0.0)), key=f"budget_edit_amount_{i}")
        with c3:
            if st.button(LANGUAGES[lang_code]["save"], key=f"save_budget_{i}"):
                budget[i] = {"desc": new_desc.strip(), "amount": float(new_amount), "date": item.get('date', str(date.today()))}
                save_data(budget, BUDGET_FILE)
                st.success(auto_translate(LANGUAGES[lang_code]["event_updated"], lang_code))
                st.session_state.budget_edit_index = None
                st.rerun()
        with c4:
            if st.button(LANGUAGES[lang_code]["cancel"], key=f"cancel_budget_{i}"):
                st.session_state.budget_edit_index = None
                st.rerun()

    else:
        with c1:
            st.markdown(f"**{item.get('date','')}** - {item.get('desc','')}")
        with c2:
            st.markdown(f"${float(item.get('amount',0.0)):.2f}")
        with c3:
            if st.button(LANGUAGES[lang_code]["edit"], key=f"edit_budget_{i}"):
                st.session_state.budget_edit_index = i
                st.rerun()
        with c4:
            if st.button(LANGUAGES[lang_code]["delete"], key=f"delete_budget_{i}"):
                budget_delete_list.append(i)

if budget_delete_list:
    for idx in sorted(budget_delete_list, reverse=True):
        budget.pop(idx)
    save_data(budget, BUDGET_FILE)
    st.success(auto_translate(LANGUAGES[lang_code]["transactions_deleted"], lang_code))
    st.rerun()

# Net balance
try:
    total = sum(float(item.get("amount", 0)) for item in budget)
except Exception:
    total = 0.0
st.metric(auto_translate(LANGUAGES[lang_code]["net_balance"], lang_code), f"${total:.2f}")

# --------------------- REMINDERS (simple placeholder) ---------------------
# You can extend this section later if you want push notifications or scheduled checks.

st.markdown("---")
if st.button("🛠️ Debug: Show saved files keys", key="debug_show"):
    st.write({
        "tasks": len(load_data(TASK_FILE)),
        "events": len(load_data(EVENT_FILE)),
        "budget_items": len(load_data(BUDGET_FILE))
    })
