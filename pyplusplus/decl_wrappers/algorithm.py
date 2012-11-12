# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""Contains few unrelated algorithms, which works on code creators tree"""

import re
from pygccxml import declarations

def creators_affect_on_me( me ):
    """
    find all relevant code creators, which influence on code generated by "me".

    C++ allows to define aliases to namespaces. `Py++` allows user to define
    aliases to the namespace and will take this aliases into account when it
    generates the code.

    Example: ::

      [a b c d e f g]
             |
             + [k l m]
                  |
                  + [y x] <-- we are here ( x )

    return value is: [y,l,k,d,c,b,a]
    """
    class impl:
        def __init__( self, creator):
            self._creator = creator

        def _get_left_siblings( self, child ):
            if not child or not child.parent:
                return []
            ids = list(map( id, child.parent.creators ))
            child_index = ids.index( id( child ) )
            return child.parent.creators[:child_index]

        def _get_definition_set( self, child ):
            answer = []
            while child:
                answer.extend( self._get_left_siblings( child ) )
                child = child.parent
            return answer

        def affect_creators(self):
            return self._get_definition_set( self._creator )
    return impl( me ).affect_creators()

__RE_VALID_IDENTIFIER = re.compile( r"[_a-z]\w*", re.I | re.L | re.U )
def create_valid_name(name):
    """
    creates Python identifier from a string

    As input this functions takes valid C++ name\\identifier and replaces all
    illegal characters.

    Illegal characters are introduced by a template instantiation.
    """
    global __RE_VALID_IDENTIFIER
    match_found = __RE_VALID_IDENTIFIER.match(name)
    if match_found and ( match_found.end() - match_found.start() == len(name) ):
        return name
    replace_table = {
          '<'  : '_less_'
        , '>'  : '_greater_'
        , '::' : '_scope_'
        , ','  : '_comma_'
        , ' '  : '_'
        , '\t' : '_'
        , '*'  : '_ptr_'
        , '&'  : '_ref_'
        , '('  : '_obrace_'
        , ')'  : '_cbrace_'
        , '['  : '_o_sq_brace_'
        , ']'  : '_c_sq_brace_'
        , '='  : '_equal_'
        , '.'  : '_dot_'
        , '$'  : '_dollar_'
    }
    for orig, dest in list(replace_table.items()):
        name = name.replace( orig, dest )
    return name


def create_identifier(creator, full_name ):
    """Return new full name, which takes into account namespace aliases"""

    from pyplusplus import code_creators
    dset = creators_affect_on_me( creator )
    dset = [x for x in dset if isinstance( x, code_creators.namespace_alias_t )]
    full_name = full_name.lstrip( '::' )
    for nsalias in dset:
        fnsname = nsalias.full_namespace_name + '::'
        if full_name.startswith( fnsname ):
            new_name = nsalias.alias + '::' + full_name[ len(fnsname) :  ]
            return new_name
    else:
        return full_name

class registration_order:
    """the class, introduces few functions, which deals with functions registration order problem"""

    @staticmethod
    def is_related( t1, t2 ):
        """Check whether two types\\classes t1 and t2 could introduce the problem"""

        if declarations.is_pointer( t1 ) and declarations.is_pointer( t2 ):
            return registration_order.is_related( declarations.remove_pointer( t1 )
                                                  , declarations.remove_pointer( t2 ) )
        elif declarations.is_pointer( t1 ) and not declarations.is_pointer( t2 ):
            t1 = declarations.remove_cv( declarations.remove_pointer( t1 ) )
            t2 = declarations.remove_cv( t2 )
            if declarations.is_same( t1, t2 ):
                return 1
        elif not declarations.is_pointer( t1 ) and declarations.is_pointer( t2 ):
            t1 = declarations.remove_cv( t1 )
            t2 = declarations.remove_cv( declarations.remove_pointer( t2 ) )
            if declarations.is_same( t1, t2 ):
                return -1
        else: #not is_pointer( t1 ) and not is_pointer( t2 ):
            if declarations.is_integral( t1 ) and not declarations.is_bool( t1 ) \
               and declarations.is_bool( t2 ):
                return -1
            elif declarations.is_bool( t1 ) \
                 and declarations.is_integral( t2 ) and not declarations.is_bool( t2 ):
                return 1
            else:
                pass
        return None

    @staticmethod
    def select_problematics( calldef ):
        """Return list of problematic functions for function "calldef" """
        if 1 != len( calldef.required_args ):
            return []
        arg_type = calldef.arguments[0].type
        if declarations.is_calldef_pointer( arg_type ):
            return []
        problematics = []
        for f in calldef.overloads:
            if 1 != len( f.required_args ):
                continue
            if f.ignore:
                continue
            if None != registration_order.is_related( calldef.arguments[0].type, f.arguments[0].type ):
                problematics.append( f )
        return problematics
