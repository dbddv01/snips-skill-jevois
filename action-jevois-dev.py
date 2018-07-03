#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import io

from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import json
import serial


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"


global sentence


class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in+ self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()
    
# Init


MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))


INTENT_START_SKILL = "dbddv01:open_eyes"
INTENT_ANSWER_YES = "dbddv01:answer_yes"
INTENT_ANSWER_NO = "dbddv01:answer_no"
INTENT_INTERRUPT = "dbddv01:stop_cam"
#INTENT_DOES_NOT_KNOW = "dbddv01:does_not_know"

INTENT_FILTER_GET_ANSWER = [
    INTENT_ANSWER_YES,
    INTENT_ANSWER_NO,
    INTENT_INTERRUPT,
    ]

def launch_jevois(hermes, session_id):
    
    # Opens the serial over usb bus during 2 seconds
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
    serial_line = ""
       
    # Read the incoming serial messages and close the interface to prevent any deadlock      
    serial_line = ser.readline()
    msg_jevois_string = str(serial_line)
    #print(msg_jevois_string)
    ser.close()
    
    # Analyse msg from serial and give answer               
    if msg_jevois_string[0:6] == "FD0OO:":
            sentence = "Je vois un visage que je ne reconnais pas ?"
            hermes.publish_end_session(session_id, sentence)
            hermes.publish_start_session_action("default", 'Dois-je continuer mon observation ?' , INTENT_FILTER_GET_ANSWER, True, "" )
    
    elif msg_jevois_string[0:6] == "FD020:":
            msg_jevois_nom = msg_jevois_string[6:]
            sentence = "Sans certitude, je vois un visage semblable à  " + msg_jevois_nom
            hermes.publish_end_session(session_id, sentence)
            hermes.publish_start_session_action("default", 'Dois-je continuer mon observation ?' , INTENT_FILTER_GET_ANSWER, True, "" )
    elif msg_jevois_string[0:6] == "FD010:":
            msg_jevois_nom = msg_jevois_string[6:]
            sentence = "Je pense vous avoir identifié. Bonjour " + msg_jevois_nom + "."
            hermes.publish_end_session(session_id, sentence)
            hermes.publish_start_session_action("default", 'Dois-je continuer mon observation ?', INTENT_FILTER_GET_ANSWER, True,"")
    else:
        sentence = "Je ne perçois aucun visage en ce moment... "
        hermes.publish_end_session(session_id, sentence)
        hermes.publish_start_session_action("default", 'Puis-je continuer à observer ?', INTENT_FILTER_GET_ANSWER, True,"")


def user_request_open_eyes(hermes, intent_message):
       
        session_id = intent_message.session_id
    
        launch_jevois(hermes, session_id)
             
        
def user_interrupt(hermes, intent_message):
    #User wants to quit
        
        session_id = intent_message.session_id
        
        sentence = " Ok à la session est terminée"
        
        #hermes.publish_end_session(session_id, sentence)
        

def user_gives_answer_yes(hermes, intent_message):
        
        session_id = intent_message.session_id
                
        launch_jevois(hermes, session_id)
			
	

def user_gives_answer_no(hermes, intent_message):
    
        session_id = intent_message.session_id
        
        sentence = " Ok à prochaine fois"
			
	#hermes.publish_end_session(session_id, sentence)

def session_started(hermes, session_started_message):
   

    session_id = session_started_message.session_id
    
	    
if __name__ == "__main__":
  
   
  with Hermes(MQTT_ADDR) as h:

    h.subscribe_intent(INTENT_START_SKILL, user_request_open_eyes) \
        .subscribe_intent(INTENT_INTERRUPT, user_interrupt) \
        .subscribe_intent(INTENT_ANSWER_YES, user_gives_answer_yes) \
        .subscribe_intent(INTENT_ANSWER_NO, user_gives_answer_no) \
        .subscribe_session_started(session_started) \
	.start()
  
  
  

  
      
	

    