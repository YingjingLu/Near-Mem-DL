# Spec Sheet

## NN Spec
* json file
* Batch size specified and shared throughout all layers, append batch size by the start of the shape of layer input shape. Ex: layer ifmap is [ 15, 15, 3 ], then with batch size is [ 16, 15, 15, 3 ] is the true datashape 
* Data Rate is # of batch / sec
* layers weights are packed in a npz file where each key word refers to layer name
* input data layer has a type of "INPUT" and has no weight information, their shape is refered as "out_shape"
* layer "type" consists of "INPUT / CNN / FC" refers to input layer, conv layer and fully connected layer (currently not supporting pooling)

Example with [ 28x28x1 ] input, [3x3x16] conv filter stride 2, and a cully connected layer with 1 output:
```json
{
    "nn_name": "Sample_NN",
    "batch_size": 16,
    "data_rate": 2.5,
    "layers":
    [
        {
            "name": "input1",
            "type": "INPUT",
            "out_shape": [ 28, 28, 1 ],
            "activation": ""
        },
        {
            "name": "conv1",
            "type": "CONV",
            "config": 
            {
                "weight_shape": [ 3, 3, 16 ],
                "padding": [ 1, 0, 1, 0 ],
                "stride": [ 2, 2, 2, 2 ],
                "dilation": [ 1, 1, 1, 1 ] 
            },
            "in_layer": "input1",
            "out_shape": [ 14, 14, 16 ],
            "activation": "relu"
        },
        {
            "name": "fc1",
            "type": "FC",
            "config": 
            {
                "weight_shape": [ 3136, 1 ]
            },
            "in_layer": "conv1",
            "out_shape": [ 1 ],
            "activation": "sigmoid"
        }
    ]
}
```

## Processing Engine Spec

1 OP = 1 MAC
CPU cycle time = 1 / core frequency

Core Frequency 

MAC OP energy

## Bus
Bus bandwidth

## SRAM Register / Buffer Spec

## HMC spec
https://github.com/HewlettPackard/cacti

https://github.com/rafaeljin/Systolic-Array-simulator

https://github.com/ARM-software/SCALE-Sim


## HMC Computation


## HMC layout

* vault
* layer
* bank
* subarray
* row
* col 
