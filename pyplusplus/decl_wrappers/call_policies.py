# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This modules contains definition of call policies classes. Call policies names
are same, that used in boost.python library. 

For every class that implements code creation of call policies, there is a 
convinience function.
"""

from pygccxml import declarations
import algorithm

class CREATION_POLICY:
    """Implementation details"""
    AS_INSTANCE = 'as instance'
    AS_TEMPLATE_ARGUMENT = 'as template argument'

class call_policy_t(object):
    """Base class for all call polices classes"""
    def __init__(self):
        object.__init__(self)

    def create(self, function_creator, creation_policy=CREATION_POLICY.AS_INSTANCE):
        """Creates code from the call policies class instance.
        @param function_creator: parent code creator
        @type function_creator: L{code_creators.function_t} or L{code_creators.constructor_t}

        @param creation_policy: indicates whether we this call policy used as template
                                argument or as an instance
        @type creation_policy: L{CREATION_POLICY}
        """
        code = self._create_impl( function_creator )
        if creation_policy == CREATION_POLICY.AS_INSTANCE:
            code = code + '()'
        return code

    def _create_impl( self, function_creator ):
        raise NotImplementedError()
   
class default_t(call_policy_t):
    """implementation for ::boost::python::default_call_policies"""
    def __init__( self ):
        call_policy_t.__init__( self )
    
    def _create_impl(self, function_creator ):
        return algorithm.create_identifier( function_creator, '::boost::python::default_call_policies' )
    
    def __str__(self):
        return 'default_call_policies'
    
def default_call_policies():
    """create ::boost::python::default_call_policies"""
    return default_t()

class compound_policy_t( call_policy_t ):
    """base class for all call policies, except default one"""
    def __init__( self, base=None ):
        call_policy_t.__init__( self )
        self._base = base
        if not base:
            self._base = default_t()
            
    def _get_base_policy( self ):
        return self._base    
    def _set_base_policy( self, new_policy ):
        self._base = new_policy
    base_policy = property( _get_base_policy, _set_base_policy
                            , doc="base call policy, by default is reference to L{default_t} call policy")

    def _get_args(self, function_creator):
        return []

    def _get_name(self, function_creator):
        raise NotImplementedError()
    
    def _create_impl( self, function_creator ):
        args = self._get_args(function_creator)
        args.append( self._base.create( function_creator, CREATION_POLICY.AS_TEMPLATE_ARGUMENT ) )
        name = algorithm.create_identifier( function_creator, self._get_name(function_creator) )
        return declarations.templates.join( name, args )

    def __str__(self):
        name = self._get_name(None).replace('::boost::python::', '' )
        args = map( lambda text: text.replace( '::boost::python::', '' )
                    , self._get_args( None ) )
        return declarations.templates.join( name, args )
        
class return_argument_t( compound_policy_t ):
    """implementation for ::boost::python::return_argument call policies"""
    def __init__( self, position=1, base=None):
        compound_policy_t.__init__( self, base )
        self._position = position
        
    def _get_position( self ):
        return self._position
    def _set_position( self, new_position):
        self._position = new_position
    position = property( _get_position, _set_position )

    def _get_name(self, function_creator):
        if self.position == 1:
            return '::boost::python::return_self'
        else:
            return '::boost::python::return_arg'
    
    def _get_args(self, function_creator):
        if self.position == 1:
            return []
        else:
            return [ str( self.position ) ]

def return_arg( arg_pos, base=None ):
    return return_argument_t( arg_pos, base )

def return_self(base=None):
    return return_argument_t( 1, base )

class return_internal_reference_t( compound_policy_t ):
    def __init__( self, position=1, base=None):
        compound_policy_t.__init__( self, base )
        self._position = position
        
    def _get_position( self ):
        return self._position
    def _set_position( self, new_position):
        self._position = new_position
    position = property( _get_position, _set_position )

    def _get_name(self, function_creator):
        return '::boost::python::return_internal_reference'
    
    def _get_args(self, function_creator):
        return [ str( self.position ) ]

def return_internal_reference( arg_pos=1, base=None):
    return return_internal_reference_t( arg_pos, base )
        
class with_custodian_and_ward_t( compound_policy_t ):
    def __init__( self, custodian, ward, base=None):
        compound_policy_t.__init__( self, base )
        self._custodian = custodian
        self._ward = ward
        
    def _get_custodian( self ):
        return self._custodian
    def _set_custodian( self, new_custodian):
        self._custodian = new_custodian
    custodian = property( _get_custodian, _set_custodian )
        
    def _get_ward( self ):
        return self._ward
    def _set_ward( self, new_ward):
        self._ward = new_ward
    ward = property( _get_ward, _set_ward )
    
    def _get_name(self, function_creator):
        return '::boost::python::with_custodian_and_ward'
    
    def _get_args(self, function_creator):
        return [ str( self.custodian ), str( self.ward ) ]

def with_custodian_and_ward( custodian, ward, base=None):
    return with_custodian_and_ward_t( custodian, ward, base )

class with_custodian_and_ward_postcall_t( with_custodian_and_ward_t ):
    def __init__( self, custodian, ward, base=None):
        with_custodian_and_ward_t.__init__( self, custodian, ward, base )

    def _get_name(self, function_creator):
        return '::boost::python::with_custodian_and_ward_postcall'
    
def with_custodian_and_ward_postcall( custodian, ward, base=None):
    return with_custodian_and_ward_postcall_t( custodian, ward, base )

class return_value_policy_t( compound_policy_t ):
    def __init__( self, result_converter_generator, base=None):
        compound_policy_t.__init__( self, base )
        self._result_converter_generator = result_converter_generator
        
    def _get_result_converter_generator( self ):
        return self._result_converter_generator
    def _set_result_converter_generator( self, new_result_converter_generator):
        self._result_converter_generator = new_result_converter_generator
    result_converter_generator = property( _get_result_converter_generator
                                           , _set_result_converter_generator )

    def _get_name(self, function_creator):
        return '::boost::python::return_value_policy'
    
    def _get_args(self, function_creator):
        if function_creator:
            rcg = algorithm.create_identifier( function_creator, self.result_converter_generator )
            return [ rcg ]
        else:
            return [self.result_converter_generator]

copy_const_reference = '::boost::python::copy_const_reference'
copy_non_const_reference = '::boost::python::copy_non_const_reference'
manage_new_object = '::boost::python::manage_new_object'
reference_existing_object = '::boost::python::reference_existing_object'
return_by_value = '::boost::python::return_by_value'
return_opaque_pointer = '::boost::python::return_opaque_pointer'

def return_value_policy( result_converter_generator, base=None):
    return return_value_policy_t( result_converter_generator, base )