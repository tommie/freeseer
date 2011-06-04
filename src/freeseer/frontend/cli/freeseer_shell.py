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

import cmd

class FreeSeerShell(cmd.Cmd):
    '''
    Freeseer Shell. Used to provide an interface to the CLI frontend
    '''
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "freeseer> "
        self.intro = "\nfreeseer - video recording and streaming software\n" \
        "Copyright (C) 2011  Free and Open Source Software Learning Centre\n"
        
        
    #TODO    
    def do_frecord(self, line):
        print "frecord command executed with arguments: '" + line + "'" 

    #TODO   
    def complete_frecord(self, text, line, start_index, end_index):        
        pass
  
    #TODO         
    def do_ftalk(self, line):
        print "ftalk command executed with arguments: '" + line + "'" 

    #TODO   
    def complete_ftalk(self, text, line, start_index, end_index):        
        pass
    
    #TODO          
    def do_fconfig(self, line):
        print "fconfig command executed with arguments: '" + line + "'" 

    #TODO   
    def complete_fconfig(self, text, line, start_index, end_index):        
        pass
        
    def run(self):
        self.cmdloop()