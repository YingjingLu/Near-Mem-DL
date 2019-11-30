from hmc import * 
import json
NAIVE_TEST_STR = """
weight, write, 1022, 2, 1, l1, 3, 5, 3, 5, 6, 3
weight, write, 1176, 2, 2, l2, 3, 4, 5, 6, 5, 7
weight, write, 1298, 3, 2, l1, 3, 3, 5, 6, 6, 8
weight, read, 2109, 2, 6, l3, 3, 4, 5, 6, 8, 10
weight, free, 2234, 2, 2, l1, 3, 4, 4, 6, 13, 15
weight, free, 2564, 3, 2, l4, 5, 8, 5, 10, 15, 17
weight, write, 1787, 2, 4, l1, 3, 4, 5, 6, 15, 18
weight, read, 1907, 4, 4, l1, 4, 7, 12, 6, 18, 20
weight, write, 1088, 6, 6, l1, 3, 4, 5, 6, 23, 25
weight, write, 1970, 2, 2, l2, 3, 8, 5, 7, 34, 35
weight, read, 1097, 3, 3, l1, 3, 4, 5, 6, 24, 56
"""

if __name__ == "__main__":
    with open( "../spec/ram_config/16ghmc.json", "r" ) as f:
        config = json.load( f )
    hmc = HMC( config, 16 )
    for trace in NAIVE_TEST_STR.strip().split( "\n" ):
        hmc.process_access( trace )
    hmc.get_summary()