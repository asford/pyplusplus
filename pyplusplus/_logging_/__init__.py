# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#TODO: find better place for it

"""
This package contains logging configuration for pyplusplus. Default log level
is DEBUG. Default log messages destination is sys.stdout.
"""

import os
import sys
import logging
from multi_line_formatter import multi_line_formatter_t

def _create_logger_( name ):    
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter( multi_line_formatter_t( os.linesep + '%(levelname)s: %(message)s' ) )
    logger.addHandler(handler) 
    logger.setLevel(logging.INFO)
    return logger

class loggers:
    file_writer = _create_logger_( 'pyplusplus.file_writer' )
    declarations = _create_logger_( 'pyplusplus.declarations' )
    module_builder = _create_logger_( 'pyplusplus.module_builder' )
    #root logger exists for configuration purpose only
    root = logging.getLogger( 'pyplusplus' )
    all = [ root, file_writer, module_builder ]
