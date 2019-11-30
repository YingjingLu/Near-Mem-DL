import json 
from solver import * 
from hmc import HMC
class Dataflow( object ):

    def __init__( self, nn_config_file, pe_config_file, buffer_config_file, ram_config_file, bit_unit = 16 ):
        
        self.nn_config_file = nn_config_file
        self.pe_config_file = pe_config_file 
        self.buffer_config_file = buffer_config_file 
        self.ram_config_file = ram_config_file 
        self.bit_unit = bit_unit

        self.load_weight()
        self.load_input()
        self.do_calculation_place_partial()


    def load_weight( self ):
        """
        determine which part of the weight is placed in which vault
        for lowest amount memory access
        """
        self.load_fc_weights()
        self.load_conv_weights()

    def load_input( self ):
        """
        load input into the memory and plac eit into the incoming fmap queue
        """
        pass 
    def do_calculation_place_partial( self ):
        """
        keep poping the fmap from the fmap_queue,
        load current layer weights,
        do calculation 
        and write the resulting fmap partials back to the memory

        """
        pass 


    def parse_nn_config( self ):
        with open( self.nn_config_file, "r" ) as f:
            nn_dict = json.load( f )
            self.layer_stack = nn_dict[ "layers" ]
            self.bach_size = nn_dict[ "batch_size" ]
            self.nn_name = nn_dict[ "nn_name" ]
        
        # perform topological sort to determine dependency graph among layers
        self.layer_stack = self.topo_sort_layers( self.layer_stack )

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

    def parse_ram_config( self ):
        self.hmc = HMC( self.ram_config_file, self.bit_unit )

    def topo_sort_layers( self, list ):
        # name, count
        incoming =  dict()
        # name: [ name ]
        outgoing = dict()
        name_dict = dict()
        
        queue = []
        for layer in list:
            name = layer[ "name" ]
            name_dict[ name ] = layer 
            if layer[ "type" ] == "INPUT":
                incoming[ name ] = 0
                queue.append( layer )
            else:
                incoming[ name ] = len( layer[ in_layer ] )
                for in_layer in layer[ "in_layer" ]:
                    outgoing[ in_layer ].add( name )
            outgoing[ name ] = set() 
        res = []
        while len( queue ) != 0:
            l = queue.pop()
            res.append( l )
            for out in outgoing[ l ]:
                incoming[ out ] -= 1
                if incoming[ out ] == 0:
                    queue.append( out )
        return res

    # handle fc layers
    def load_fc_weights( self ):
        pass 
    
    def load_fc_weight_in_vault( self, vault,  )
    # handle conv layers
    def load_conv_weights( self ):
        pass 





