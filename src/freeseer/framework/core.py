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


import codecs
import datetime
import time
import logging
import logging.config
import re
import unicodedata

from freeseer import project_info
from freeseer.backend.gstreamer import *

from config import Config
from logger import Logger
from rss_parser import *
from presentation import *

__version__= project_info.VERSION

class FreeseerCore:
    '''
    Freeseer core logic code.  Used to link a GUI frontend with a recording
    backend such as backend.gstreamer
    '''
    def __init__(self, ui):
        self.ui = ui

        # Read in config information
        configdir = os.path.abspath(os.path.expanduser('~/.freeseer/'))
        self.config = Config(configdir)
        self.logger = Logger(configdir)

        # Start Freeseer Recording Backend
        self.backend = Freeseer_gstreamer(self)

        # Find corresponding pixel resolution to name selected
        if self.config.resolution in self.config.resmap:
            res_temp = self.config.resmap[self.config.resolution]
        else:
            res_temp = self.config.resolution

        resolution = res_temp.split('x')
        self.change_output_resolution(resolution[0], resolution[1])

        self.feedback = False
        self.spaces = False

        self.logger.log.info(u"Core initialized")


    def _get_record_name(self, presentation):
        '''
        Returns the filename to use when recording.
        '''
        ts = presentation.start_time.strftime('%Y%m%dT%H%M%S')

        return '%s-%s-%s.ogg' % (
            ts,
            self._mangle_filename_part(presentation.author),
            self._mangle_filename_part(presentation.title))


    DISALLOWED_CHARACTERS = re.compile(r'[^\w_.]')


    def _mangle_filename_part(self, s):
        '''
        Return a string suitable for use in a file name.
        '''
        s = s.lower().replace(u'-', u'_').replace(u' ', u'_')
        s = self.DISALLOWED_CHARACTERS.sub(u'', s)

        return unicodedata.normalize('NFKD', s)[:32].encode('utf-8')

    ##
    ## Backend Functions
    ##
    def get_video_sources(self):
        '''
        Returns supported video sources.
        '''
        vidsrcs = self.backend.get_video_sources()
        self.logger.log.debug('Available video sources: ' + str(vidsrcs))
        return vidsrcs


    def get_video_devices(self, device_type):
        '''
        Returns available video devices.
        '''
        viddevs = self.backend.get_video_devices(device_type)
        self.logger.log.debug('Available video devices for ' + device_type + ': ' + str(viddevs))
        return viddevs


    def get_audio_sources(self):
        '''
        Returns supported audio sources.
        '''
        sndsrcs = self.backend.get_audio_sources()
        self.logger.log.debug('Available audio sources: ' + str(sndsrcs))
        return sndsrcs


    def set_video_mode(self, mode):
        '''
        Enables video recording when mode is set to True
        Disables video recording when mode is set to False
        '''
        if mode == True:
            self.logger.log.info('Video recording: ENABLED')
        else:
            self.logger.log.info('Video recording: DISABLED')

        self.backend.set_video_mode(mode)


    def change_videosrc(self, vid_source, vid_device):
        '''
        Informs backend of new video source to use when recording.
        '''
        self.backend.change_video_source(vid_source, vid_device)
        self.logger.log.debug('Video source changed to ' + vid_source + ' using ' + vid_device)


    def set_record_area(self, enabled):
        self.backend.set_record_area(enabled)


    def set_recording_area(self, x1, y1, x2, y2):
        # gstreamer backend needs to have the lower x/y coordinates
        # sent first.
        if (x2 < x1):
            if (y2 < y1):
                self.backend.set_recording_area(x2, y2, x1, y1)
            else:
                self.backend.set_recording_area(x2, y1, x1, y2)
        else:
            if (y2 < y1):
                self.backend.set_recording_area(x1, y2, x2, y1)
            else:
                self.backend.set_recording_area(x1, y1, x2, y2)


    def change_output_resolution(self, width, height):
        self.backend.change_output_resolution(width, height)
        self.logger.log.debug('Video output resolution changed to ' + width + 'x' + height)


    def change_stream_resolution(self, width, height):
        '''
        Change the stream resolution.
        '''
        # resolution should be text from list, i.e. 360p
        # map this to the appropriate numeric resolution if possible (i.e. 480x360)
        if self.config.resolution in self.config.resmap:
            res_temp = self.config.resmap[self.config.resolution]
        else:       # if the text is not in resmap, assume it is already numeric
            res_temp = self.config.resolution

        rec_res = res_temp.split('x')
        self.backend.change_stream_resolution(width, height, rec_res[0], rec_res[1])
        self.logger.log.debug('Video stream resolution changed to ' + str(width) + 'x' + str(height))


    def set_audio_mode(self, mode):
        '''
        Enables video recording when mode is set to True
        Disables video recording when mode is set to False
        '''
        if mode == True:
            self.logger.log.info('Audio recording: ENABLED')
        else:
            self.logger.log.info('Audio recording: DISABLED')

        self.backend.set_audio_mode(mode)


    def change_soundsrc(self, snd_source):
        '''
        Informs backend of new audio source to use when recording.
        '''
        return self.backend.change_audio_source(snd_source)


    def test_sources(self, state, video=False, audio=False):
        if state == True:
            self.backend.test_feedback_start(video, audio)
        else:
            self.backend.test_feedback_stop()


    def _prepare_metadata(self, presentation):
        '''
        Returns a dictionary of tags and tag values to be used
        to populate the current recording's file metadata.
        '''
        return { "title" : presentation.title,
                 "artist" : presentation.author,
                 "performer" : presentation.author,
                 "date" : presentation.start_time.strftime('%Y-%m-%d'),
                 "extended-comment" : 'timestamp=' + presentation.start_time.strftime('%Y-%m-%d %H:%M:%S%z'),
        }


    def record(self, presentation):
        '''
        Informs backend to begin recording presentation.
        '''
        self.backend.populate_metadata(self._prepare_metadata(presentation))

        self._current_presentation = presentation
        record_name = self._get_record_name(presentation)
        record_location = os.path.abspath(os.path.join(self.config.videodir, record_name))
        self.backend.record(record_location)
        self.logger.log.info('Recording started')


    def stop(self, presentation):
        '''
        Informs backend to stop recording.
        '''
        self.backend.stop()

        # Queue file for upload
        record_name = self._get_record_name(self._current_presentation)

        os.link(
            os.path.join(self.config.videodir, record_name),
            os.path.join(self.config.uploaddir, record_name))

        self.logger.log.info('Recording stopped')


    def test_feedback(self, video, audio):
        if self.feedback:
            self.feedback = False
            self.backend.test_feedback_stop()
        else:
            self.feedback = True
            self.backend.test_feedback_start(video, audio)


    def preview(self, enable=False, window_id=None):
        '''
        Enable/Disable the video preview window.
        '''
        if enable == True:
            self.backend.enable_video_feedback(window_id)
            self.logger.log.info('Video Preview Activated')
        else:
            self.backend.disable_video_feedback()
            self.logger.log.info('Video Preview Deactivated')


    def audioFeedback(self, enable=False):
        '''
        Enable/Disable the audio preview.
        '''
        if enable == True:
            self.backend.enable_audio_feedback()
            self.logger.log.info('Audio Feedback Activated')
        else:
            self.backend.disable_audio_feedback()
            self.logger.log.info('Audio Feedback Deactivated')


    def audioFeedbackEvent(self, percent):
        event_type = 'audio_feedback'
        self.ui.coreEvent(event_type, percent)
