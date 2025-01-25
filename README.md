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



```
cmake -G "Ninja" ..
```
build fresh (clean)
```
cmake --build build --clean-first
```


llvm-profdata merge -sparse build/test/default.profraw -o default.profdata
llvm-cov show ./build/test/tests.exe -instr-profile=default.profdata -format=html -output-dir=coverage

llvm-profdata merge  default.profraw -output=default.profdata
llvm-cov show basic_test.exe -instr-profile=default.profdata -format=html -output-dir=coverage
llvm-cov export basic_test.exe -instr-profile=default.profdata  > coverage.json

llvm-cov export basic_test.exe -instr-profile=default.profdata -format=lcwov > coverage.xml