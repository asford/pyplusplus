import os
import sys
import getpass

class boost:
    libs = ''
    include = ''

class python:
    libs = ''
    include = ''

class gccxml:
    executable = ''

class scons:
    suffix = ''
    cmd_build = ''
    cmd_clean = ''
    ccflags = []
    
if 'roman' in getpass.getuser():
    
    scons.cmd_build = 'scons --file=%s'
    scons.cmd_clean = 'scons --clean --file=%s'

    if sys.platform == 'win32':
        scons.suffix = '.dll'
        scons.ccflags = ['/MD', '/EHsc', '/GR', '/Zc:wchar_t', '/Zc:forScope' ]
        boost.libs = 'd:/boost_cvs/bin'
        boost.include = 'd:/boost_cvs'
        python.libs = 'c:/python/libs'
        python.include = 'c:/python/include'
        gccxml.executable = 'c:/tools/gccxml/bin/gccxml.exe'
    else:
        scons.suffix = '.so'
        boost.libs = '/home/roman/boost_cvs/bin'
        boost.include = '/home/roman/boost_cvs'
        python.include = '/usr/include/python2.4'
        gccxml.executable = '/home/roman/gccxml/bin/gccxml'


_my_path = None
try:
    import environment_path_helper
    environment_path_helper.raise_error()
except Exception, error:
    _my_path = os.path.abspath( os.path.split( sys.exc_traceback.tb_frame.f_code.co_filename )[0] )
    if not os.path.exists( os.path.join( _my_path, 'environment.py' ) ):
        #try another guess
        if sys.modules.has_key('environment'):
            _my_path = os.path.split( sys.modules['environment'].__file__ )[0]

try:
    import pygccxml
    print 'pygccxml INSTALLED version will be used'
except ImportError:
    sys.path.append( os.path.join( _my_path, '../pygccxml_dev' ) )
    import pygccxml
    print 'pygccxml DEVELOPMENT version will be used'

import pyplusplus

