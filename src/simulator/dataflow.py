import json 

class Dataflow( object ):

    def __init__( self, nn_config_file, pe_config_file, buffer_config_file, ram_config_file ):
        
        self.nn_config_file = nn_config_file
        self.pe_config_file = pe_config_file 
        self.buffer_config_file = buffer_config_file 
        self.ram_config_file = ram_config_file 

    def parse_nn_config( self ):
        pass 
    def parse_pe_config( self ):
        pass
    def parse_buffer_config( self ):
        pass
    def parse_ram_config( self ):
        pass
    
