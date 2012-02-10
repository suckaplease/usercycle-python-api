#!/usr/bin/env python
#Copyright 2011 A.T. Fouty
#
#Licensed under the Apache License, Version 2.0 (the 'License');
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an 'AS IS' BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

from distutils.core import setup

json_pkg = ""

try:
    import simplejson
except:
    try:
        import json
    except:
        json_pkg = 'simplejson'
    

setup(name='usercycle',
       version='1.0',
       description='USERcycle Python API wrapper',
       author='A.T. Fouty',
       author_email='afouty@gmail.com',
       url='http://github.com/suckaplease/usercycle-python-api',
       packages=['usercycle',],
       install_requires=[json_pkg,"requests",]
    )
