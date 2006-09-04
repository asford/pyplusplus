# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import autoconfig
from pygccxml import parser
from pygccxml import declarations
from pyplusplus import code_creators
from pyplusplus import module_creator
from pyplusplus import module_builder
from pyplusplus import utils as pypp_utils

class indent_tester_t(unittest.TestCase):
    def test( self ):
        indent = code_creators.code_creator_t.indent
        self.failUnless( '    abc' == indent('abc') )

class make_flatten_tester_t(unittest.TestCase):
    def test(self):
        mb = module_builder.module_builder_t(
                [ module_builder.create_text_fc( 'namespace enums{ enum { OK=1 }; }' ) ]
                , gccxml_path=autoconfig.gccxml.executable )
        mb.namespace( name='::enums' ).include()
        mb.build_code_creator('dummy')
        flatten = code_creators.make_flatten(mb.code_creator.creators)
        self.failUnless( filter( lambda inst: isinstance( inst, code_creators.unnamed_enum_t ), flatten ) )

class creator_finder_tester_t( unittest.TestCase ):
    def test_find_by_declaration(self):
        mb = module_builder.module_builder_t(
            [ module_builder.create_text_fc( 'namespace enums{ enum color{ red = 1}; }' )]
            , gccxml_path=autoconfig.gccxml.executable )
        mb.namespace( name='::enums' ).include()
        enum_matcher = declarations.match_declaration_t( name='color' )
        mb.build_code_creator( 'dummy' )
        enum_found = code_creators.creator_finder.find_by_declaration(
                        enum_matcher
                        , mb.code_creator.creators )
        self.failUnless( enum_found )

    def test_find_by_class_instance(self):
        mb = module_builder.module_builder_t(
            [ module_builder.create_text_fc( 'namespace enums{ enum color{ red = 1}; }' )]
            , gccxml_path=autoconfig.gccxml.executable )
        mb.namespace( name='::enums' ).include()
        mb.build_code_creator('dummy')
        enum_found = code_creators.creator_finder.find_by_class_instance(
            code_creators.enum_t
            , mb.code_creator.creators
            , recursive=True)
        self.failUnless( enum_found )

class class_organizer_tester_t(unittest.TestCase):
    def __init__(self, *args ):
        unittest.TestCase.__init__(self, *args)

    def _findout_base_classes(self, class_inst ):
        answer = []
        for base in class_inst.bases:
            answer.append( base.related_class )
            answer.extend( self._findout_base_classes( base.related_class ) )
        return answer

    def test(self):
        config = parser.config_t( gccxml_path=autoconfig.gccxml.executable )
        code = []
        code.append('struct a{};')
        code.append('struct b{};')
        code.append('struct c{};')
        code.append('struct d : public a{};')
        code.append('struct e : public a, public b{};')
        code.append('struct f{};')
        code.append('struct g : public d, public f{};')
        code.append('struct h : public f{};')
        code.append('struct i : public h, public g{};')
        code.append('struct j{};')
        code.append('struct k{};')

        global_ns = parser.parse_string( os.linesep.join( code ), config )
        decls = global_ns[0].declarations
        dorder = module_creator.findout_desired_order( decls )
        self.failUnless( len( code ) == len( dorder ), 'all classes should stay within the list' )
        for i in range( 1, len(dorder) ):
            bases = set( self._findout_base_classes( dorder[i] ) )
            exported = set( dorder[:i])
            self.failUnless( bases.issubset( exported )
                             , 'for derived class %s not all base classes have been exported' % dorder[i].name )

class exclude_function_with_array_arg_tester_t( unittest.TestCase ):
    def test(self):
        mb = module_builder.module_builder_t(
            [ module_builder.create_text_fc( 'namespace arr{ struct x{ x( int arr[3][3], int ){} x( const x arr[3][3], int ){} }; }' )]
            , gccxml_path=autoconfig.gccxml.executable )
        arr = mb.namespace( name='arr' )
        mem_funs = arr.calldefs( 'x', arg_types=[None,None] )
        for x in mem_funs:
            self.failUnless( x.exportable == False )

class readme_tester_t( unittest.TestCase ):
    CODE = \
    """
    namespace xxx{
        int do_smth(int);
        typedef int Int;
        struct data_t{
            data_t& operator--(int a);
        };
    }
    """
    def test(self):
        mb = module_builder.module_builder_t(
            [ module_builder.create_text_fc( self.CODE )]
            , gccxml_path=autoconfig.gccxml.executable )
        xxx = mb.namespace( name='xxx' )
        fun = xxx.calldef( 'do_smth' )
        self.failUnless( fun.readme() == [] )
        minus_minus = xxx.operator( symbol='--' )
        self.failUnless( 1 == len( minus_minus.readme() ), os.linesep.join( minus_minus.readme() ) )

class class_multiple_files_tester_t(unittest.TestCase):
    CLASS_DEF = \
    """
    namespace tester{
    struct X{
        enum EColor{ red, blue };
        enum EFruit{ apple, orange };

        X(){}
        X( int ){}

        void do_nothing(){}

        int do_somghing(){ return 1; }

        int m_dummy;
    };
    }
    """
    def test(self):
        mb = module_builder.module_builder_t(
                [ module_builder.create_text_fc( self.CLASS_DEF ) ]
                , gccxml_path=autoconfig.gccxml.executable )
        mb.namespace( name='::tester' ).include()
        X = mb.class_( 'X' )
        X.add_declaration_code( '//hello world' )
        mb.build_code_creator('dummy')
        mb.split_module( autoconfig.build_dir
                        , [ mb.class_( '::tester::X' ) ]
                        , on_unused_file_found=lambda fpath: fpath )


class split_sequence_tester_t(unittest.TestCase):
    def test(self):
        seq = [ 1,2,3 ]
        split = pypp_utils.split_sequence
        self.failUnless( [[1],[2],[3]] == split( seq, 1 ) )
        self.failUnless( [[1,2],[3]] == split( seq, 2 ) )
        self.failUnless( [[1,2,3]] == split( seq, 3 ) )
        self.failUnless( [[1,2,3]] == split( seq, 4 ) )

class doc_extractor_tester_t( unittest.TestCase ):
    def test( self ):
        escaped_doc = module_builder.doc_extractor_i.escape_doc('Hello "Py++"')
        self.failUnless( escaped_doc == '"Hello \\"Py++\\""' )

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(doc_extractor_tester_t))
    suite.addTest( unittest.makeSuite(class_organizer_tester_t))
    suite.addTest( unittest.makeSuite(indent_tester_t))
    suite.addTest( unittest.makeSuite(make_flatten_tester_t))
    suite.addTest( unittest.makeSuite(creator_finder_tester_t))
    suite.addTest( unittest.makeSuite(exclude_function_with_array_arg_tester_t))
    suite.addTest( unittest.makeSuite(class_multiple_files_tester_t))
    suite.addTest( unittest.makeSuite(readme_tester_t))
    suite.addTest( unittest.makeSuite(split_sequence_tester_t))


    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
