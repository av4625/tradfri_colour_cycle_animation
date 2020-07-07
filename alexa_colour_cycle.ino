#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Switch.h>
#include <upnpBroadcastResponder.h>

// Network details
const char ssid[] = "";
const char wifi_password[] = "";

// MQTT server IP
const char mqtt_server[] = "";
// The topic name for your switches
const char mqtt_rainbow_cycle_topic[] = "rainbow_cycle";
const char mqtt_colour_cycle_topic[] = "colour_cycle";
const char mqtt_colour_cycle_slow_topic[] = "colour_cycle_slow";
// MQTT Username and Password
const char mqtt_username[] = "";
const char mqtt_password[] = "";
const char mqtt_client_id[] = "colour_cycle";

WiFiClient wifi_client;
PubSubClient client(mqtt_server, 1883, wifi_client);

UpnpBroadcastResponder upnp;

Switch *rainbow_cycle = NULL;
Switch *colour_cycle = NULL;
Switch *colour_cycle_slow = NULL;

void setup()
{
    Serial.begin(115200);

    connect_wifi();
    connect_to_mqtt();

    upnp.beginUdpMulticast();

    // Define your switches here. Max 10
    // Format: Alexa invocation name, local port no, on callback, off callback
    rainbow_cycle = new Switch(
        "Rainbow Cycle", 80, rainbow_cycle_on, rainbow_cycle_off);
    colour_cycle = new Switch(
        "Colour Cycle", 81, colour_cycle_on, colour_cycle_off);
    colour_cycle_slow = new Switch(
        "Colour Cycle Slow", 82, colour_cycle_slow_on, colour_cycle_slow_off);

    upnp.addDevice(*rainbow_cycle);
    upnp.addDevice(*colour_cycle);
    upnp.addDevice(*colour_cycle_slow);
}

void loop()
{
    upnp.serverLoop();

    rainbow_cycle->serverLoop();
    colour_cycle->serverLoop();
    colour_cycle_slow->serverLoop();

    client.loop();
}

bool rainbow_cycle_on()
{
    client.publish(mqtt_rainbow_cycle_topic, "on", false);
    return true;
}

bool rainbow_cycle_off()
{
    client.publish(mqtt_rainbow_cycle_topic, "off", false);
    return false;
}

bool colour_cycle_on()
{
    client.publish(mqtt_colour_cycle_topic, "on", false);
    return true;
}

bool colour_cycle_off()
{
    client.publish(mqtt_colour_cycle_topic, "off", false);
    return false;
}

bool colour_cycle_slow_on()
{
    client.publish(mqtt_colour_cycle_slow_topic, "on", false);
    return true;
}

bool colour_cycle_slow_off()
{
    client.publish(mqtt_colour_cycle_slow_topic, "off", false);
    return false;
}

void connect_wifi()
{
    WiFi.persistent(false);
    WiFi.disconnect();
    WiFi.mode(WIFI_STA);

    // Connect to the network
    WiFi.begin(ssid, wifi_password);
    Serial.println("Connecting to WiFi");

    int retry_count = 0;

    while (WiFi.status() != WL_CONNECTED && retry_count < 15)
    {
        delay(1000);
        retry_count++;
        Serial.print(".");
    }

    if (WiFi.status() != WL_CONNECTED)
    {
        ESP.restart();
    }

    Serial.println("");
}

void connect_to_mqtt()
{
    int retry_count = 0;

    while (!client.connected() && retry_count < 15)
    {
        // Connect to MQTT broker
        if (client.connect(mqtt_client_id, mqtt_username, mqtt_password))
        {
            Serial.println("Connected to MQTT Broker!");
        }
        else
        {
            Serial.println("Connection to MQTT Broker failed...");
            Serial.print(client.state());
            retry_count++;
            delay(1000);
        }
    }

    if (!client.connected())
    {
        ESP.restart();
    }
}
