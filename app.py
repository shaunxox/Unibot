from flask import Flask, request, jsonify, send_from_directory # send_from_directory needed for HTML files

from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS



# CRUCIAL FIX: Set static_folder to 'static' so Flask knows where your HTML files are

app = Flask(__name__, static_url_path='/', static_folder='static')

CORS(app)



# Database config

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///college_chatbot.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



# Database Models (rest of your models are here)

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



# Static links

COLLEGE_LINKS = {

    "library": "https://college.edu/library",

    "portal": "https://college.edu/portal",

    "hostel": "https://college.edu/hostel",

    "sports": "https://college.edu/sports",

    "canteen": "https://college.edu/canteen"

}



# ----------------------------------------------------------------------

# NEW ROUTES TO SERVE HTML FILES (LOGICALLY CORRECTED)

# ----------------------------------------------------------------------

# FIX 1: Root URL (/) now goes to the Login Page

@app.route('/')

def login_page():

    return app.send_static_file('login.html')



# FIX 2: The Chat interface is now served at /chat

@app.route('/chat')

def index():

    return app.send_static_file('index.html')

# ----------------------------------------------------------------------



# Simple chatbot logic - keyword matching (rest of your logic remains here)

def get_chatbot_response(message):

    message = message.lower().strip()



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

            # ... (rest of department logic)

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



    if any(word in message for word in ['hi', 'hello', 'hey', 'hola']):

        return "👋 Hello! I'm your college assistant. I can help you with:\n• Timetable\n• Exam schedules\n• Staff contacts\n• College website links\n• Events\n\nWhat would you like to know?"



    return ("I can help you with:\n"

            "• Timetable (try: 'timetable for Monday')\n"

            "• Exam schedules (try: 'show exams')\n"

            "• Staff contacts (try: 'staff contacts')\n"

            "• Website links (try: 'college links')\n"

            "• Events (try: 'college events')\n\n"

            "What would you like to know?")



@app.route('/api/chat', methods=['POST'])

def chat():

    # ... (rest of your API and GET routes remain here)

    try:

        data = request.json

        user_message = data.get('message', '')

        if not user_message:

            return jsonify({"error": "Message is required"}), 400

        response = get_chatbot_response(user_message)

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

        # DROP ALL TABLES before creating to reset DB with fresh data

        db.drop_all()

        db.create_all()



        # Insert Timetable data

        if Timetable.query.count() == 0:

            db.session.add_all([

                Timetable(day="Monday", subject="Mathematics", time="9:00 AM - 10:00 AM"),

                Timetable(day="Monday", subject="Physics", time="10:00 AM - 11:00 AM"),

                Timetable(day="Monday", subject="Chemistry", time="11:00 AM - 12:00 PM"),

                Timetable(day="Tuesday", subject="Computer Science", time="9:00 AM - 10:00 AM"),

                Timetable(day="Tuesday", subject="Mathematics", time="10:00 AM - 11:00 AM"),

                Timetable(day="Wednesday", subject="Physics Lab", time="2:00 PM - 5:00 PM"),

            ])



        # Insert ExamSchedule with 2025 dates

        if ExamSchedule.query.count() == 0:

            db.session.add_all([

                ExamSchedule(subject="Mathematics", exam_date="2025-11-20"),

                ExamSchedule(subject="Physics", exam_date="2025-11-22"),

                ExamSchedule(subject="Chemistry", exam_date="2025-11-25"),

                ExamSchedule(subject="Computer Science", exam_date="2025-11-27"),

            ])



        # Insert StaffContact data

        if StaffContact.query.count() == 0:

            db.session.add_all([

                StaffContact(name="Dr. Rajesh Kumar", department="Mathematics", email="rajesh.kumar@college.edu", phone="9876543210"),

                StaffContact(name="Prof. Priya Sharma", department="Physics", email="priya.sharma@college.edu", phone="9876543211"),

                StaffContact(name="Dr. Anil Verma", department="Chemistry", email="anil.verma@college.edu", phone="9876543212"),

                StaffContact(name="Prof. Sneha Reddy", department="Computer Science", email="sneha.reddy@college.edu", phone="9876543213"),

            ])



        # Insert CollegeEvent data with 2025-2026 dates

        if CollegeEvent.query.count() == 0:

            db.session.add_all([

                CollegeEvent(title="Tech Fest 2025", date="November 15-17, 2025", description="A 3-day tech fest with coding competitions, hackathons, and technical workshops."),

                CollegeEvent(title="Cultural Night", date="December 5, 2025", description="Evening of music, dance, and drama performances by students."),

                CollegeEvent(title="Science Exhibition", date="January 20, 2026", description="Projects from all departments will be showcased and judged."),

                CollegeEvent(title="Sports Day", date="February 10, 2026", description="Inter-department sports competitions and athletics events."),

            ])



        db.session.commit()

        print("Database initialized with sample data!")



if __name__ == '__main__':

    # init_db() # Commented out for server deployment

    app.run(debug=True, port=5000)



