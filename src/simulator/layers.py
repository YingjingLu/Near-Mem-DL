VGG = \
[
    {
        "type": "conv",
        "in": [ 250, 250, 3 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 64 ]
    },
    {
        "type": "conv",
        "in": [ 250, 250, 64 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 64 ]
    },
    {
        "type": "conv",
        "in": [ 250, 250, 64 ],
        "stride": [ 2, 2 ],
        "weight": [ 3, 3, 128 ]
    },
    {
        "type": "conv",
        "in": [ 125, 125, 128 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 128 ]
    },
    {
        "type": "conv",
        "in": [ 125, 125, 128 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 128 ]
    },
    {
        "type": "conv",
        "in": [ 125, 125, 128 ],
        "stride": [ 2, 2 ],
        "weight": [ 3, 3, 256 ]
    },
    {
        "type": "conv",
        "in": [ 62, 62, 256 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 256 ]
    },
    {
        "type": "conv",
        "in": [ 62, 62, 256 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 256 ]
    },
    {
        "type": "conv",
        "in": [ 62, 62, 256 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 256 ]
    },
    {
        "type": "conv",
        "in": [ 62, 62, 256 ],
        "stride": [ 2, 2 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 32, 32, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 32, 32, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 32, 32, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 32, 32, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 32, 32, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 32, 32, 512 ],
        "stride": [ 2, 2 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 16, 16, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 16, 16, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 16, 16, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 16, 16, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 16, 16, 512 ],
        "stride": [ 2, 2 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 8, 8, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 8, 8, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 8, 8, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "conv",
        "in": [ 8, 8, 512 ],
        "stride": [ 1, 1 ],
        "weight": [ 3, 3, 512 ]
    },
    {
        "type": "fc",
        "in": [ 32768 ],
        "weight": [ 32768, 4096 ]
    },
    {
        "type": "fc",
        "in": [ 4096 ],
        "weight": [ 4096, 4096 ]
    },
    {
        "type": "fc",
        "in": [ 4096 ],
        "weight": [ 4096, 4096 ]
    },
    {
        "type": "fc",
        "in": [ 4096 ],
        "weight": [ 4096, 100 ]
    }
]

LENET = \
[
    {
        "type": "conv",
        "in": [ 28, 28, 1 ],
        "stride": [ 2,2 ],
        "weight": [ 3,3, 16 ]
    },
    {
        "type": "conv",
        "in": [ 14, 14, 16 ],
        "stride": [ 2, 2 ],
        "weight": [ 3,3, 32 ]
    },
    {
        "type": "conv",
        "in": [ 7, 7, 32 ],
        "stride": [ 2, 2 ],
        "weight": [ 3,3, 64 ]
    },
    {
        "type": "conv",
        "in": [ 4, 4, 64 ],
        "stride": [ 2, 2 ],
        "weight": [ 3,3, 64 ]
    },
    {
        "type": "fc",
        "in": [ 16384 ],
        "weight": [ 16384, 10 ]
    }
]