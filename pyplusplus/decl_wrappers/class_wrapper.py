# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""defines class that configure class definition and class declaration exposing"""

import os
import user_text
import decl_wrapper
import scopedef_wrapper
from pygccxml import declarations
import indexing_suite1 as isuite1
import indexing_suite2 as isuite2


always_expose_using_scope_documentation = \
"""boolean, configures how Py++ should generate code for class.
Py can generate code using IDL like syntax:

    class_< ... >( ... )
        .def( ... );

Or it can generate code using more complex form:

    typedef bp::class_< my_class > my_class_exposer_t;
    my_class_exposer_t my_class_exposer = my_class_exposer_t( "my_class" );
    boost::python::scope my_class_scope( my_class_exposer );
    my_class_exposer.def( ... );

Also, the second way is much longer, it solves few problems:

    - you can not expose enums and internal classes defined within the class using first method
    - you will get much better compilation errors
    - the code looks like regular C++ code after all :-)

By default, this property is set to False. Also, Py++ knows pretty well
when it have to ignore this property and generate right code
"""

class class_common_details_t( object ):
    """defines few properties that are common to
    L{class declaration<pygccxml.declarations.class_declaration_t>} and
    L{definition<pygccxml.declarations.class_t>} classes
    """
    def __init__(self):
        object.__init__( self )
        self._always_expose_using_scope = False
        self._indexing_suite = None
        self._equality_comparable = None
        self._less_than_comparable = None
        self._isuite_version = 1

    def _get_indexing_suite_version( self ):
        return self._isuite_version
    def _set_indexing_suite_version( self, version ):
        assert version in ( 1, 2 )
        if self._isuite_version != version:
            self._isuite_version = version
            self._indexing_suite = None
    indexing_suite_version = property( _get_indexing_suite_version, _set_indexing_suite_version
                                       , doc="indexing suite version")

    def _get_indexing_suite( self ):
        if self._indexing_suite is None:
            for container_traits in declarations.all_container_traits:
                if container_traits.is_my_case( self ):
                    if self._isuite_version == 1:
                        self._indexing_suite = isuite1.indexing_suite1_t( self, container_traits )
                    else:
                        self._indexing_suite = isuite2.indexing_suite2_t( self, container_traits )
                    break
        return self._indexing_suite
    indexing_suite = property( _get_indexing_suite
                               , doc="reference to indexing suite configuration class. " \
                                    +"If the class is not STD container, returns None")

    def _get_always_expose_using_scope( self ):
        #I am almost sure this logic should be moved to code_creators
        if isinstance( self.indexing_suite, isuite2.indexing_suite2_t ) \
           and ( self.indexing_suite.disable_methods or self.indexing_suite.disabled_methods_groups ):
            return True
        return self._always_expose_using_scope
    def _set_always_expose_using_scope( self, value ):
        self._always_expose_using_scope = value
    always_expose_using_scope = property( _get_always_expose_using_scope, _set_always_expose_using_scope
                                          , doc="please see L{class_wrapper.always_expose_using_scope_documentation} variable for documentation."  )

    def _get_equality_comparable( self ):
        if None is self._equality_comparable:
            self._equality_comparable = declarations.has_public_equal( self )
        return self._equality_comparable

    def _set_equality_comparable( self, value ):
        self._equality_comparable = value

    equality_comparable = property( _get_equality_comparable, _set_equality_comparable
                                    , doc="indicates existence of public operator=" \
                                         +"Default value is calculated, based on information presented in the declarations tree" )

    def _get_less_than_comparable( self ):
        if None is self._less_than_comparable:
            self._less_than_comparable = declarations.has_public_less( self )
        return self._less_than_comparable

    def _set_less_than_comparable( self, value ):
        self._less_than_comparable = value

    less_than_comparable = property( _get_less_than_comparable, _set_less_than_comparable
                                     , doc="indicates existence of public operator<. " \
                                          +"Default value is calculated, based on information presented in the declarations tree" )

#this will only be exported if indexing suite is not None and only when needed
class class_declaration_t( class_common_details_t
                           , decl_wrapper.decl_wrapper_t
                           , declarations.class_declaration_t ):
    def __init__(self, *arguments, **keywords):
        class_common_details_t.__init__( self )
        declarations.class_declaration_t.__init__(self, *arguments, **keywords )
        decl_wrapper.decl_wrapper_t.__init__( self )

