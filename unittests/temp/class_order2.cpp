// This file has been generated by pyplusplus.

// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include "boost/python.hpp"
#ifdef _MSC_VER
    #pragma hdrstop
#endif //_MSC_VER

#include "unittests/data/class_order2_to_be_exported.hpp"

namespace bp = boost::python;

BOOST_PYTHON_MODULE(class_order2){
    bp::class_< class_order2::S1 >( "S1" )    
        .def( "do_smth"
                , (void ( ::class_order2::S1::* )( ::class_order2::S2 * ) )(&class_order2::S1::do_smth)
                , ( bp::arg("s2")=bp::object() )
                , bp::default_call_policies() )    
        .def( "do_smth"
                , (void ( ::class_order2::S1::* )( double,::class_order2::S2 * ) )(&class_order2::S1::do_smth)
                , ( bp::arg("d"), bp::arg("s2")=bp::object() )
                , bp::default_call_policies() );

    bp::class_< class_order2::S2 >( "S2" )    
        .def( "do_smth"
                , (void ( ::class_order2::S2::* )( ::class_order2::S1 * ) )(&class_order2::S2::do_smth)
                , ( bp::arg("S1")=bp::object() )
                , bp::default_call_policies() )    
        .def( "do_smth"
                , (void ( ::class_order2::S2::* )( double,::class_order2::S1 * ) )(&class_order2::S2::do_smth)
                , ( bp::arg("d"), bp::arg("S1")=bp::object() )
                , bp::default_call_policies() );
}
