// This file has been generated by pyplusplus.

// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include "boost/python.hpp"
#ifdef _MSC_VER
    #pragma hdrstop
#endif //_MSC_VER

#include "unittests/data/class_order3_to_be_exported.hpp"

namespace bp = boost::python;

BOOST_PYTHON_MODULE(class_order3){
    if( true ){
        typedef bp::class_< class_order3::consts > consts_exposer_t;
        consts_exposer_t consts_exposer = consts_exposer_t( "consts" );
        bp::scope consts_scope( consts_exposer );
        bp::enum_<class_order3::consts::fruits>("fruits")
            .value("orange", class_order3::consts::orange)
            .value("apple", class_order3::consts::apple)
            .export_values()
            ;
    }

    bp::class_< class_order3::container >( "container", bp::init< bp::optional< class_order3::consts::fruits > >(( bp::arg("x")=class_order3::consts::apple ))[bp::default_call_policies()] )    
        .def_readwrite( "my_fruit", &class_order3::container::my_fruit );

    bp::implicitly_convertible< class_order3::consts::fruits, class_order3::container >();
}
