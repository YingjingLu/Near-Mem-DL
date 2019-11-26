from mem_solver import * 
import math 

COV = 1024

class HMC( object ):
    def __init__( self, config, bit_unit, mode = "naive" ):
        self.config = config 
        self.bit_unit = bit_unit
        self.mode = mode
        # spec short cut 
        self.total_size = self.config[ "config" ][ "size" ]
        self.num_bank = self.config[ "config" ][ "num_bank" ]
        self.num_layer = self.config[ "config" ][ "stacked_die_count" ]
        self.num_vault = self.config[ "config" ][ "num_vault" ]
        self.subarray_row = self.config[ "config" ][ "subarray_row" ]
        self.subarray_col = self.config[ "config" ][ "subarray_col" ]
        self.subarray_row_word = self.subarray_row // self.bit_unit 
        self.subarray_col_word = self.subarray_col // self.bit_unit 

        # calc derived spec 
        self.subarray_per_bank = self.calc_subarray_per_bank()
        self.cas_latency = self.calc_cas_latency()
        self.ras_latency = self.calc_ras_latency()
        self.cas_energy = self.calc_cas_energy()
        self.ras_energy = self.calc_ras_energy()
        self.local_bus_latency = self.calc_local_bus_latency()
        self.local_bus_energy = self.calc_local_bus_energy()
        self.cross_vault_bus_latency = self.calc_cross_vault_bus_latency()
        # stat
        self.num_row_access = 0
        self.num_col_access = 0
        self.num_cross_vault_access = 0

        self.read_bit = 0
        self.write_bit = 0
        self.cross_vault_read_bit = 0
        self.cross_vault_write_bit = 0

        # vault, layer, bank, subarray
        self.bank_wise_access = \
            [
                [
                    [
                        [ 
                            0 for _ in range( self.subarray_per_bank ) 
                        ] for _ in range( self.num_bank ) \
                    ] for _ in range( self.num_layer ) \
                ] for _ in range( self.num_vault )\
            ]


        self.mem_topology = dict()
    
    def process_access( self, trace ):
        raw = trace.strip().split( "," ) 
        raw[ 2 ] = float( raw[ 2 ] )
        for i in [ 3, 4, 6, 7, 8, 9 ]:
            raw[ i ] = int( raw[ i ] )
        if raw[ 0 ] == "weight":
            raw = raw[ 2: ]
            if self.mode == "naive":
                self.naive_mem_access_weight( *raw )
        elif raw[ 0 ] == "fmap":
            raw = raw[ 2: ]
            if self.mode == "naive":
                self.naive_mem_access_partial( *raw )
        else:
            NotImplementedError( "Access not implemented: {}".format( raw[ 0 ] ) )

    def get_summary( self ):
        ras_energy = self.num_row_access * self.ras_energy
        cas_energy = self.num_col_access * self.cas_energy

        ras_latency = self.num_row_access * self.ras_latency
        cas_latency = self.num_col_access * self.cas_latency

        cross_vault_bus_latency = self.cross_vault_bus_latency * self.num_cross_vault_access


        print(
            """
            Total row access: {}
            Total col access: {}
            Total memory acess: {} bits
            cross vault access: {}
            -----------------------------------------
            Energy
            Row access energy: {} nj
            Col access energy {} nj
            Total energy consumption: {} nj
            Unit energy {}: nj / bit
            -----------------------------------------
            Latency
            Row access latency: {} ns
            Col access latency: {} ns
            Cross vault access latency: {} ns
            Total letency: {} ns
            Unit latency: {} ns / bit
            """.format(
                self.num_row_access,
                self.num_col_access,
                self.num_col_access,
                self.num_cross_vault_access,

                ras_energy,
                cas_energy,
                ras_energy + cas_energy,
                ( ras_energy + cas_energy ) / self.num_col_access,

                ras_latency,
                cas_latency,
                cross_vault_bus_latency,
                ras_latency + cas_latency + cross_vault_bus_latency, 
                (ras_latency + cas_latency + cross_vault_bus_latency) / self.num_col_access,

            )
        )

    def naive_access( self, in_time, 
                            req_vault, dest_vault,
                            layer_name,
                            start_row, start_col, 
                            end_row, end_col ):
        """
        ignore spatial locality and treat every request in a per bit basis 
        """
        # calc access energy 
        bits = ( end_row - start_row ) * ( end_col - start_col ) *  self.bit_unit 
        row_access = math.ceil( bits / self.subarray_col )
        col_access = bits

        self.num_row_access += row_access
        self.num_col_access += col_access 

        if req_vault != dest_vault:
            self.num_cross_vault_access += 1
        
        delta_time = self.cas_latency * col_access + self.ras_latency * row_access
        return in_time + delta_time // 1e6
        
    def naive_mem_access_weight(  self,
                                in_time, 
                                req_vault, dest_vault, 
                                layer_name, 
                                start_row, start_col, 
                                end_row, end_col ):
        
        return self.naive_access( in_time, 
                                  req_vault, dest_vault, 
                                  layer_name, 
                                  start_row, start_col, 
                                  end_row, end_col )
    def naive_mem_access_partial( self,
                                in_time,
                                req_vault, dest_vault,
                                fmap_name,
                                start_row, start_col,
                                end_row, end_col ):
        return self.naive_access( in_time, 
                                  req_vault, dest_vault, 
                                  fmap_name, 
                                  start_row, start_col, 
                                  end_row, end_col )

    def mem_read_weight(    self,
                            in_time, 
                            req_vault, dest_vault, 
                            layer_name, 
                            start_row, start_col, 
                            end_row, end_col ):
        pass 
    
    def mem_read_partial( self,
                          in_time,
                          req_vault, dest_vault,
                          partial_name,
                          start_row, start_col,
                          end_row, end_col ):
        pass 

    def mem_write_weight(   self,
                            in_time, 
                            dest_vault, 
                            layer_name, 
                            start_row, start_col,
                            end_row, end_col ):
        pass 
    
    def mem_write_partial(      self,
                                in_time, 
                                dest_vault, 
                                fmap_name, 
                                start_row, start_col,
                                end_row, end_col ):
        pass 

    # subspec calculation in ns / bit, nj / bit
    def calc_cross_vault_bus_latency( self ):
        return 1.0e9 / self.GB_to_bits( self.config[ "bus" ][ "bandwidth" ] )

    
    def calc_subarray_per_bank( self ):
        total_bits = self.GB_to_bits( self.total_size )
        bits_per_vault = total_bits // self.num_vault
        bits_per_layer = bits_per_vault // self.num_layer
        bits_per_bank = bits_per_layer // self.num_bank 
        num_subarray = bits_per_bank // ( self.subarray_row * self.subarray_col )
        return num_subarray

    def calc_cas_latency( self ):
        """
        row_activation_bus_delay + row_predecoder_delay + row_decoder_delay
        + local_wordline_delay
        """
        delay = self.config[ "spec" ][ "timing" ]
        return delay[ "local_wordline_delay" ] \
               + delay[ "row_predecoder_delay" ] \
               + delay[ "row_decoder_delay" ] \
               + delay[ "local_wordline_delay" ]

    def calc_ras_latency( self ):
        """
        row_activation_bus_delay + row_predecoder_delay + row_decoder_delay
        + local_wordline_delay
        """
        latency = self.config[ "spec" ][ "timing" ]
        return latency[ "row_activation_bus_delay" ]\
                + latency[ "row_predecoder_delay" ]\
                + latency[ "row_decoder_delay" ] \
                + latency[ "local_wordline_delay" ]
    
    def calc_cas_energy( self ):
        """
        bitline_energy + sense_amp_energy + column_access_bus_energy 
        + column_predecoder_energy + column_selectline_energy
        """
        energy = self.config[ "spec" ][ "energy" ]
        return energy[ "bitline_energy" ] \
                + energy[ "sense_amp_energy" ] \
                + energy[ "column_access_bus_energy" ]\
                + energy[ "column_predecoder_energy" ]\
                + energy[ "column_selectline_energy" ]

    def calc_ras_energy( self ):
        """
        row_activation_bus_energy + row_predecoder_energy + row_decoder_energy
        + local_wordline_energy
        """
        energy = self.config[ "spec" ][ "energy" ]
        return energy[ "local_wordline_energy" ] \
               + energy[ "row_predecoder_energy" ] \
               + energy[ "row_decoder_energy" ] \
               + energy[ "local_wordline_energy" ]

    def calc_local_bus_latency( self ):
        """
        datapath_bus_delay + global_dataline_delay + data_buffer_delay + 
        subarray_output_driver_delay
        """
        timing = self.config[ "spec" ][ "timing" ]
        return timing[ "datapath_bus_delay" ] \
                + timing[ "global_dataline_delay" ]\
                + timing[ "local_dataline_delay" ]\
                + timing[ "data_buffer_delay" ]\
                + timing[ "subarray_output_driver_delay" ]

    def calc_local_bus_energy( self ):
        """
        datapath_bus_energy + global_dataline_energy + local_dataline_energy
        + data_buffer_energy 
        """
        timing = self.config[ "spec" ][ "energy" ]
        return timing[ "datapath_bus_energy" ] \
                + timing[ "global_dataline_energy" ]\
                + timing[ "local_dataline_energy" ]\
                + timing[ "data_buffer_energy" ]

    
    # utilities

    def GB_to_bits( self, GB ):
        # GB -> MB -> KB -> B -> bits
        return GB * 1024 * 1024 * 1024 * 8



