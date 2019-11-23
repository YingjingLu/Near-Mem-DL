import json 
from solver import * 
class Dataflow( object ):

    def __init__( self, nn_config_file, pe_config_file, buffer_config_file, ram_config_file, bit_unit = 16 ):
        
        self.nn_config_file = nn_config_file
        self.pe_config_file = pe_config_file 
        self.buffer_config_file = buffer_config_file 
        self.ram_config_file = ram_config_file 
        self.bit_unit = bit_unit

    def parse_nn_config( self ):
        with open( self.nn_config_file, "r" ) as f:
            nn_dict = json.load( f )
            self.layer_list = nn_dict[ "layers" ]
            self.bach_size = nn_dict[ "batch_size" ]
            self.nn_name = nn_dict[ "nn_name" ]

    def parse_pe_config( self ):
        with open( self.pe_config_file, "r" ) as f:
            pe_config = json.load( f )
        self.tile_shape = [ pe_config[ "tile_row" ], pe_config[ "tile_col" ]  ]
        self.gbuf = pe_config[ "gbuf" ]
        self.arr_shape = [ pe_config[ "arr_row" ], pe_config[ "arr_col" ] ]
        self.pe_width = pe_config[ "pe_width" ]
        self.pe_clock = pe_config[ "pe_clock" ]
        self.pe_energy = pe_config[ "pe_energy" ]
        self.pe_noc = pe_config[ "pe_noc" ]
        self.reg_read_energy = pe_config[ "reg_read_energy" ]
        self.reg_read_latency = pe_config[ "reg_read_latency" ]
        self.reg_write_energy = pe_config[ "reg_write_energy" ]
        self.reg_write_latency = pe_config[ "reg_write_latency" ]

        self.tile_col = self.pe_width * self.arr_shape[ 1 ]
        self.tile_row = self.arr_shape[ 0 ]

        self.total_col = self.tile_col * self.tile_shape[ 1 ]
        self.total_row = self.tile_row * self.tile_shape[ 0 ]
        

    # def parse_buffer_config( self ):
    #     pass

    def parse_ram_config( self, hmc ):
        self.hmc = hmc

