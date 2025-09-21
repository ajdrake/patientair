from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import time
import json

app = Flask(__name__)

# Twilio configuration
account_sid = 'replace with'
auth_token = 'replace with auth token'
client = Client(account_sid, auth_token)
from_number = 'whatsapp:+14155238886'

# User session storage (in production, use a database)
user_sessions = {}

class PregnancyHealthBot:
    def __init__(self):
        self.stages = {
            'start': self.handle_start,
            'name': self.handle_name,
            'menstrual_period': self.handle_menstrual_period,
            'address': self.handle_address,
            'ac_purifier': self.handle_ac_purifier,
            'job': self.handle_job,
            'job_title': self.handle_job_title,
            'feet_time': self.handle_feet_time,
            'outside_time': self.handle_outside_time,
            'health_questions': self.handle_health_questions,
            'onboarding_complete': self.handle_onboarding_complete,
            'first_alert': self.handle_first_alert,
            'wellbeing_check_1': self.handle_wellbeing_check_1,
            'location_check': self.handle_location_check,
            'travel_plans': self.handle_travel_plans,
            'symptom_check_2': self.handle_symptom_check_2,
            'emergency_response': self.handle_emergency_response,
            'hospital_response': self.handle_hospital_response
        }
    
    def send_message(self, to_number, message):
        """Send WhatsApp message via Twilio"""
        try:
            message = client.messages.create(
                from_=from_number,
                body=message,
                to=to_number
            )
            return message.sid
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def get_user_session(self, phone_number):
        """Get or create user session"""
        if phone_number not in user_sessions:
            user_sessions[phone_number] = {
                'stage': 'start',
                'data': {},
                'last_activity': time.time()
            }
        return user_sessions[phone_number]
    
    def handle_start(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['stage'] = 'name'
        return "Hey there, what is your full name?"
    
    def handle_name(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['name'] = message_body
        session['stage'] = 'menstrual_period'
        return "When was your last menstrual period?"
    
    def handle_menstrual_period(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['menstrual_period'] = message_body
        session['stage'] = 'address'
        return "I am now going to ask you some questions to help you get onboarded to our system to deliver personalized alerts. What is your home address?"
    
    def handle_address(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['address'] = message_body
        session['stage'] = 'ac_purifier'
        return "Do you have an AC in your house (Y/N)?"
    
    def handle_ac_purifier(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['ac_purifier'] = message_body
        session['stage'] = 'job'
        return "Do you have a job?"
    
    def handle_job(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['has_job'] = message_body
        if message_body.lower() in ['yes', 'y']:
            session['stage'] = 'job_title'
            return "May I know your job title?"
        else:
            session['stage'] = 'feet_time'
            return "How often are you on your feet?"
    
    def handle_job_title(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['job_title'] = message_body
        session['stage'] = 'feet_time'
        return "How often are you on your feet?"
    
    def handle_feet_time(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['feet_time'] = message_body
        session['stage'] = 'outside_time'
        return "How many hours on average are you outside?"
    
    def handle_outside_time(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['outside_time'] = message_body
        session['stage'] = 'health_questions'
        return "Now I will ask you some health-related questions. Is this your first pregnancy?"
    
    # How old are you?
    #  Do you have diabetes (Y/N)? Do you have hypertension (Y/N)?
    #
    def handle_health_questions(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['health_info'] = message_body
        session['stage'] = 'onboarding_complete'
        return "Perfect, thank you so much. If the air quality and heat near your home is unusually high we will send you an alert along with some recommendations."
    
    def handle_onboarding_complete(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['stage'] = 'first_alert'
        # Schedule alert to be sent in 5 seconds
        import threading
        timer = threading.Timer(7.0, self.send_first_alert, args=[phone_number])
        timer.start()
        return "Great! You're all set up. I'll monitor air quality and temperature in your area."

    def send_first_alert(self, phone_number):
        """Send first environmental alert"""
        name = user_sessions[phone_number]['data'].get('name', 'there').split()[0]
        message = f"Hey {name}, the AQI near your home is 100 and the temperature is 35°C, which is considered an extreme heat day. If you can avoid going out please do so, if you must go out please wear a mask."
        self.send_message(phone_number, message)
        user_sessions[phone_number]['stage'] = 'wellbeing_check_1'
    
    def handle_first_alert(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['stage'] = 'wellbeing_check_1'
        return "I will now ask some questions to check on your well-being. Have you felt shortness of breath recently (1-10)? Do you feel dizzy (1-10)? Do you have contractions (Y/N)?"
    
    # separate out into separate questions
    ## 
    def handle_wellbeing_check_1(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['wellbeing_1'] = message_body
        session['stage'] = 'location_check'
        return "May I know your current location so I can recommend cooling centers nearby?"
    
    def handle_location_check(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['current_location'] = message_body
        session['stage'] = 'travel_plans'
        return "Here is a cooling center nearby just in case: 2134567 LA. Do you plan on travelling anywhere today?"
    
    def handle_travel_plans(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['travel_plans'] = message_body
        if 'supermarket' in message_body.lower() or 'yes' in message_body.lower():
            response = "There is a cooling center near the supermarket at 456 LA Cooling Center (1 min walk away) and a clinic you can go to at 4561 LA Cooling Center (5 min walk away)."
        else:
            response = "Okay, stay safe and indoors when possible."
        session['stage'] = 'symptom_check_2'
        return response
    
    def send_second_symptom_check(self, phone_number):
        """Send follow-up symptom check"""
        name = user_sessions[phone_number]['data'].get('name', 'there').split()[0]
        message = f"A couple of hours have passed. Hey {name}, could you answer these questions please? Have you felt shortness of breath recently (1-10)? Do you feel dizzy (1-10)? Do you have contractions (Y/N)?"
        self.send_message(phone_number, message)
        user_sessions[phone_number]['stage'] = 'symptom_check_2'
    
    def handle_symptom_check_2(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['wellbeing_2'] = message_body
        
        # Check for worsening symptoms (simplified logic)
        if any(word in message_body.lower() for word in ['6', '7', '8', '9', '10', 'high', 'bad']):
            session['stage'] = 'emergency_response'
            name = session['data'].get('name', 'there').split()[0]
            return f"Hey {name}, please contact your physician at +1 (646) 271-8965. May I know your current location so I can recommend a healthcare center to go to?"
        else:
            return "Your symptoms seem stable. Continue to monitor and stay indoors."
    
    def handle_emergency_response(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['emergency_location'] = message_body
        session['stage'] = 'hospital_response'
        return "Here is the nearest hospital that can manage your symptoms: 567 LA Hospital (30 min car ride away). Should I call an ambulance for you (Y/N)?"
    
    def handle_hospital_response(self, phone_number, message_body):
        session = self.get_user_session(phone_number)
        session['data']['ambulance_response'] = message_body
        
        if message_body.lower() in ['yes', 'y']:
            return "Calling ambulance now. Stay calm and wait for medical assistance."
        else:
            return "Please go to the hospital as soon as you can. We have updated your EHR with your current symptoms."
    
    def process_message(self, phone_number, message_body):
        """Main message processing function"""
        session = self.get_user_session(phone_number)
        current_stage = session['stage']
        
        if current_stage in self.stages:
            response = self.stages[current_stage](phone_number, message_body)
            session['last_activity'] = time.time()
            return response
        else:
            return "I'm sorry, I didn't understand. Could you please try again?"

# Initialize bot
bot = PregnancyHealthBot()

@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    
    # Process message through bot
    response_text = bot.process_message(from_number, incoming_msg)
    
    # Create TwiML response
    resp = MessagingResponse()
    resp.message(response_text)
    
    return str(resp)

@app.route('/send_alert/<phone_number>')
def send_alert(phone_number):
    """Manual trigger for sending first alert (for testing)"""
    full_number = f"whatsapp:{phone_number}"
    bot.send_first_alert(full_number)
    return "Alert sent!"

@app.route('/send_followup/<phone_number>')
def send_followup(phone_number):
    """Manual trigger for sending symptom follow-up (for testing)"""
    full_number = f"whatsapp:{phone_number}"
    bot.send_second_symptom_check(full_number)
    return "Follow-up sent!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Additional utility functions for scheduled alerts
def schedule_environmental_alerts():
    """Function to check environmental data and send alerts"""
    # This would integrate with air quality API
    # For now, manually trigger alerts for testing
    pass

def check_user_symptoms():
    """Function to periodically check on users with alerts"""
    # This would run on a schedule to follow up with users
    pass

# Example usage commands:
# Start conversation: Send "hi" to your WhatsApp bot
# Trigger alert: Visit http://localhost:5000/send_alert/+15025942457
# Trigger follow-up: Visit http://localhost:5000/send_followup/+15025942457