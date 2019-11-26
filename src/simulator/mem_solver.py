"""
mem addr:
( 
    vault_idx, 
    layer_idx, 
        bank_idx, 
            subarray_idx, 
                subarray_row_start, sybarray_col_start,
                subarray_row_end, subarray_col_end  
)
malloc_chunk:
(
    layer_row_start, layer_col_start,
    layer_row_end, layer_col_end,

    mem_addr
)


memory_topology: layer/fmap -> memory addr 

weight:
    layer_name:
        [ malloc_chunk, .... ]

fmap: 
    fmap_name:
        [ malloc_chunk, ..... ]

"""

