# Fail-Secure Smart Locker System  

## Overview  
The **Fail-Secure Smart Locker System** is a dual-access locker designed for enhanced security and flexibility. Its features are:  
- **Fail-Secure Functionality**: Lockers remain locked during power outages.  
- **Dual Access Methods**: Users can lock/unlock lockers via a keypad or website.  
- **Secure Data Handling**: Phone numbers and passwords are stored in a database, with communication between hardware managed by ATMEGA and backend managed by the ESP8266.   
- **Scalable Architecture**: Supports up to 8 lockers using a GPIO expander.  
- **Efficient Power Usage**: Relays supply power to locks for just 0.2 seconds during operation.  

## System Architecture  
The system integrates both hardware and software components, which include:  
- **ATMega Microcontroller**: Handles keypad inputs, OLED display, and relay operations.  
- **ESP8266**: Facilitates Wi-Fi communication with the backend API.  
- **Backend API**: Manages CRUD operations for locker data. Uses FastAPI 
- **MySQL Database**: Stores locker information, including phone numbers and passwords.  
- **Relays**: Control power supply to locks.  
- **GPIO Expander**: Increases the number of relays connected to the microcontroller.  

## Hardware Components  
- **ATMega Microcontroller**  
- **ESP8266 Wi-Fi Module**  
- **4x4 Keypad**  
- **128x64 OLED Display**  
- **Electromechanical Locks**  
- **Relays**  
- **PCF8574 GPIO Expander**  

## Working  
1. **Locking via Keypad**:  
   - The user sets a 4-digit password and selects an available locker from the list displayed on the OLED.  
   - The phone number and password are sent to the ESP8266 and stored in the database via the backend API.  

2. **Locking via Website**:  
   - The user selects a locker from the dropdown and enters their phone number.  
   - A randomly generated 4-digit password is sent to the entered number and stored in the database.  

3. **Unlocking via Keypad or Website**:  
   - The user enters their phone number to retrieve a list of associated lockers.  
   - Upon selecting a locker, the stored password is fetched from the database for verification.  
   - If the password matches, the relay is triggered to unlock the locker.  
 
### Prerequisites  
- **Hardware**: ATMega, ESP8266, GPIO Expander, Relays, Electromechanical Locks, OLED Display.
- **Software**: Arduino IDE, Python FastAPI, Database (MySQL), Streamlit.  

## Future Improvements  
- **Biometric Integration**: Add fingerprint or facial recognition for enhanced security.  
- **Battery Backup**: Ensure functionality during extended power outages.  
- **Mobile App**: Develop a dedicated app for better user experience.  
