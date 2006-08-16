# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

class user_text_t(object):
    def __init__( self, text ):
        object.__init__( self )
        self.text = text

class class_user_text_t( user_text_t ):
    def __init__( self, text, works_on_instance=True ):
        """works_on_instance: If true, the custom code can be applied directly to obj inst.
           Ex: ObjInst."CustomCode"
        """
        user_text_t.__init__( self, text )
        self.works_on_instance = works_on_instance