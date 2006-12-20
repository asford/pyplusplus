# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""This module contains the class L{transformer_t}.
"""

import sys, os.path, copy, re, types
from pygccxml import declarations, parser

return_ = -1
#return_ is a spacial const, which represent an index of return type

class transformer_t:
    """Base class for a function transformer."""
    
    USE_1_BASED_INDEXING = False
        
    def __init__(self, function):
        """@param function: reference to function declaration"""
        self.__function = function

    @property 
    def function( self ):
        """reference to the function, for which a wrapper will be generated"""
        return self.__function

    def required_headers( self ):
        """Returns list of header files that transformer generated code depends on."""
        return []

    def get_argument( self, reference ):
        """returns reference to the desired argument
        
        @param reference: name( str ) or index( int ) of the argument
        """
        if isinstance( reference, str ):
            found = filter( lambda arg: arg.name == reference, self.function.arguments )
            if len( found ) == 1:
                return found[0]
            raise RuntimeError( "Argument with %s was not found" % reference )
        else:
           assert isinstance( reference, int )
           if transformer_t.USE_1_BASED_INDEXING:
               reference += 1
           return self.function.arguments[ reference ]

    def get_type( self, reference ):
        """returns type of the desired argument or return type of the function
        
        @param reference: name( str ) or index( int ) of the argument
        """       
        global return_
        if isinstance( reference, int ) and reference == return_:
            return self.function.return_type
        else:
            return self.get_argument( reference ).type

    def configure_mem_fun( self, controller ):
        """Transformers should overridde the method, in order to define custom 
        transformation for non-virtual member function.
        
        @param controller: instance of L{mem_fun_controller_t} class
        """
        pass
    
    def configure_free_fun( self, controller ):
        """Transformers should overridde the method, in order to define custom 
        transformation for free function.
        
        @param controller: instance of L{free_fun_controller_t} class
        """        
        pass
    
    def configure_virtual_mem_fun( self, controller ):
        """Transformers should overridde the method, in order to define custom 
        transformation for virtual member function.
        
        @param controller: instance of L{virtual_mem_fun_controller_t} class
        """        
        pass
        
