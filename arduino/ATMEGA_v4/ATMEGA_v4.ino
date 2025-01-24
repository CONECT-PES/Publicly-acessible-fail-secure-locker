#include <SoftwareSerial.h>
#include <Adafruit_PCF8574.h>
#include <Wire.h>
#include <Keypad.h>
#include "U8glib.h"

// OLED setup
U8GLIB_SSD1306_128X64 oled(U8G_I2C_OPT_NONE);

// Define pins for ESP8266 communication
#define rxPin 10
#define txPin 11

Adafruit_PCF8574 pcf8574;
SoftwareSerial espSerial(rxPin, txPin);

// Keypad setup
const byte ROWS = 4;
const byte COLS = 4;

char keys[ROWS][COLS] = {
    {'1', '2', '3', 'A'},
    {'4', '5', '6', 'B'},
    {'7', '8', '9', 'C'},
    {'*', '0', '#', 'D'}};

byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

char pin[5];
char phone[9];
int locker = -1;
int pinIndex = 0;
bool pinEntered = false;

int phoneIndex = 0;
bool phoneEntered = false;

void setup()
{
    Serial.begin(9600);
    espSerial.begin(9600);
    Wire.begin();
    pcf8574.begin();

    for (int i = 0; i <= 7; i++)
    {
        pcf8574.pinMode(i, OUTPUT);
        pcf8574.digitalWrite(i, HIGH);
    }

    displayMessage("Press 'A' to select\na locker, 'B' to\nunlock.");
}

void loop()
{
    char key = keypad.getKey();

    if (key)
    {
        processKey(key);
    }

    if (espSerial.available())
    {
        String request = espSerial.readStringUntil('\n');
        request.trim();

        if (request.startsWith("ACTIVATE_RELAY"))
        {
            int locker = request.substring(request.indexOf('|') + 1).toInt();
            activateRelay(locker);
        }
    }
}

void processKey(char key)
{
    if (key == 'A')
    {
        enterPassword();
    }
    else if (key == 'B')
    {
        selectUnlockLocker();
    }
}

void enterPassword()
{
    String phone = acceptPhone();
    delay(50);

    displayMessage("Select a locker:\nRequesting empty...");
    espSerial.println("GET_EMPTY_LOCKERS");

    unsigned long startMillis = millis();
    while (!espSerial.available())
    {
        if (millis() - startMillis > 10000)
        {
            displayMessage("Timeout waiting for\nESP response.");
            return;
        }
        delay(50);
    }

    if (espSerial.available() > 0)
    {
        String response = espSerial.readStringUntil("\n");
        displayMessage("Empty lockers:\n" + response);
    }

    while (true)
    {
        char l = keypad.getKey();
        if (l)
        {
            locker = l - '0';
            if (locker >= 1 && locker <= 8)
            {
                displayMessage("Locker " + String(locker) + " selected.\nEnter password.");
                setPassword(locker, phone);
                break;
            }
        }
    }
}

void setPassword(int locker, String phone)
{
    String pin = acceptInput();
    sendPayload(locker, pin, phone);
}

String acceptInput()
{
    displayMessage("Enter 4-digit PIN.\nPress C to clear.");
    pinIndex = 0;

    while (pinIndex < 4)
    {
        char key = keypad.getKey();

        if (key && key != 'A' && key != 'B')
        {
            pin[pinIndex++] = key;
            displayMessage("PIN: " + String(pin).substring(0, pinIndex));
        }

        if (key == 'C')
        {
            pinIndex = 0;
            displayMessage("Input cleared.\nEnter PIN again.");
        }
    }
    return String(pin);
}

String acceptPhone()
{
    phoneIndex = 0;
    phoneEntered = false;

    displayMessage("Enter phone number.\nPress C to reset.");

    while (phoneIndex < 10)
    {
        char key = keypad.getKey();

        if (key && key != 'A' && key != 'B' && key != 'C' && key != 'D' && key != '*' && key != '#')
        {
            phone[phoneIndex++] = key;
            displayMessage("Phone: " + String(phone).substring(0, phoneIndex));
        }

        if (key == 'C')
        {
            phoneIndex = 0;
            displayMessage("Input cleared.\nEnter phone again.");
        }
    }

    return String(phone);
}

void sendPayload(int locker, String pin, String phone)
{
    String payload = "{\"id\": " + String(locker) + ", \"phone\": \"" + phone + "\", \"password\": \"" + pin + "\"}";

    displayMessage("Payment successful! Sending payload:\n" + payload);
    delay(2000);
    espSerial.print("UPDATE_LOCKER|");
    espSerial.println(payload);
}

void selectUnlockLocker()
{
    String phone = acceptPhone();
    delay(50);
    displayMessage("Requesting locked\nlockers...");

    espSerial.print("GET_LOCKED_LOCKERS|");
    espSerial.println(phone);

    unsigned long startMillis = millis();
    while (!espSerial.available())
    {
        if (millis() - startMillis > 10000)
        {
            displayMessage("Timeout waiting\nfor ESP.");
            return;
        }
        delay(50);
    }

    if (espSerial.available() > 0)
    {
        String response = espSerial.readStringUntil("\n");
        displayMessage("Locked lockers:\n" + response);
    }

    while (true)
    {
        char l = keypad.getKey();
        if (l)
        {
            locker = l - '0';
            if (locker >= 1 && locker <= 8)
            {
                displayMessage("Locker " + String(locker) + " selected.\nEnter password.");
                inputPassword(locker);
                break;
            }
        }
    }
}

void inputPassword(int locker)
{
    String pin = acceptInput();
    checkPassword(locker, pin);
}

void checkPassword(int locker, String pin)
{
    displayMessage("Checking password...");
    espSerial.print("GET_LOCKER_PASSWORD|");
    espSerial.println(locker);

    unsigned long startMillis = millis();
    while (!espSerial.available())
    {
        if (millis() - startMillis > 10000)
        {
            displayMessage("Timeout waiting\nfor ESP.");
            return;
        }
        delay(50);
    }

    if (espSerial.available() > 0)
    {
        String response = espSerial.readStringUntil("\n");
        response.trim();
        if (response.equals(pin))
        {
            displayMessage("Password correct.\nUnlocking...");
            correctPassword(locker);
        }
        else
        {
            displayMessage("Incorrect password.");
        }
    }
}

void correctPassword(int locker)
{
    displayMessage("Unlocking locker...");
    espSerial.print("RESET|");
    espSerial.println(locker);
}

void activateRelay(int locker)
{
    pcf8574.digitalWrite(locker - 1, LOW);
    delay(1000);
    pcf8574.digitalWrite(locker - 1, HIGH);
    clearScreen();
}

void clearScreen()
{
    displayMessage("Unlocked locker");
    Serial.println("Unlocked locker message displayed.");
    delay(3000);
    displayMessage("Press 'A' to select\na locker, 'B' to\nunlock.");

}

void displayMessage(String message)
{
    oled.firstPage();
    do
    {
        oled.setFont(u8g_font_6x12);
        int y = 10;
        for (int i = 0; i < message.length(); i += 16)
        {
            oled.drawStr(0, y, message.substring(i, i + 16).c_str());
            y += 12;
        }
    } while (oled.nextPage());
}