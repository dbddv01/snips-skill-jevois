#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import random
import sys
import serial

from hermes_python.hermes import Hermes
from hermes_python.ontology import *


CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

#global compteur
global 
global bonne_reponse
global etape_du_jeu
global sentence


class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()



MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))


INTENT_START_SKILL = "dbddv01:open_eyes"
INTENT_ANSWER_YES = "dbddv01:answer_yes"
INTENT_ANSWER_NO = "dbddv01:answer_no"
INTENT_INTERRUPT = "dbddv01:interrupt"
#INTENT_DOES_NOT_KNOW = "dbddv01:does_not_know"

INTENT_FILTER_GET_ANSWER = [
    INTENT_ANSWER_YES,
    INTENT_ANSWER_NO,
    INTENT_INTERRUPT,
    ]
# Initialisation des données

def say(hermes, text):
    hermes.publish('hermes/tts/say', json.dumps({'text': text}))


def launch_jevois(hermes):
    
    ser = serial.Serial('/dev/ttyACM0', 115200)
    
    while True:
        serial_line = ser.readline()
        msg_jevois_string = str(serial_line)
        if msg_jevois_string == "":
            sentence = "Je ne perçois aucun visage en ce moment..."
            say(hermes,sentence)
        elif msg_jevois_string[0:6] == "FD0OO:":
                sentence = "Je vois un visage que je ne reconnais pas. Eclairez votre visage face à moi, je vous prie..."
                say(hermes,sentence)
        elif msg_jevois_string[0:6] == "FD020:":
                msg_jevois_nom = msg_jevois_string[7:end]
                sentence = "Je vois un visage que je n'identifie pas correctement. Tentez d'éclairer et de vous positionner face à moi s'il vous plait"
                say(hermes,sentence)
        elif msg_jevois_string[0:6] == "FD010:":
                msg_jevois_nom = msg_jevois_string[7:end]
                sentence = "Bonjour " + msg_jevois_nom + ". Dois-je continuer le mode de reconnaissance ?"
                break
        
    return(sentence)


def user_request_open_eyes(hermes, intent_message):
       
        session_id = intent_message.session_id
    
        sentence = str(launch_jevois())
             
        hermes.publish_continue_session(intent_message.session_id, sentence, INTENT_FILTER_GET_ANSWER)
	
    
def user_gives_answer_yes(hermes, intent_message):
        
        session_id = intent_message.session_id
        
        sentence = str(launch_jevois())
			
	hermes.publish_continue_session(intent_message.session_id, sentence, INTENT_FILTER_GET_ANSWER)

def user_gives_answer_no(hermes, intent_message):
    
        session_id = intent_message.session_id
        
        sentence = " Ok à prochaine fois"
			
	hermes.publish_end_session(session_id, sentence)

def user_interrupt(hermes, intent_message):
    #User wants to quit
        
        session_id = intent_message.session_id
        
        sentence = " Ok à la session est terminée"
        
        hermes.publish_end_session(session_id, sentence)

def session_started(hermes, session_started_message):
    

   
def session_ended(hermes, session_ended_message):
    



with Hermes(MQTT_ADDR) as h:

    h.subscribe_intent(INTENT_START_SKILL, user_request_open_eyes) \
        .subscribe_intent(INTENT_INTERRUPT, user_interrupt) \
        .subscribe_intent(INTENT_ANSWER_YES, user_gives_answer_yes) \
        .subscribe_intent(INTENT_ANSWER_NO, user_gives_answer_no) \
	.subscribe_session_ended(session_ended) \
        .subscribe_session_started(session_started) \
        .start()
