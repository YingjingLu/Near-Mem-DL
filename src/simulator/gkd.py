import math
from layers import *
I_REG = 16
O_REG = 16
W_REG = I_REG 

PE_NUM = 16 
IMAP_BUFFER = 256
OMAP_BUFFER = 256
WEIGHT_BUFFER = 256

VAULT_NUM = 16

RAM_COL = 32

"""
map shape size[ B, H, W, C ]
weight_shape [ H, W, C ] / [ W ]

MODE:

0: calc distinct Data
1: calc MAC energy
2: calc RAM energy 
3: calc bus energy 
4: calc total energy
"""

MODE = 1

########################### Distinct Data ######################################

def distinct_weight_dup_w( weight_shape ):
    [w, h, c] = weight_shape 

    num_pe = PE_NUM 
    return num_pe * ( min( w, W_REG ) )


def distinct_weight_dup_i( weight_shape ):
    [w, h, c] = weight_shape 
    if w > W_REG:
        return W_REG * PE_NUM 
    return PE_NUM * ( ( W_REG // w ) * w )

def distinct_imap_dup_w( imap_shape, weight_shape, stride  ):
    i_n, i_w, i_h, i_c = imap_shape 
    w_w, w_h, w_c = weight_shape

    return PE_NUM * ( ( ( I_REG - w_w ) // stride ) * stride + w_w )

def distinct_imap_dup_i( imap_shape, weight_shape, stride ):
    i_n, i_w, i_h, i_c = imap_shape 
    w_w, w_h, w_c = weight_shape

    return PE_NUM * w_w 


def distinct_weight_ow( weight_shape ):
    [w, h, c] = weight_shape 

    return w * (W_REG // w) * PE_NUM // int( math.sqrt( PE_NUM ) )

def distinct_imap_ow( imap_shape, weight_shape, stride  ):
    i_n, i_w, i_h, i_c = imap_shape 
    w_w, w_h, w_c = weight_shape

    return W_REG + ( W_REG - 1 ) * stride
    

######################## End Distinct Data #####################################


def fc_mac( imap_shape, weight_shape ):
    w = imap_shape 
    w, h = weight_shape 
    
    calc_w, calc_h = math.ceil( w / W_REG ), h
    return calc_w * calc_h * W_REG 



def conv_mac( imap_shape, stride, weight_shape ):
    i_w, i_h, i_c = imap_shape 
    w_w, w_h, w_c = weight_shape 
    s_h, s_v = stride
    w_op = math.ceil( ( i_w - w_w ) / s_h ) + 1
    h_op = math.ceil( ( i_h - w_h ) / s_v ) + 1

    return w_op * w_w *h_op * w_h * i_c * w_c 

def fc_ram_dup_w( layer_list ):
    """
    [ [ input_shape, weight_shape ] ]

    """
    total_imap = 0
    total_weight = 0
    for imap, weight in layer_list:
        total_imap += imap[ 0 ]
        total_weight += weight[ 0 ] * weight[ 1 ]

    
    return total_imap, total_weight 


def conv_ram_dup_w( layer_list ):
    """
    imap_shape, stride, weight_shape
    """
    imap_mem_total = 0
    weight_mem_total = 0
    pe_side = int( math.sqrt( PE_NUM ) )
    total_pe = PE_NUM * VAULT_NUM 
    for imap, stride, weight in layer_list:
        sh, sv = stride
        w_h, w_w, w_v = weight 
        i_h, i_w, i_c = imap

        weight_capacity = w_w * total_pe
        weight_total = weight[ 0 ] * weight[ 1 ] * weight[ 2 ]
        weight_times = weight_total / weight_capacity
        imap_total = i_h * i_w * i_c 
        pe_times = I_REG // w_w 
        imap_capacity = ( sh * ( pe_times ) ) * total_pe 
        imap_times = imap_total / imap_capacity
        weight_mem_total += int( weight_total * imap_times )
        imap_mem_total += int( imap_total * imap_times )
    return imap_mem_total, weight_mem_total


def fc_ram_dup_i( layer_list ):
    """
    [ [ input_shape, weight_shape ] ]

    """
    total_imap = 0
    total_weight = 0
    for imap, weight in layer_list:
        total_imap += imap[ 0 ]
        total_weight += weight[ 0 ] * weight[ 1 ]
    return total_imap, total_weight 

def conv_ram_dup_i( layer_list ):
    """
    imap_shape, stride, weight_shape
    """
    imap_mem_total = 0
    weight_mem_total = 0
    pe_side = int( math.sqrt( PE_NUM ) )
    total_pe = PE_NUM * VAULT_NUM 
    for imap, stride, weight in layer_list:
        sh, sv = stride
        w_h, w_w, w_v = weight 
        i_h, i_w, i_c = imap
        pe_times = I_REG // w_w 
        weight_capacity = w_w * total_pe * pe_times
        weight_total = weight[ 0 ] * weight[ 1 ] * weight[ 2 ]
        weight_times = weight_total / weight_capacity
        imap_total = i_h * i_w * i_c 
        imap_capacity = ( sh) * total_pe 
        imap_times = imap_total / imap_capacity
        weight_mem_total += int( weight_total * imap_times )
        imap_mem_total += int( imap_total * imap_times )
    return imap_mem_total, weight_mem_total

def fc_bus_dup_w( imap_shape, weight_shape ):
    w = imap_shape 
    w, h = weight_shape 
    
    calc_w, calc_h = math.ceil( w / W_REG ), h
    return calc_w * calc_h 


def conv_bus_dup_w( imap_shape, stride, weight_shape ):
    i_w, i_h, i_c = imap_shape 
    w_w, w_h, w_c = weight_shape 
    s_h, s_v = stride
    w_op = math.ceil( ( i_w - w_w ) / s_h ) + 1
    h_op = math.ceil( ( i_h - w_h ) / s_v ) + 1

    num_imap_per_pe = math.floor( I_REG / w_w )

    i_traffic = math.ceil( w_op / num_imap_per_pe ) * h_op * w_h * w_c
    return i_traffic



def fc_bus_dup_i( imap_shape, weight_shape ):
    w = imap_shape 
    w, h = weight_shape 
    
    calc_w, calc_h = math.ceil( w / W_REG ), h
    return calc_w * calc_h 


def conv_bus_dup_i( imap_shape, stride, weight_shape ):
    i_w, i_h, i_c = imap_shape 
    w_w, w_h, w_c = weight_shape 
    s_h, s_v = stride
    w_op = math.ceil( ( i_w - w_w ) / s_h ) + 1
    h_op = math.ceil( ( i_h - w_h ) / s_v ) + 1

    per_height = math.ceil( w_h * w_c / W_REG ) 

    i_traffic = w_op * h_op * w_h * w_c * per_height
    return i_traffic

if __name__ == "__main__":

    if MODE == 1:

        stride = 4
        weight_shape = [ 5, 5, 64 ]
        imap_shape = [ 64, 112, 112, 32 ]
        print( "distinct_weight_dup_w", distinct_weight_dup_w( weight_shape ) )
        print( "distinct_weight_dup_i", distinct_weight_dup_i( weight_shape ) )
        print( "distinct_weight_ow", distinct_weight_ow( weight_shape ) )

        print( "distinct_imap_dup_w", distinct_imap_dup_w( imap_shape, weight_shape, stride ) )
        print( "distinct_imap_dup_i", distinct_imap_dup_i( imap_shape, weight_shape, stride ) )
        print( "distinct_imap_ow", distinct_imap_ow( imap_shape, weight_shape, stride ) )

    if MODE == 2:

        layers = LENET

        total_bus = 0
        total_mac = 0
        total_ram_weight = 0
        total_ram_imap = 0

        DUP_I = False 
        fc_layers = []
        conv_layers = []
        for l in layers:
            if l[ "type" ] == "conv":
                conv_layers.append( [ l[ "in" ], l[ "stride" ], l[ "weight" ] ] )
                if DUP_I:
                    total_bus += conv_bus_dup_i( l[ "in" ], l[ "stride" ], l[ "weight" ] )
                    total_mac += conv_mac( l[ "in" ], l[ "stride" ], l[ "weight" ] )
                else:
                    total_bus += conv_bus_dup_w( l[ "in" ], l[ "stride" ], l[ "weight" ] )
                    total_mac += conv_mac( l[ "in" ], l[ "stride" ], l[ "weight" ] )
            else:
                fc_layers.append( [ l[ "in" ], l[ "weight" ] ] )
                if DUP_I:
                    total_bus += fc_bus_dup_i( l[ "in" ], l[ "weight" ] )
                    total_mac += fc_mac( l[ "in" ], l[ "weight" ] )
                else:
                    total_bus += fc_bus_dup_w( l[ "in" ], l[ "weight" ] )
                    total_mac += fc_mac( l[ "in" ], l[ "weight" ] )

        if len( fc_layers ) > 0:
            if DUP_I:
                imap, weight = fc_ram_dup_i( fc_layers )
            else:
                imap, weight = fc_ram_dup_w( fc_layers )
        total_ram_weight += weight 
        total_ram_imap += imap
        if len( conv_layers ) > 0:
            if DUP_I:
                imap, weight = conv_ram_dup_i( conv_layers )
            else:
                imap, weight = conv_ram_dup_w( conv_layers )
        total_ram_weight += weight 
        total_ram_imap += imap

        print( "bus count:", total_bus * 0.68 / 1000 * 16 )
        print( "mac: ", total_mac / 1000 * 16 )
        print( "ram weight: ", total_ram_weight * 3.82 )
        print( "ram imap: ", total_ram_imap * 3.82/50 )






