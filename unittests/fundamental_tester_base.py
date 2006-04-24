# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import autoconfig
from pyplusplus import module_builder

LICENSE = """// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)"""

class fundamental_tester_base_t( unittest.TestCase ):
    SUFFIX_TO_BE_EXPORTED = '_to_be_exported.hpp'
    
    def __init__(self, module_name, *args ):
        unittest.TestCase.__init__(self, *args)
        self.__module_name = module_name
        self.__to_be_exported_header \
            = os.path.join( autoconfig.data_directory
                            , self.__module_name + self.SUFFIX_TO_BE_EXPORTED )
        
        self.__generated_source_file_name = os.path.join( autoconfig.scons_config.build_dir
                                                          , self.__module_name + '.cpp' )
        self.__generated_scons_file_name = os.path.join( autoconfig.scons_config.build_dir
                                                          , self.__module_name + '.scons' )

    def failIfRaisesAny(self, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except Exception, error:
            self.fail( 'exception has been raised during execution. exception: ' + str(error) )

    def failIfNotRaisesAny(self, callableObj, *args, **kwargs):
        was_exception = False
        try:
            callableObj(*args, **kwargs)
        except:
            was_exception = True
        self.failUnless(was_exception, 'exception has not been raised during execution.')           
    def customize(self, generator):
        pass
        
    def run_tests(self, module):
        raise NotImplementedError()

    def _create_extension_source_file(self):
        global LICENSE
        mb = module_builder.module_builder_t( [self.__to_be_exported_header]
                                              , gccxml_path=autoconfig.gccxml_path
                                              , include_paths=[autoconfig.boost_path]
                                              , undefine_symbols=['__MINGW32__'] )
        self.customize( mb )
        if not mb.has_code_creator():
            mb.build_code_creator( self.__module_name )
        mb.code_creator.std_directories.extend( autoconfig.scons_config.cpppath )
        mb.code_creator.user_defined_directories.append( autoconfig.package_location )
        mb.code_creator.precompiled_header = "boost/python.hpp" 
        mb.code_creator.license = LICENSE
        mb.write_module( self.__generated_source_file_name )

    def _create_sconstruct(self, sources ):
        sources_str = []
        for source in sources:
            sources_str.append( "r'%s'" % source )
        sources_str = ','.join( sources_str )
        sconstruct_script = autoconfig.scons_config.create_sconstruct()\
                            % { 'target' : self.__module_name
                                , 'sources' : sources_str }
        sconstruct_file = file( self.__generated_scons_file_name, 'w+b' )
        sconstruct_file.write( sconstruct_script )
        sconstruct_file.close()
    
    def _create_extension(self):
        cmd = autoconfig.scons_config.cmd_build % self.__generated_scons_file_name
        output = os.popen( cmd )
        scons_reports = []
        while True:
            data = output.readline()
            scons_reports.append( data )
            if not data:
                break
        exit_status = output.close()
        scons_msg = ''.join(scons_reports)
        if scons_msg:
            print os.linesep
            print scons_msg
        if exit_status:
            raise RuntimeError( "unable to compile extension. error: %s" % scons_msg )

    def _clean_build( self, sconstruct_file ):
        cmd = autoconfig.scons_config.cmd_clean % sconstruct_file
        output = os.popen( cmd )
        scons_reports = []
        while True:
            data = output.readline()
            scons_reports.append( data )
            if not data:
                break
        exit_status = output.close()
        scons_msg = ''.join(scons_reports)
        if exit_status:
            raise RuntimeError( "unable to clean extension. error: %s" % scons_msg )

    def test(self):
        pypp = None
        try:
            self._create_extension_source_file()
            sources = [ self.__generated_source_file_name ]            
            to_be_exported_cpp = os.path.splitext( self.__to_be_exported_header )[0] + '.cpp'
            if os.path.exists( to_be_exported_cpp ):
                sources.append( to_be_exported_cpp  )
            self._create_sconstruct(sources)
            self._create_extension()       
            pypp = __import__( self.__module_name )
            self.run_tests(pypp)
        finally:
            if sys.modules.has_key( self.__module_name ):
                del sys.modules[self.__module_name]
            del pypp
            #self._clean_build(self.__generated_scons_file_name)