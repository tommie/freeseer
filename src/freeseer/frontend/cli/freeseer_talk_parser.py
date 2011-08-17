#!/usr/bin/python
# -*- coding: utf-8 -*-

# freeseer - vga/presentation capture software
#
#  Copyright (C) 2011  Free and Open Source Software Learning Centre
#  http://fosslc.org
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# For support, questions, suggestions or any other inquiries, visit:
# http://wiki.github.com/fosslc/freeseer/


import argparse

import sys,os
import re
import freeseer.framework.presentation



from freeseer.framework.core import FreeseerCore
from freeseer.framework.presentation import Presentation


class FreeSeerTalkParser(argparse.ArgumentParser):
    def __init__(self):  
        argparse.ArgumentParser.__init__(self)
        
        self.core = FreeseerCore(self)     
        self.db_connector = self.core.db  
        
        self.add_argument('mode',nargs = '+', metavar='talk mode')
        
        self.add_argument('--all', dest='remove_all', action='store_const',const=True, default=False)    
        self.add_argument('-e', dest='event',nargs = '+',type=str)
        self.add_argument('-p', dest='presentation',type=str)
        self.add_argument('-r', dest='room',nargs = '+',type=str)
        
    def analyse_command(self, command):  
        '''
        Analyses the command typed by the user
        '''        
        try:
            namespace = self.parse_args(command.split())
        except:
            print "*** Syntax Error"
            return
        
        mode = self._get_mode(namespace.mode) 
        
        if(mode == "show events"):
            self.show_all_events()
            
        elif(mode == "show talks"):
            self.show_all_talks()
            
        elif(mode == "show talk"):
            #TODO Search how to get arguments with space
            if(namespace.presentation == None and namespace.event == None and namespace.room == None):
                print "*** Error: Please specify the talk id, the talk event or the talk room you want to filter"
            elif(self._get_number_of_args(namespace) > 1):
                print "*** Error: Please provide only one filter"
            elif(namespace.presentation):
                self.show_talk_by_id(namespace.presentation)    
            elif(namespace.event):
                self.show_talk_by_event(self._get_mode(namespace.event))
            elif(namespace.room):
                self.show_talk_by_room(self._get_mode(namespace.room))
                                   
        elif(mode == "remove talk"):            
            if(namespace.presentation == None and namespace.remove_all == None):
                print "*** Error: Please specify the talk id or the -all argument"
            else:  
                if(namespace.presentation != None and namespace.remove_all):
                    print "*** Error: Please specify only one option"
                else:
                    if(namespace.presentation):
                        self.remove_talk(namespace.presentation)
                    elif namespace.remove_all:
                        self.clear_database()   
                                             
        elif(mode == "add talk"):
            self.add_talk_by_prompt()


        elif(mode == "update"):
            self.update_talk_by_prompt(namespace.presentation)               
                
        else:
            print "*** Unknown mode, please type one of the available modes or type 'help talk' to see all available modes"
            
            
    def show_all_events(self):
        print "---------------------------------- Events -----------------------------------"
        for event in self.db_connector.get_talk_events():
            if(len(event)>0):
                print event;
        print "-----------------------------------------------------------------------------"
        
    def show_all_talks(self):
        print "---------------------------------- Talks ------------------------------------"
        count = 1
        for talk_data in self.db_connector.get_talk_titles():
            print "Talk #" + unicode(count)
            print "Talk Id: " + unicode(talk_data[5])
            print "Talk Title: " + unicode(talk_data[1])
            print "Talk Speaker: " + unicode(talk_data[0])
            print "#########################################################################"
            count+=1
        print "-----------------------------------------------------------------------------\n"
        
    def show_talk_by_id(self, id):
        if not int(id) in self.db_connector.get_talks_ids():
            print "There's no such presentation"
            return
        
        print "---------------------------------- Talk -------------------------------------"
        for talk_data in self.db_connector.get_talk_titles():
            if str(talk_data[5]) == str(id):         
                print "#########################################################################"  
                print "Talk Title: " + unicode(talk_data[1])
                print "Talk Speaker: " + unicode(talk_data[0])
                print "Talk Room: " + unicode(talk_data[2])
                print "Talk Event " + unicode(talk_data[3])
                print "#########################################################################"
                
    def show_talk_by_event(self, event):
        if not unicode(event) in self.db_connector.get_talk_events():
            print "There's no such presentations"
            return
        
        print "---------------------------------- Talk(s) -------------------------------------"
        for talk_data in self.db_connector.get_talk_titles():
            if unicode(talk_data[3]) == unicode(event):         
                print "Talk Title: " + unicode(talk_data[1])
                print "Talk Speaker: " + unicode(talk_data[0])
                print "Talk Room: " + unicode(talk_data[2])
                print "Talk Event " + unicode(talk_data[3])
                print "#########################################################################"
                
    def show_talk_by_room(self, room):
        if not unicode(room) in self.db_connector.get_talk_rooms():
            print "There's no such presentations"
            return
        
        print "---------------------------------- Talk(s) -------------------------------------"
        for talk_data in self.db_connector.get_talk_titles():
            if unicode(talk_data[2]) == unicode(room):         
                print "Talk Title: " + unicode(talk_data[1])
                print "Talk Speaker: " + unicode(talk_data[0])
                print "Talk Room: " + unicode(talk_data[2])
                print "Talk Event " + unicode(talk_data[3])
                print "#########################################################################"
        
      
                
    def remove_talk(self, id):
        if int(id) in self.db_connector.get_talks_ids():
            self.show_talk_by_id(id)
            answer = raw_input("This will remove this presentation.Continue? (yes/no) ")
            
            while answer != "yes" and answer != "no":
                answer = raw_input("Please provide an available answer.Do you want to remove this presentation? (yes/no) ")
            else:
                if answer == "yes":
                    self.db_connector.delete_talk(id)
        else:
            print "There's no such presentation"
            
    def remove_all_talks(self):
        answer = raw_input("WARNING: This will remove ALL presentations.Continue? (yes/no) ")
        
        while answer != "yes" and answer != "no":
            answer = raw_input("Please provide an available answer.Do you want to remove ALL presentations? (yes/no) ")
        
        if answer == "yes":
                self.db_connector.clear_database()
           
    def add_talk_by_prompt(self):
        print "------------------------------ Adding a Talk -------------------------------\n"
        presentation = Presentation("")
        
        presentation.title = raw_input("Type the presentation title or press <ENTER> to pass: ")
        presentation.speaker = raw_input("Type the presentation speaker or press <ENTER> to pass: ")
        presentation.description = raw_input("Type the presentation description or press <ENTER> to pass: ")
        presentation.level = raw_input("Type the speaker level or press <ENTER> to pass: ")
        presentation.event = raw_input("Type the event that held the presentation or press <ENTER> to pass: ")
        presentation.room = raw_input("Type the room where the presentation will be performed or press <ENTER> to pass: ")        
        data = raw_input("Type the presentation time (format: dd/MM/yyyy HH:mm) or press <ENTER> to pass: ")
        
        while(not self._is_date_format(data)):
            if(len(data) > 0):
                data = raw_input("Wrong date format, please type the presentation time (format: dd/MM/yyyy HH:mm) or press <ENTER> to pass: ")
            else:
                break
             
        if not self.db_connector.db_contains(presentation):
            self.db_connector.add_talk(presentation)
            print "###################### Talk Added ############################"
        else:
            print "############### Error: Talk Already Exists ###################"

    def update_talk_by_prompt(self, id):        
        print "#### You have choose to edit the following talk ###"
        for talk_data in self.db_connector.get_talk_titles():            
            if str(talk_data[5])  == str(id): 
                title = unicode(talk_data[1])
                speaker = unicode(talk_data[0])
                room = unicode(talk_data[2])
                event = unicode(talk_data[3])
                talk_id = unicode(talk_data[5])
                print "#########################################################################"  
                print "Talk Title: " + title
                print "Talk Speaker: " + speaker
                print "Talk Room: " + room
                print "Talk Event " + event
                print "#########################################################################"              
                
                   
                   
        new_title = raw_input("Type the new presentation title (<ENTER> to keep old data): ")
        if(len(new_title) > 0):
            title = new_title
            
        new_speaker = raw_input("Type the new presentation speaker (<ENTER> to keep old data): ")
        if(len(new_speaker) > 0):
            speaker = new_speaker
            
        new_event = raw_input("Type the new event that held the presentation (<ENTER> to keep old data): ")
        if(len(new_event) > 0):
            event = new_event
            
        new_room = raw_input("Type the new room where the presentation will be performed (<ENTER> to keep old data): ")  
        if(len(new_room) > 0):
            room = new_room
            
        new_presentation = Presentation("")
        
        new_presentation.talk_id = talk_id
        new_presentation.title = new_title
        new_presentation.speaker = new_speaker
        new_presentation.event = new_event
        new_presentation.room = new_room
        
        self.db_connector.update_talk(talk_id, speaker, title, room, event, "")
        
        print "### Talk Updated! ###"
        
    def _is_date_format(self, value):
        if(re.match("[0-3][0-9]/[0-1][0-9]/[0-9][0-9][0-9][0-9] [0-2][0-9]:[0-5][0-9]", value)):
            return True
        return False
    
    def _get_mode(self, mode_list):
        mode = ""
        for item in mode_list:
            mode += item + " "
        return mode[0:len(mode)-1]
    
    def _get_number_of_args(self, namespace):
        count = 0
        if(namespace.event):
            count+=1
        if(namespace.presentation):
            count+=1
        if(namespace.room):
            count+=1
        
        return count

                
            
        
             
    
