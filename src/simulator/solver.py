"""
----------------------    Assumptions    ---------------------------------------
The overall RAM is able to hold all the weight and the demanding fmaps and intermediaries 
without reading or writing back to the disk.

The weights, once loaded is kept stationary in RAM and only partial fmaps will be 
loaded or offloaded from the RAM

----------------------    Proposed PE    --------------------------------------- 

The proposed PE has the following parts:
- A vector ALU unit that is able to perform vector MAC in 1 cycle as 1 OP
- A weight register file that stores the weight it is using
- A partial register / buffer that captures the MAC result for all data exchange to ths PE
- A input register that stores the input fmap assigned or rotated to this PE

----------------------   Handle FC solver   ------------------------------------

Prelim
Each PE is assigned with weight equal to its weight reg size
Each PE is assigned with equal sized fmap info

1. 
The dataflow figures out how weight is assigned to each PE -> tile
The dataflow load the weights and fmap of that layer into the RAM
Repeat for each layer:
    Repeat:
        loads each partition weight into the PEs
        loads each parttioned fmaps into the PE
        accumulate MAC and rotate weights, rotate fmaps
        store the partial results back to the RAM
    if the layer fmap / partials will no longer in use from dependency graph, remove them 
--------------------------------------------------------------------------------
"""
import math

def solve_num_stride( buffer, w, h ):
    """
    solve for maximized feature map assigned to each vault 
    weight_v + num * stride_v, weight_h + num * stride_h * num
    square
    """
    b = ( w + h )
    a = 1
    c = w * h - buffer
    delta = b **2 - 4 * a * c
    if delta < 0:
        return 0
    return math.floor( ( -b + math.sqrt( delta ) ) / 2 / a)