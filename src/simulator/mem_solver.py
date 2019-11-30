"""
mem addr:
( 
    vault_idx, 
    layer_idx, 
        bank_idx, 
            subarray_idx, 
                subarray_row_start, sybarray_col_start,
                subarray_row_end, subarray_col_end  
    
    size 
    prev 
    next 
)
malloc_chunk:
(
    layer_row_start, layer_col_start,
    layer_row_end, layer_col_end,
    
    mem_addr

    size
)

"""

class Mem_Addr( object ):
    
    def __init__( self, size, occu,
                  vault_idx, layer_idx, bank_idx, subarray_idx,
                  subarray_row_start, subarray_col_start,
                  subarray_row_end, subarray_col_end ):
        self.size = size
        self.occu = occu
        self.vault_idx = vault_idx
        self.layer_idx = layer_idx
        self.bank_idx = bank_idx 
        self.subarray_idx = subarray_idx 
        self.subarray_row_start = subarray_row_start 
        self.subarray_col_start = subarray_col_start 
        self.subarray_row_end = subarray_row_end
        self.subarray_col_end = subarray_col_end

        self.prev = None 
        self.next = None 


class Mem_Chunk( object ):
    
    def __init__( self, 
                  layer_row_start, layer_col_start,
                  layer_row_end, layer_col_end,
                  mem_addr ):
        self.layer_row_start = layer_row_start
        self.layer_col_start = layer_col_start,
        self.layer_row_end = layer_row_end 
        self.layer_col_end = layer_col_end 
        self.mem_addr = mem_addr 
        self.prev = None 
        self.next = None
    
