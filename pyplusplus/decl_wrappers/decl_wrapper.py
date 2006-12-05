# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""defines base class for all classes, that will keep Py++ code generator engine
instructions."""

import algorithm
from pyplusplus import _logging_
from pygccxml import declarations
from pyplusplus import messages

class decl_wrapper_t(object):
    """Declaration interface.

    This class represents the interface to the declaration tree. Its
    main purpose is to "decorate" the nodes in the tree with
    information about how the binding is to be created. Instances of
    this class are never created by the user, instead they are
    returned by the API.
    """

    def __init__(self):
        object.__init__(self)
        self._alias = None
        self._ignore = False
        self._exportable = None
        self._exportable_reason = None
        self._documentation = None

    @property
    def logger( self ):
        """returns reference to L{_logging_.loggers.declarations}"""
        return _logging_.loggers.declarations

    def _get_documentation( self ):
        return self._documentation
    def _set_documentation( self, value ):
        self._documentation = value
    documentation = property( _get_documentation, _set_documentation
                             , doc="Using this property you can set documentation of the declaration." )

    def _generate_valid_name(self, name=None):
        if name == None:
            name = self.name
        return algorithm.create_valid_name( name )

    def _get_alias(self):
        if not self._alias:
            if declarations.templates.is_instantiation( self.name ):
                container_aliases = [ 'value_type', 'key_type', 'mapped_type' ]
                if isinstance( self, declarations.class_t ) \
                    and 1 == len( set( map( lambda typedef: typedef.name, self.aliases ) ) ) \
                    and self.aliases[0].name not in container_aliases:
                        self._alias = self.aliases[0].name
                else:
                    self._alias = self._generate_valid_name()
            else:
                self._alias = self.name
        return self._alias
    def _set_alias(self, alias):
        self._alias = alias
    alias = property( _get_alias, _set_alias
                      , doc="Using this property you can easily change Python name of declaration" )

    def rename( self, new_name ):
        """renames the declaration name, under which it is exposed"""
        self.alias = new_name

    def _get_ignore( self ):
        return self._ignore
    def _set_ignore( self, value ):
        self._ignore = value
    ignore = property( _get_ignore, _set_ignore
                       ,doc="If you set ignore to True then this declaration will not be exported." )

    def exclude( self ):
        """Exclude "self" and child declarations from being exposed."""
        self.ignore = True

    def include( self ):
        """Include "self" and child declarations to be exposed."""
        self.ignore = False

    def why_not_exportable( self ):
        """returns strings that explains why this declaration could not be exported or None otherwise"""
        if None is self._exportable_reason:
            self.get_exportable()
        return self._exportable_reason

    def _exportable_impl( self ):
        return ''

    def get_exportable( self ):
        if self._exportable is None:
            if self.name.startswith( '__' ):
                self._exportable_reason = messages.W1000
            elif self.location and self.location.file_name == "<internal>":
                self._exportable_reason = messages.W1001
            elif self.is_artificial \
                 and not isinstance( self, ( declarations.class_t, declarations.enumeration_t ) ):
                self._exportable_reason = messages.W1002
            else:
                self._exportable_reason = self._exportable_impl( )
            self._exportable = not bool( self._exportable_reason )
        return self._exportable
    def set_exportable( self, exportable ):
        self._exportable = exportable

    exportable = property( get_exportable, set_exportable
                          , doc="Returns True if declaration could be exported to Python, otherwise False" )

    def _readme_impl( self ):
        return []

    def readme( self ):
        """This function will returns some hints/tips/description of problems
        that applied to the declarations. For example function that has argument
        reference to some fundamental type could be exported, but could not be called
        from Python
        """
        text = []
        if not self.exportable:
            text.append( self.why_not_exportable() )
        text.extend( self._readme_impl() )
        return text
