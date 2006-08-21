# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""defines interface for exposing STD containers, using current version of indexing suite"""

from pygccxml import declarations

#NoProxy
#By default indexed elements have Python reference semantics and are returned by
#proxy. This can be disabled by supplying true in the NoProxy template parameter.
#When we want to disable is:
#1. We deal with immutable objects:
#   1. fundamental types
#   2. enum type
#   3. std::[w]string
#   4. std::complex
#   5. shared_ptr

class indexing_suite1_t( object ):
    """
    This class helps user to export STD containers, using Boost.Python
    indexing suite V2.
    """

    def __init__( self, container_class, container_traits, no_proxy=None, derived_policies=None ):
        object.__init__( self )
        self.__no_proxy = no_proxy
        self.__derived_policies = derived_policies
        self.__container_class = container_class
        self.__container_traits = container_traits

    def _get_container_class( self ):
        return self.__container_class
    container_class = property( _get_container_class
                                , doc="Reference to STD container class" )

    def _get_element_type(self):
        return self.__container_traits.element_type( self.container_class )
    element_type = property( _get_element_type
                            , doc="Reference to container value_type( mapped_type ) type" )

    def _get_no_proxy( self ):
        if self.__no_proxy is None:
            element_type = self.element_type
            if declarations.is_fundamental( element_type ) \
               or declarations.is_enum( element_type )    \
               or declarations.is_std_string( element_type ) \
               or declarations.is_std_wstring( element_type ) \
               or declarations.smart_pointer_traits.is_smart_pointer( element_type ):
                self.__no_proxy = True
            else:
                self.__no_proxy = False
        return self.__no_proxy

    def _set_no_proxy( self, no_proxy ):
        self.__no_proxy = no_proxy
    no_proxy = property( _get_no_proxy, _set_no_proxy
                         , doc="NoProxy value, the initial value depends on container"
                              +" element_type( mapped_type ) type. In most cases, "
                              +"Py++ is able to guess this value, right. If you are not "
                              +"lucky, you will have to set the property value.")

    def _get_derived_policies( self ):
        return self.__derived_policies
    def _set_derived_policies( self, derived_policies ):
        self.__derived_policies = derived_policies
    derived_policies = property( _get_derived_policies, _set_derived_policies
                                 , doc="This proprty contains DerivedPolicies string. "
                                      +"It will be added as is to the generated code.")
