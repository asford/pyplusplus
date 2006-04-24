// This file has been generated by pyplusplus.

// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include "boost/python.hpp"
#ifdef _MSC_VER
    #pragma hdrstop
#endif //_MSC_VER

#include "unittests/data/operators_bug_to_be_exported.hpp"

namespace bp = boost::python;

BOOST_PYTHON_MODULE(operators_bug){
    bp::class_< operators_bug::number<operators_bug::integral,int> >( "number_less_operators_bug_scope_integral_comma_int_grate_" )    
        .def_readwrite( "value", &operators_bug::number<operators_bug::integral,int>::value );

    bp::class_< operators_bug::integral2, bp::bases< operators_bug::number<operators_bug::integral,int> > >( "integral2" );

    bp::class_< operators_bug::integral, bp::bases< operators_bug::number<operators_bug::integral,int> > >( "integral" )    
        .def( bp::self + bp::other< int >() )    
        .def( bp::self + bp::self );
}
