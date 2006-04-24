// This file has been generated by pyplusplus.

// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include "boost/python.hpp"
#ifdef _MSC_VER
    #pragma hdrstop
#endif //_MSC_VER

#include "unittests/data/free_operators_to_be_exported.hpp"

namespace bp = boost::python;

BOOST_PYTHON_MODULE(free_operators){
    bp::class_< free_operators::number >( "number" )    
        .def_readwrite( "i", &free_operators::number::i )    
        .def( !bp::self )    
        .def( bp::self + bp::other< int >() );
}
