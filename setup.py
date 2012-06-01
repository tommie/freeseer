#!/usr/bin/env python
import distutils.util
import glob
import os.path
import subprocess
import sys

from setuptools import setup

def uic4(inpath, outpath):
    subprocess.check_call([ 'pyuic4', '-o', outpath, inpath ])

def rcc4(inpath, outpath):
    subprocess.check_call([ 'pyrcc4', '-o', outpath, inpath ])

QT4_UI_DEFS = [
    ('frontend/configtool/forms/freeseer_configtool_ui.ui', 'frontend/configtool/freeseer_configtool_ui.py'),
    ('frontend/talkeditor/forms/talkeditor_ui_qt.ui', 'frontend/talkeditor/talkeditor_ui_qt.py'),
    ('frontend/default/forms/freeseer_ui_qt.ui', 'frontend/default/freeseer_ui_qt.py'),
    ('framework/forms/freeseer_about.ui', 'framework/freeseer_about.py'),
]

QT4_RC_DEFS = [
    ('framework/resources/resource.qrc', 'framework/resource_rc.py'),
]

build_dir = os.path.join('build', 'lib.%s-%s' % (distutils.util.get_platform(), sys.version[0:3]))

for (inpath, outpath) in QT4_UI_DEFS:
    outdir = os.path.join(build_dir, 'freeseer', os.path.dirname(outpath))
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    uic4(os.path.join('src', 'freeseer', inpath), os.path.join(build_dir, 'freeseer', outpath))

for (inpath, outpath) in QT4_RC_DEFS:
    outdir = os.path.join(build_dir, 'freeseer', os.path.dirname(outpath))
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    rcc4(os.path.join('src', 'freeseer', inpath), os.path.join(build_dir, 'freeseer', outpath))

setup(name='freeseer',
      version='2.5.3',
      description='video recording and streaming tool',
      author='fosslc',
      author_email='fosslc@gmail.com',
      url='http://wiki.github.com/fosslc/freeseer/',
      long_description='Freeseer is a tool for capturing or streaming video.\n\n\
It enables you to capture great presentations, demos, training material,\n\
and other videos. It handles desktop screen-casting with ease.\n\n\
Freeseer is one of a few such tools that can also record vga output \n\
or video from external sources such as firewire, usb, s-video, or rca.\n\n\
It is particularly good at handling very large conferences with hundreds \n\
of talks and speakers using varied hardware and operating systems.\n\n\
Freeseer itself can run on commodity hardware such as a laptop or desktop.',
      license='GPLv3',
      package_dir={'freeseer': 'src/freeseer'},
      packages=['freeseer', 'freeseer.backend',
                            'freeseer.framework',
                            'freeseer.frontend',
                            'freeseer.frontend.configtool',
                            'freeseer.frontend.talkeditor',
                            'freeseer.frontend.default'],
      scripts=['src/freeseer-record', 'src/freeseer-config', 'src/freeseer-talkeditor'],
      data_files=[('share/applications', ['data/freeseer.desktop']),
                  ('share/applications', ['data/48x48-freeseer.png']),
                  ('share/pixmaps', ['src/freeseer/framework/resources/freeseer_logo.png']),
                  ('share/freeseer/translations/configtool', glob.glob('src/freeseer/frontend/configtool/languages/*.qm')),
                  ('share/freeseer/translations/default', glob.glob('src/freeseer/frontend/default/languages/*.qm')),
                  ('share/freeseer/translations/talkeditor', glob.glob('src/freeseer/frontend/talkeditor/languages/*.qm')),
                  ('/etc/modprobe.d', ['data/vga2usb.conf'])]
)
