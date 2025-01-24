from twilio.rest import Client
import random
import requests



account_sid = "YOUR-ACCOUNT-SID-HERE" 
auth_token = "AUTH-TOKEN"    
twilio_phone_number = "TWILIO-PHONE-NO"  

def send_password_sms(to_number, locker_no, password):
    try:
        if(password!=None):

            client = Client(account_sid, auth_token)
            message_content= f"The password for locker {locker_no} is {password}"
           
            message = client.messages.create(
                body=message_content,
                from_=twilio_phone_number,
                to=to_number
            )
            
            print(f"Message sent. SID: {message.sid}")
            return password
            
        else:
            return None
            
        
    except Exception as e:
        print(f"Failed to send SMS: {e}")


def generate():
    password=random.randint(1000,9999)
    password=str(password)
    return password


def put_request(id, payload):
    response = requests.put(f"http://127.0.0.1:8000/lockers/{id}", json=payload)
    return response           