#!/usr/bin/env python3
"""
Simple MQTT Logger - Displays all MQTT traffic from a public broker
"""

import sys
import subprocess
import importlib
import argparse
from datetime import datetime

def install_paho_mqtt():
    """Install paho-mqtt if not available"""
    try:
        importlib.import_module('paho.mqtt.client')
        print("✓ paho-mqtt is already installed")
    except ImportError:
        print("Installing paho-mqtt...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'paho-mqtt'])
            print("✓ Successfully installed paho-mqtt")
        except subprocess.CalledProcessError:
            print("✗ Failed to install paho-mqtt")
            sys.exit(1)

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when connected to broker"""
    if rc == 0:
        print("✓ Connected to MQTT broker")
        client.subscribe("#")
        print("✓ Subscribed to all topics (#)")
        print("-" * 60)
    else:
        print(f"✗ Failed to connect, return code: {rc}")

def on_message(client, userdata, msg):
    """Callback for when a message is received"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Decode payload
    if isinstance(msg.payload, bytes):
        try:
            payload = msg.payload.decode('utf-8')
        except UnicodeDecodeError:
            payload = f"[Binary data: {len(msg.payload)} bytes]"
    else:
        payload = msg.payload
    
    # Display message
    print(f"[{timestamp}]")
    print(f"Topic: {msg.topic}")
    print(f"QoS: {msg.qos}, Retained: {msg.retain}")
    print(f"Payload: {payload}")
    print("-" * 60)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple MQTT Logger - Display all MQTT traffic')
    parser.add_argument('-broker', required=True, help='MQTT broker IP address')
    parser.add_argument('-log', required=True, help='Log file path')
    parser.add_argument('-port', type=int, default=1883, help='MQTT broker port (default: 1883)')
    
    args = parser.parse_args()
    
    # Install required library
    install_paho_mqtt()
    import paho.mqtt.client as mqtt
    
    # Setup log file
    log_file = open(args.log, 'a', encoding='utf-8')
    
    def log_to_file(msg):
        """Write message to log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Topic: {msg.topic}, QoS: {msg.qos}, Retained: {msg.retain}, Payload: {msg.payload}\n"
        log_file.write(log_entry)
        log_file.flush()
    
    def on_message_with_log(client, userdata, msg):
        """Callback that both displays and logs messages"""
        on_message(client, userdata, msg)
        log_to_file(msg)
    
    # Create MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    
    # Set callback functions
    client.on_connect = on_connect
    client.on_message = on_message_with_log
    
    try:
        # Connect to broker
        print(f"Connecting to MQTT broker at {args.broker}:{args.port}...")
        client.connect(args.broker, args.port, 60)
        
        # Start listening
        print("Listening for MQTT messages...")
        print("Press Ctrl+C to stop\n")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        client.disconnect()
        log_file.close()
        print("Stopped")
    except Exception as e:
        print(f"Error: {e}")
        log_file.close()
        sys.exit(1)

if __name__ == "__main__":
    main()
