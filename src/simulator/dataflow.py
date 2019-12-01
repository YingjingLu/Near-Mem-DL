import json 
import math
from solver import * 
from hmc import HMC

W_TIME, F_TIME = 0, 1
MAC, BUFFER_ACCESS, REG_ACCESS, BUS_ACCESS, CROSS_VAULT = 0, 1, 2, 3, 4

class Dataflow( object ):

    def __init__( self, nn_config_file, pe_config_file, buffer_config_file, ram_config_file, bit_unit = 16 ):
        
        # get config files
        self.nn_config_file = nn_config_file
        self.pe_config_file = pe_config_file 
        self.buffer_config_file = buffer_config_file 
        self.ram_config_file = ram_config_file 
        
        # key attribute
        self.bit_unit = bit_unit
        self.layer_stack = None # The layers sorted in topological order

        # parse configs
        self.parse_nn_config()
        self.parse_pe_config()
        self.parse_ram_config()

        self.mem_vault_to_layer = dict() # vault_idx, layer_idx 
        self.mem_layer_to_vault = {i:[] for i in range( self.total_vault )} # layer_idx: [ vault1 vault 2 ]


        self.layer_to_idx = dict()
        self.idx_to_layer = dict()
        

    def run_net( self ):
        """
        keep poping the fmap from the fmap_queue,
        load current layer weights,
        do calculation 
        and write the resulting fmap partials back to the memory

        """
        layer_index = 0
        cur_vault = 0
        self.vault_time = [ [ 0, 0 ]  for i in range( self.total_vault ) ] # weight time , feature time
        # compute MAC, buffer access, reg_access, bus access, cross vaule access
        self.vault_energy = [ [ 0, 0, 0, 0, 0 ] for _ in range( self.vault_shape[ 0 ] * self.vault_shape[ 1 ] ) ]
        self.mem_topo = dict() # layer: vault_idx: [ [ pe_start, pe_end, cur_time, op_time ] ]


        """
        use different strategy for cases when all weights could be loaded into chips or not
        """
        cur_vault = 0
        while layer_index != len( self.layer_stack ):
            cur_layer = self.layer_stack[ layer_index ]
            if cur_layer[ "type" ] == "CONV":
                cur_vault = self.load_weight_conv( cur_vault, layer_index )
            elif cur_layer[ "type" ] == "FC":
                cur_vault = self.load_weight_fc( cur_vault, layer_index )
        
        if cur_vault >= self.total_vault:
            all_load = False 
        else:
            # if all load, reset weight loading time
            all_load = True 
            self.vault_time = [ [ 0, 0 ]  for i in range( self.total_vault ) ]
        
        while layer_index != len( self.layer_stack ):
            cur_layer = self.layer_stack[ layer_index ]
            cur_layer_name = cur_layer[ "name" ]
            if cur_layer[ "type" ] == "INPUT":
                self.place_input_in_ram( cur_vault )
                cur_vault = 0

            elif cur_layer[ "type" ] == "CONV":
                cur_vault = self.process_conv( cur_vault, layer_index, all_load )

            elif cur_layer[ "type" ] == "FC":
                cur_vault = self.process_fc( cur_vault, layer_index, all_load ) 

    def place_input_in_ram( self, cur_pe ):
        cur_pe = 0
        input_name = self.layer_stack[ 0 ][ "name" ]
        self.mem_topo[ input_name ] = dict()
        prev_vault = 0
        cur_vault= 0
        pe_start = 0
        max_new_time = 0
        if self.layer_stack[ 1 ][ "type" ] == "FC":
            input_row, input_col = self.layer_stack[ 0 ][ "out_shape" ]
            for col in range( input_col ):
                remain = input_row % self.pe_width 
                consume = input_row // self.pe_width 
                if remain > 0:
                    consume += 1
                for _ in range( consume ):
                    cur_pe += 1
                    vault_idx = self.vault_idx_from_pe_idx( cur_pe )
                    # if filled a vault them calculate its time and update memory location topo
                    if prev_vault != vault_idx:
                        new_time = self.hmc.pe_mem_access( cur_time, cur_pe - pe_start, self.pe_width, vault_idx, vault_idx )
                        prev_vault = vault_idx 
                        max_new_time = max( max_new_time, new_time )
                        if vault_idx not in self.mem_topo[ input_name ]:
                            self.mem_topo[ input_name ][ vault_idx ] = []
                        self.mem_topo[ input_name ][ vault_idx ].append( [ pe_start, cur_pe -1, 1 ] )
                        self.vault_time[ vault_idx ][ F_TIME ] = new_time
                        pe_start = cur_pe
                    # if filled enough for the first round, then reset curtime
                    if cur_pe == self.total_pe:
                        cur_time = max_new_time
                        cur_pe = 0
        elif self.layer_stack[ 1 ][ "type" ] == "CONV":
            input_row, input_col, input_z = self.layer_stack[ 0 ][ "out_shape" ]
            stride = self.layer_stack[ 1 ][ "config" ][ "stride" ]
            stride_v, stride_h = stride[ 1 ], stride[ 2 ]
            weight = self.layer_stack[ 1 ][ "config" ][ "weight_shape" ]
            weight_v, weight_h = weight[ 0 ], weight[ 1 ]
            cur_vault = 0
            # calculate fmap assigned to each vault, truncated overlapping
            per_vault_v, per_vault_h = weight_v + (self.vault_shape[ 0 ] - 1) * stride_v - ( weight_v + stride_v), \
                                       weight_h + (self.vault_shape[ 1 ] - 1) * stride_h - ( weight_h + stride_h )
            
            # calculate num_pe used
            self.mem_topo[ input_name ] = dict()
            for z in range( input_z ):
                num_row, num_col = math.ceil( input_row / per_vault_v ), math.ceil( input_col / per_vault_h )
                for row in range( num_row ):
                    for col in range( num_col ):
                        new_time = self.hmc.pe_mem_access( cur_time, cur_pe - pe_start, self.pe_width, vault_idx, vault_idx )
                        max_new_time = max( max_new_time, new_time )
                        if cur_vault not in self.mem_topo[ input_name ]:
                            self.mem_topo[ input_name ] = []
                        self.mem_topo[ input_name ][ cur_vault ].append( [ cur_vault * self.pe_per_vault, ( cur_vault + 1 ) * self.pe_per_vault, 1 ] )
                        self.vault_time[ cur_vault ][ F_TIME ] = new_time
                        cur_vault += 1
                        if cur_vault == self.total_vault:
                            cur_time = max_new_time
                            cur_vault = 0

    def process_conv( self, cur_vault, layer_idx, all_load ):
        """
        do current processing,
        rotate within vault 
        rotate across vaule 
        
        load feature map
        load weight 

        for each of the comp, in vaule, count the calculation, update current pe time, count the bus 
        """
        cur_layer = self.layer_stack[ layer_idx ]
        if all_load:
            pass
        if self.mem_layer_to_vault[ layer_idx ] != []:
            self.load_weight_fc( cur_vault, layer_idx )
        mem_list = self.mem_layer_to_vault[ layer_idx ]
        # load input
        for weight_vault in mem_list:
            true_weight_vault = weight_vault % self.total_vault
            for input_name in cur_layer[ "in_layer" ]:
                for fmap_vault in self.mem_topo[ input_name ]:
                    true_fmap_vault = fmap_vault % self.total_vault
                    self.calc_conv( true_weight_vault, true_fmap_vault )
        self.assign_conv_omap( mem_list[ 0 ], layer_idx )
        return weight_vault

    def load_weight_conv( self, cur_vault, layer_idx ):
        layer = self.layer_stack[ layer_idx ]
        row, col, z = layer[ "config" ][ "weight_shape" ]
        num_channel_per_pe = self.pe_width // row 
        num_channel_contained = self.arr_shape[ 0 ] // row* self.arr_shape[ 1 ] // col
        vault_list = []
        for _ in range( math.ceil( z / num_channel_per_pe / num_channel_contained ) ):
            num_pe = row * col * num_channel_per_pe 
            true_vault_idx = cur_vault % self.total_vault 
            prev_time = self.vault_time[ true_vault_idx ][ W_TIME ]
            new_time = self.hmc.pe_mem_access( prev_time, num_pe, self.pe_width, true_vault_idx, true_vault_idx )
            self.vault_time[ true_vault_idx ][ W_TIME ] = new_time
            vault_list.append( true_vault_idx )
            self.mem_vault_to_layer[ true_vault_idx ] = layer_idx
            cur_vault += 1
            
        self.mem_layer_to_vault[ layer_idx ] = vault_list 
        return cur_vault 

    def load_weight_fc( self, cur_vault, layer_idx ):
        layer = self.layer_stack[ layer_idx ]
        row, col = layer[ "config" ][ "weight_shape" ]
        vault_list = []

        for c in col:
            num_pe = math.ceil( row / self.pe_width )
            num_vault = math.ceil( num_pe / self.pe_per_vault )
            for i in range( num_vault ):
                true_vault_idx = ( cur_vault + i ) % self.total_vault
                pe_loaded_num = min( self.pe_per_vault, num_pe - self.pe_per_vault * i )
                prev_time = self.vault_time[ true_vault_idx ][ W_TIME ]
                new_time = self.hmc.pe_mem_access( prev_time, pe_loaded_num, self.pe_width, true_vault_idx, true_vault_idx )
                self.vault_time[ true_vault_idx ][ W_TIME ] = new_time
                vault_list.append( true_vault_idx )
                self.mem_vault_to_layer[ true_vault_idx ] = layer_idx
            cur_vault += num_vault 
        self.mem_layer_to_vault[ layer_idx ] = vault_list 
        
        return cur_vault 


    def process_fc( self, cur_vault, layer_idx, all_load ):
        cur_layer = self.layer_stack[ layer_idx ]
        
        # load weight
        if self.mem_layer_to_vault[ layer_idx ] != []:
            self.load_weight_fc( cur_vault, layer_idx )
        mem_list = self.mem_layer_to_vault[ layer_idx ]
        # load input
        for weight_vault in mem_list:
            true_weight_vault = weight_vault % self.total_vault
            for input_name in cur_layer[ "in_layer" ]:
                for fmap_vault in self.mem_topo[ input_name ]:
                    true_fmap_vault = fmap_vault % self.total_vault
                    self.calc_fc( true_weight_vault, true_fmap_vault )
        self.assign_fc_omap( mem_list[ 0 ], layer_idx )
        return weight_vault
    
    def calc_fc( self, true_weight_vault, true_fmap_vault ):
        if true_fmap_vault != true_weight_vault:
            self.vault_energy[ BUFFER_ACCESS ] += 1
            self.vault_energy[ CROSS_VAULT ] += 1
        num_op = self.arr_shape[ 0 ] * ( ( self.arr_shape[ 1 ] ) // 2 ) + self.arr_shape[ 1 ] * ( self.arr_shape[ 0 ] // 2 )
        bus_op = ( self.arr_shape[ 0 ] - 1 ) * ( ( self.arr_shape[ 1 ] - 1 )**2 // 2 ) + ( self.arr_shape[ 1 ] - 1)  * ( ( self.arr_shape[ 0 ] - 1 )**2 // 2 )
        self.vault_energy[ MAC ] += num_op 
        self.vault_energy[ BUFFER_ACCESS ] += num_op 
        self.vault_energy[ BUS_ACCESS ] += bus_op 

    def calc_conv( self, true_weight_vault, true_fmap_vault ):
        if true_fmap_vault != true_weight_vault:
            self.vault_energy[ BUFFER_ACCESS ] += 1
            self.vault_energy[ CROSS_VAULT ] += 1
        num_op = self.arr_shape[ 0 ] * ( ( self.arr_shape[ 1 ] )**2 // 2 ) + self.arr_shape[ 1 ] * ( self.arr_shape[ 0 ]**2 // 2 )
        bus_op = ( self.arr_shape[ 0 ] - 1 ) * ( ( self.arr_shape[ 1 ] - 1 )**2 // 2 ) + ( self.arr_shape[ 1 ] - 1)  * ( ( self.arr_shape[ 0 ] - 1 )**2 // 2 )
        self.vault_energy[ MAC ] += num_op 
        self.vault_energy[ BUFFER_ACCESS ] += num_op 
        self.vault_energy[ BUS_ACCESS ] += bus_op 
    
    def assign_fc_omap( self, start_vault, layer_idx ):
        row = self.layer_stack[ layer_idx ][ "out_shape" ][ 0 ]
        name = self.layer_stack[ layer_idx ][ "name" ]
        self.mem_topo[ name ] = dict()
        num_pe = math.ceil( row / self.pe_width )
        num_vault = math.ceil( num_pe / self.pe_per_vault )
        for i in range( num_vault ):
            true_idx = ( start_vault + i ) % self.total_vault
            self.vault_energy[ true_idx ][ CROSS_VAULT ] += 1
            self.hmc.pe_mem_access( 0, min( self.pe_per_vault, num_pe - i * self.pe_per_vault ), self.pe_width, true_idx, true_idx )
            if true_idx not in self.mem_topo[ name ]:
                self.mem_topo[ name ][ true_idx ] = []
            self.mem_topo[ name ][ true_idx ].append( [ "TODO" ] )
             
    def assign_conv_omap( self, start_vault, layer_idx ):
        input_row, input_col, input_z = self.layer_stack[ layer_idx ][ "out_shape" ]
        for z in range( input_z ):
            num_row, num_col = math.ceil( input_row / per_vault_v ), math.ceil( input_col / per_vault_h )
            for row in range( num_row ):
                for col in range( num_col ):
                    max_new_time = max( max_new_time, new_time )
                    if cur_vault not in self.mem_topo[ input_name ]:
                        self.mem_topo[ input_name ] = []
                    self.mem_topo[ input_name ][ cur_vault ].append( [ cur_vault * self.pe_per_vault, ( cur_vault + 1 ) * self.pe_per_vault, 1 ] )
                    self.vault_time[ cur_vault ][ F_TIME ] = new_time
                    cur_vault += 1
                    if cur_vault == self.total_vault:
                        cur_time = max_new_time
                        cur_vault = 0
        num_pe = math.ceil( row / self.pe_width )
        num_vault = math.ceil( num_pe / self.pe_per_vault )
        for i in range( num_vault ):
            true_idx = ( start_vault + i ) % self.total_vault
            self.vault_energy[ true_idx ][ CROSS_VAULT ] += 1
            self.hmc.pe_mem_access( 0, min( self.pe_per_vault, num_pe - i * self.pe_per_vault ), self.pe_width, true_idx, true_idx )

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
        self.vault_shape = [ pe_config[ "tile_row" ], pe_config[ "tile_col" ]  ]
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

        self.vault_buffer_size = pe_config[ "vault_buffer_size" ]

        self.vault_col = self.pe_width * self.arr_shape[ 1 ]
        self.vault_row = self.arr_shape[ 0 ]

        self.pe_per_vault = self.arr_shape[ 0 ]* self.arr_shape[ 1 ]
        self.total_pe = self.pe_per_vault * self.vault_shape[ 0 ] * self.vaule_shape[ 1 ]

        self.per_vault_op = self.vault_row * self.vault_col 

        self.total_col = self.vault_col * self.vault_shape[ 1 ]
        self.total_row = self.vault_row * self.vault_shape[ 0 ]

        self.per_total_op = self.total_row * self.total_col 
        self.total_vault = self.vault_shape[ 0 ] * self.vault_shape[ 1 ]

    def parse_ram_config( self ):
        self.hmc = HMC( self.ram_config_file, self.bit_unit )

    def topo_sort_layers( self, l ):
        # name, count
        incoming =  dict()
        # name: [ name ]
        outgoing = dict()
        name_dict = dict()
        
        queue = []
        for idx, layer in enumerate( l ):
            name = layer[ "name" ]
            self.layer_to_idx[ name ] = idx 
            self.idx_to_layer[ idx ] = name
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
    # def load_fc_weights( self ):
    #     layer_index = 0
        
    #     total_vault_row, total_vault_col = self.vault_shape 
    #     vault_row, vault_col = 0, 0
    #     cur_pe = 0
    #     cur_vault = 0
    #     while layer_index != len( self.layer_stack ):
    #         layer = self.layer_stack[ layer_index ]
    #         if layer[ "type" ] == "FC":
    #             total_layer_row, total_layer_col = layer[ "config" ][ "weight_shape" ]
                
    #             for layer_col_index in range( total_layer_col ):
    #                 remain = total_layer_row % self.pe_width 
    #                 consume = total_layer_row // self.pe_width 
    #                 if remain > 0:
    #                     consume += 1
    #                 for delta_pe in range( consume ):
    #                     pe_idx = cur_pe + delta_pe 
    #                     vault_idx = self.vault_idx_from_pe_idx( pe_idx )
    #                     pe_inner_idx = self.pe_inner_idx_from_pe_idx( pe_idx )
    #                 cur_pe += consume 
    #             # reset for every layer and load them separately
    #         layer_index += 1

    def vault_idx_from_pe_idx( self, pe ):
        pe = pe % self.total_pe
        return math.ceil( pe / self.pe_per_vault )

    def pe_inner_idx_from_pe_idx( self, pe ):
        pe = pe % self.total_pe
        prev_vault = math.floor( pe / self.pe_per_vault )
        pe -= prev_vault * self.pe_per_vault
        return pe








