#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>
#include <SoftwareSerial.h>

// Define the software serial communication for ATmega
SoftwareSerial espSerial(4, 12);  // RX, TX

// Wi-Fi credentials
const char* ssid = "<wifi ssid>";
const char* password = "<wifi password>";

const char* baseUrl = "http://<system_ip_address>:8000/lockers/";
ESP8266WebServer server(80);

void setup() {
  Serial.begin(9600);    
  espSerial.begin(9600); 
  connectToWiFi();       
  setupWebServer();     
}

void loop() {

  server.handleClient();


  if (espSerial.available()) {
    String request = espSerial.readStringUntil('\n');
    request.trim();

    if (request == "GET_EMPTY_LOCKERS") {
      getEmptyLockers();
    }
    else if (request.startsWith("GET_LOCKED_LOCKERS"))
    {
      String phone = request.substring(request.indexOf('|') + 1);
      getLockedLockers(phone);
    }
    else if (request.startsWith("UPDATE_LOCKER")) {
      String jsonPayload = request.substring(request.indexOf('|') + 1);
      updateLocker(jsonPayload);
    }
    else if (request.startsWith("GET_LOCKER_PASSWORD")) {
      int lockerId = request.substring(request.indexOf('|') + 1).toInt();
      getPassword(lockerId);
    }
    else if (request.startsWith("RESET")) {
      int lockerId = request.substring(request.indexOf('|') + 1).toInt();
      resetIndex(lockerId);
    }
  }
}

void connectToWiFi() {
  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
  Serial.print("ESP8266 IP Address: ");
  Serial.println(WiFi.localIP());
}


void setupWebServer() 
{
  server.on("/ACTIVATE_RELAY", HTTP_GET, []() 
  {

    if (server.hasArg("id")) {

      int locker_id = server.arg("id").toInt();

      activateRelay(locker_id);

      
      server.send(200, "text/plain", "Relay request received by ESP8266.");
    } 
    else 
    {
      
      server.send(400, "text/plain", "client_id parameter is missing.");
    }
  });

  server.begin();
}

// HTTP Request to get locker status (empty or locked)
void getEmptyLockers() 
{
  if (WiFi.status() != WL_CONNECTED) 
  {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectToWiFi();
  }

  Serial.println("Requesting locker status...");
  String serverUrl = String(baseUrl) + "empty";

  WiFiClient client;
  HTTPClient http;
  http.begin(client, serverUrl);

  int httpCode = http.GET();

  if (httpCode > 0) {
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("Received payload:");
      Serial.println(payload);

      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        Serial.print(F("JSON deserialization failed: "));
        Serial.println(error.f_str());
        return;
      }

      JsonArray lockers = doc.as<JsonArray>();
      for (JsonObject locker : lockers) {
        int id = locker["id"];
        espSerial.println(id);  // Send data back to ATmega via espSerial
      }
    }
  } else {
    Serial.printf("HTTP request failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}



void getLockedLockers(String phone) 
{
  if (WiFi.status() != WL_CONNECTED) 
  {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectToWiFi();
  }

  Serial.println("Requesting locker status...");
  String serverUrl = String(baseUrl) + "locked/"+ phone;

  WiFiClient client;
  HTTPClient http;
  http.begin(client, serverUrl);

  int httpCode = http.GET();

  if (httpCode > 0) {
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println("Received payload:");
      Serial.println(payload);

      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        Serial.print(F("JSON deserialization failed: "));
        Serial.println(error.f_str());
        return;
      }

      JsonArray lockers = doc.as<JsonArray>();
      for (JsonObject locker : lockers) {
        int id = locker["id"];
        espSerial.println(id);  // Send data back to ATmega via espSerial
      }
    }
  } else {
    Serial.printf("HTTP request failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}



// HTTP PUT Request to update locker
void updateLocker(String jsonPayload) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectToWiFi();
  }

  DynamicJsonDocument doc(1024);
  deserializeJson(doc, jsonPayload);

  int lockerId = doc["id"];
  String phoneNumber = doc["phone"];

  Serial.println("Sending PUT request...");
  String serverUrl = String(baseUrl) + String(lockerId);

  doc["phone"] = phoneNumber;

  WiFiClient client;
  HTTPClient http;
  http.begin(client, serverUrl);

  http.addHeader("Content-Type", "application/json");
  String requestBody;
  serializeJson(doc, requestBody);

  int httpCode = http.PUT(requestBody);

  if (httpCode > 0) {
    if (httpCode == HTTP_CODE_OK) {
      Serial.println("Successfully updated locker info.");
    }
  } else {
    Serial.printf("HTTP request failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

// HTTP Request to get locker password
void getPassword(int lockerId) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectToWiFi();
  }

  Serial.println("Sending GET request...");
  String serverUrl = String(baseUrl) + String(lockerId);

  WiFiClient client;
  HTTPClient http;
  http.begin(client, serverUrl);

  int httpCode = http.GET();

  if (httpCode > 0) {
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();

      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        espSerial.print(F("JSON deserialization failed: "));
        espSerial.println(error.f_str());
        return;
      }

      String password = doc["password"];
      espSerial.println(password);  // Send password back to ATmega
    }
  } else {
    espSerial.printf("HTTP request failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

// HTTP DELETE request to reset locker
void resetIndex(int lockerId) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectToWiFi();
  }

  String serverUrl = String(baseUrl) + String(lockerId);

  WiFiClient client;
  HTTPClient http;
  http.begin(client, serverUrl);

  int httpCode = http.DELETE();
  espSerial.println(httpCode); // Send response code back to ATmega

  http.end();
}

// Function to activate relay
void activateRelay(int id) 
{
  espSerial.print("ACTIVATE_RELAY|");
  espSerial.println(id);
}
