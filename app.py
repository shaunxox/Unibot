from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# --- NLTK IMPORTS ---
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# --------------------

# --- NLTK Data Download (Runs ONCE when app loads) ---
def download_nltk_resources():
    # This downloads NLTK data if it's missing (required for tokenizers and stopwords)
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except:
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("NLTK data downloaded.")

download_nltk_resources() 
# ----------------------------------------------------

# CRUCIAL FIX: Set static_folder to 'static' so Flask knows where your HTML files are
app = Flask(__name__, static_folder='static') 
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models (omitted for brevity, they remain unchanged)
class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)

class ExamSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    exam_date = db.Column(db.String(50), nullable=False)

class StaffContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)

class CollegeEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

# Static links (omitted for brevity, they remain unchanged)
COLLEGE_LINKS = {
    "library": "https://college.edu/library",
    "portal": "https://college.edu/portal",
    "hostel": "https://college.edu/hostel",
    "sports": "https://college.edu/sports",
    "canteen": "https://college.edu/canteen"
}

# ----------------------------------------------------------------------
# ROUTES TO SERVE HTML FILES (LOGICALLY CORRECTED)
# ----------------------------------------------------------------------
@app.route('/')
def login_page():
    return app.send_static_file('login.html')

@app.route('/chat')
def index():
    return app.send_static_file('index.html')
# ----------------------------------------------------------------------

# Simple chatbot logic - keyword matching (REVISED WITH NLTK LOGIC)
def get_chatbot_response(message, user_name): # UPDATED SIGNATURE
    message = message.lower().strip()
    
    # --- 1. HANDLE DIRECT/SIMPLE GREETINGS ---
    simple_greetings = ['hi', 'hello', 'hey', 'hola', 'hi unibot', 'hello unibot', 'hey unibot']
    if message in simple_greetings:
        return "👋 Hello! I'm your college assistant. What can I help you with today?"
    
    # --- 2. NEW LOGIC: WHAT IS MY NAME? ---
    if 'what is my name' in message or 'my name is what' in message:
        # Returns the full name stored in local storage
        return f"Your name is **{user_name}**. How can I help you, {user_name.split(' ')[0].capitalize()}?" 

    # --- 3. INTENT MATCHING ---
    if 'timetable' in message or 'schedule' in message or 'class' in message:
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        for day in days:
            if day in message:
                entries = Timetable.query.filter_by(day=day.capitalize()).all()
                if entries:
                    response = f"📅 Timetable for {day.capitalize()}:\n\n"
                    for e in entries:
                        response += f"• {e.subject} - {e.time}\n"
                    return response
                return f"No classes scheduled for {day.capitalize()}"
        return "Please specify a day! Try: 'timetable for Monday' or 'show Tuesday schedule'"

    if 'exam' in message or 'test' in message:
        exams = ExamSchedule.query.all()
        if exams:
            response = "📝 Upcoming Exams:\n\n"
            for e in exams:
                response += f"• {e.subject} - {e.exam_date}\n"
            return response
        return "No upcoming exams scheduled"
        
    if 'staff' in message or 'contact' in message or 'professor' in message or 'teacher' in message:
        dept = None
        if 'math' in message:
            dept = 'Mathematics'
        elif 'physics' in message:
            dept = 'Physics'
        elif 'chemistry' in message:
            dept = 'Chemistry'
        elif 'cs' in message or 'computer' in message:
            dept = 'Computer Science'
        staff = StaffContact.query.filter_by(department=dept).all() if dept else StaffContact.query.all()
        if staff:
            response = "👨‍🏫 Staff Contacts:\n\n"
            for s in staff:
                response += f"• {s.name} ({s.department})\n📧 {s.email}\n"
                if s.phone:
                    response += f"📞 {s.phone}\n"
                response += "\n"
            return response
        return "No staff contacts found"

    if 'link' in message or 'website' in message or 'portal' in message:
        response = "🔗 College Links:\n\n"
        for name, url in COLLEGE_LINKS.items():
            response += f"• {name.capitalize()}: {url}\n"
        return response

    if 'event' in message or 'fest' in message or 'workshop' in message:
        events = CollegeEvent.query.all()
        if events:
            response = "🎉 Upcoming College Events:\n\n"
            for e in events:
                response += f"📌 {e.title} - {e.date}\n{e.description}\n\n"
            return response
        return "No upcoming events found."

    # --- 4. FALLBACK FOR COMPLEX GREETINGS ---
    if any(word in message for word in ['hi', 'hello', 'hey', 'hola']):
        return "👋 Hello! I heard you say hello. Please ask a direct question like 'timetable for Monday' or 'show exams'."
        
    # --- 5. DEFAULT RESPONSE ---
    return ("I can help you with:\n"
            "• Timetable (try: 'timetable for Monday')\n"
            "• Exam schedules (try: 'show exams')\n"
            "• Staff contacts (try: 'staff contacts')\n"
            "• Website links (try: 'college links')\n"
            "• Events (try: 'college events')\n\n"
            "What would you like to know?")

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        user_name = data.get('name', 'Student') # GET NAME FROM FRONTEND
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
            
        # PASS THE NAME TO THE CHATBOT FUNCTION
        response = get_chatbot_response(user_message, user_name) 
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": "Something went wrong"}), 500

@app.route('/api/timetable', methods=['GET'])
def get_timetable():
    day = request.args.get('day')
    entries = Timetable.query.filter_by(day=day.capitalize()).all() if day else Timetable.query.all()
    return jsonify([{"day": e.day, "subject": e.subject, "time": e.time} for e in entries])

@app.route('/api/exams', methods=['GET'])
def get_exams():
    exams = ExamSchedule.query.all()
    return jsonify([{"subject": e.subject, "exam_date": e.exam_date} for e in exams])

@app.route('/api/staff', methods=['GET'])
def get_staff():
    staff = StaffContact.query.all()
    return jsonify([{"name": s.name, "department": s.department, "email": s.email, "phone": s.phone} for s in staff])

@app.route('/api/events', methods=['GET'])
def get_events():
    events = CollegeEvent.query.all()
    return jsonify([{"title": e.title, "date": e.date, "description": e.description} for e in events])


def init_db():
    with app.app_context():
        # ... (Database initialization code remains unchanged)
        db.drop_all()
        db.create_all()

        # Insert sample data (Timetable, Exams, Staff, Events)
        # ... (omitted for brevity, but this is where your 2025 dates are inserted)
        
        db.session.commit()
        print("Database initialized with sample data!")

if __name__ == '__main__':
    # --- LOCAL FIX FOR "CANNOT GET /CHAT" ERROR ---
    # This ensures local testing works correctly. 
    # It must NOT be commented out for local testing.
    with app.app_context():
        # Ensure static folder is recognized for local routes:
        app.static_url_path = '/static'
    # -----------------------------------------------
    
    # init_db() is still commented out for server deployment
    app.run(debug=True, port=5000)



