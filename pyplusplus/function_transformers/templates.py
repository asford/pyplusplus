# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# Matthias Baas is an initial author of the templates.

"""defines few templates, which will be used to create a function-wrapper
definition."""

import os
from string import Template


class sealed_fun: 
    body = Template( os.linesep.join([
          'static $return_type $unique_function_name( $arg_declarations ){'
        , '    $declare_variables'
        , '    $pre_call'
        , '    $save_result$function_name($arg_expressions);'
        , '    $post_call'
        , '    $return'
        , '}'
    ]))

class virtual_mem_fun:    
    override = Template( os.linesep.join([
          'virtual $return_type $function_name( $arg_declarations )$constness $throw{'
        , '    namespace bpl = boost::python;'
        , '    if( bpl::override $py_function_var = this->get_override( "$function_alias" ) ){'
        , '        $declare_py_variables'
        , '        $py_pre_call'
        , '        ${save_py_result}bpl::call<bpl::object>( $py_function_var.ptr()$py_arg_expressions );'
        , '        $py_post_call'
        , '        $py_return'
        , '    }'
        , '    else{'
        , '        $cpp_return$wrapped_class::$function_name( $cpp_arg_expressions );'
        , '    }'
        , '}'
    ]))
    
    default = Template( os.linesep.join([
          'static $return_type $unique_function_name( $arg_declarations ){'
        , '    $declare_variables'
        , '    $pre_call'
        , '    if( dynamic_cast< $wrapper_class $wrapped_inst_constness* >( boost::addressof( $wrapped_inst ) ) ){'
        , '        $save_result$wrapped_inst.$wrapped_class::$function_name($arg_expressions);'
        , '    }'
        , '    else{'
        , '        $save_result$wrapped_inst.$function_name($arg_expressions);'
        , '    }'
        , '    $post_call'
        , '    $return'
        , '}'
    ]))


def substitute( text, **keywd ):
    return Template( text ).substitute( **keywd )
    