class class_t( class_common_details_t
               , scopedef_wrapper.scopedef_t
               , declarations.class_t):
    def __init__(self, *arguments, **keywords):
        class_common_details_t.__init__( self )
        declarations.class_t.__init__(self, *arguments, **keywords )
        scopedef_wrapper.scopedef_t.__init__( self )

        self._redefine_operators = False
        self._held_type = None
        self._noncopyable = None
        self._wrapper_alias = self._generate_valid_name() + "_wrapper"
        self._registration_code = []
        self._declaration_code = []
        self._wrapper_code = []
        self._null_constructor_body = ''
        self._copy_constructor_body = ''
        self._exception_translation_code = None

    def _get_redefine_operators( self ):
        return self._redefine_operators
    def _set_redefine_operators( self, new_value ):
        self._redefine_operators = new_value
    redefine_operators = property( _get_redefine_operators, _set_redefine_operators
                                   , doc="tells Py++ to redefine operators from base class in this class, False by default")

    def _get_held_type(self):
        return self._held_type
    def _set_held_type(self, held_type):
        self._held_type = held_type
    held_type = property( _get_held_type, _set_held_type
                          , doc="string, this property tells Py++ what HeldType this class has" \
                               +"Default value is calculated, based on information presented in exposed declarations" )

    def _get_noncopyable(self):
        if self._noncopyable is None:
            self._noncopyable = declarations.is_noncopyable( self )
        return self._noncopyable
    def _set_noncopyable(self, noncopyable):
        self._noncopyable= noncopyable
    noncopyable = property( _get_noncopyable, _set_noncopyable
                            , doc="True if the class is noncopyable, False otherwies" \
                                 +"Default value is calculated, based on information presented in the declarations tree" )

    def _get_wrapper_alias( self ):
        return self._wrapper_alias
    def _set_wrapper_alias( self, walias ):
        self._wrapper_alias = walias
    wrapper_alias = property( _get_wrapper_alias, _set_wrapper_alias
                              , doc="class-wrapper name")

    @property
    def declaration_code( self ):
        """
        List of strings, that contains valid C++ code, that will be added to
        the class registration section
        """
        return self._declaration_code

    @property
    def registration_code( self ):
        """
        List of strings, that contains valid C++ code, that will be added to
        the class registration section
        """
        return self._registration_code

    @property
    def wrapper_code( self ):
        """
        List of strings, that contains valid C++ code, that will be added to
        the class wrapper.
        """
        return self._wrapper_code

    def _get_null_constructor_body(self):
        return self._null_constructor_body
    def _set_null_constructor_body(self, body):
        self._null_constructor_body = body
    null_constructor_body = property( _get_null_constructor_body, _set_null_constructor_body
                                      , doc="null constructor code, that will be added as is to the null constructor of class-wrapper")

    def _get_copy_constructor_body(self):
        return self._copy_constructor_body
    def _set_copy_constructor_body(self, body):
        self._copy_constructor_body = body
    copy_constructor_body = property( _get_copy_constructor_body, _set_copy_constructor_body
                                      , doc="copy constructor code, that will be added as is to the copy constructor of class-wrapper")

    @property
    def exception_argument_name( self ):
        """exception argument name for translate exception function

        If you don't understand what this argument is, please take a look on
        Boost.Python documentation: http://www.boost.org/libs/python/doc/v2/exception_translator.html
        """
        return 'exc'

    def _get_exception_translation_code( self ):
        return self._exception_translation_code
    def _set_exception_translation_code( self, code ):
        self._exception_translation_code = code
    exception_translation_code = property( _get_exception_translation_code, _set_exception_translation_code
                                           , doc="C++ exception to Python exception translation code" \
                                                +"\nExample: PyErr_SetString(PyExc_RuntimeError, exc.what()); " \
                                                +"\nPy++ will generate the rest of the code." \
                                                +"\nPay attention: the exception variable name is exc." )

    def translate_exception_to_string( self, python_exception_type, to_string ):
        """registers exception translation to string

        @param python_exception_type: Python exception type, for example PyExc_RuntimeError
        @type python_exception_type: str

        @param to_string: C++ expression that extracts information from exception.
                          The type of expression should be char*.
        @type to_string: str
        """
        #NICE TO HAVE:
        #1. exception\assert\warning should be raised if python_exception_type
        #   does not contain valid Python exception
        #2. Py++ can validate, that member function returns char*
        code = "PyErr_SetString( %(exception_type)s, %(to_string)s ); " \
               % { 'exception_type' : python_exception_type, 'to_string' : to_string }
        self.exception_translation_code = code

    def add_declaration_code( self, code ):
        """adds the code to the declaration section"""
        self.declaration_code.append( user_text.user_text_t( code ) )

    def add_registration_code( self, code, works_on_instance=True ):
        """adds the code to the class registration section

        works_on_instance: If true, the custom code can be applied directly to obj inst.
        Example: ObjInst."CustomCode"
        """
        self.registration_code.append( user_text.class_user_text_t( code, works_on_instance ) )
    #preserving backward computability
    add_code = add_registration_code

    def add_wrapper_code( self, code ):
        """adds code to the class wrapper class definition"""
        self.wrapper_code.append( user_text.user_text_t( code ) )

    def set_constructors_body( self, body ):
        """Sets the body for all constructors"""
        self.constructors().body = body
        self.null_constructor_body = body
        self.copy_constructor_body = body

    def _exportable_impl( self ):
        if not self.name:
            return 'Py++ can not expose unnamed classes.'
            #it is possible to do so, but not for unnamed classes defined under namespace.
        if isinstance( self.parent, declarations.namespace_t ):
            return ''
        if not self in self.parent.public_members:
            return 'Py++ can not expose private class.'
        return ''

    def get_exportable_members( self, sort=None ):
        """returns list of internal declarations that should\\could be exported"""
        #TODO: obviously this function should be shorter. Almost all logic of this class
        #      should be spread between decl_wrapper classes
        members = filter( lambda mv: mv.ignore == False and mv.exportable, self.public_members )
        #protected and private virtual functions that not overridable and not pure
        #virtual should not be exported
        for member in self.protected_members:
            if not isinstance( member, declarations.calldef_t ):
                continue
            else:
                members.append( member )

        vfunction_selector = lambda member: isinstance( member, declarations.member_function_t ) \
                                            and member.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL
        members.extend( filter( vfunction_selector, self.private_members ) )
        #now lets filter out none public operators: Py++ does not support them right now
        members = filter( lambda decl: not isinstance( decl, declarations.member_operator_t )
                                       or decl.access_type == declarations.ACCESS_TYPES.PUBLIC
                          , members )
        #-#if declarations.has_destructor( self ) \
        #-#   and not declarations.has_public_destructor( self ):
            #remove artificial constructors
        members = filter( lambda decl: not isinstance( decl, declarations.constructor_t )
                                       or not decl.is_artificial
                          , members )
        members = filter( lambda member: member.ignore == False and member.exportable, members )
        sorted_members = members
        if sort:
            sorted_members = sort( members )
        return sorted_members
