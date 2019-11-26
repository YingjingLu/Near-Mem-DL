
## Memory

### HMC memory

#### Protocol with Processors

##### Initialize 

##### Loading DL Models
* DNN Confog: <json>
* Load throughput for loading from disk Byte/s
##### Data IO
Input (csv file, each trace is "," separated)
* weight / fmap
* read / write / free
* Time elapse of the request (in ms)
* Vault Index from the processor making the request
* Vault Index the data's destination
* Requesting layer name / fmap name
* Requesting row start index
* Requesting col start index
* Requesting row end index
* Requesting col end index

Output (csv file, each trace is "," separated)
* Time elapse that the request is being requests
* Vault index of the destination processor
* Num Row
* Num Col
* Word Size