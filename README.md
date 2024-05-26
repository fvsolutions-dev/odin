# ODIN
An cross framework object dictionary for embedded systems

TODO: Add more information


## gen
Create object dictionary
```
pip install nanopb
nanopb_generator components/odin_datastore/odin.proto
```

Convert proto
```
protoc --c_out=main/datastore/src/generated/ main/datastore/src/storage.proto
```


# TODO
Fix array support when printing
fix device capacilites getter
