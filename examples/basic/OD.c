#include "OD.h"

odin_variables_t odin_variables = {
    .test_variable_i8 = 0,
    .test_variable_i16 = 0,
    .test_variable_i32 = 0,
    .test_variable_i64 = 1234567890123456789,
    .test_variable_u8 = 123,
    .test_variable_u16 = 0,
    .test_variable_u32 = 0,
    .test_variable_u64 = 0,
    .test_variable_float32 = 0.0,
    .test_variable_float64 = 0.0,
    .test_variable_bool_false = false,
    .test_variable_bool_true = true,
    .test_variable_char = 'a',
    .group_A = {
        .group_A = {
            .other_child = 0.0
        },
        .test_variable_A = 0.0,
        .test_variable_B = 1.23,
        .test_variable_small = 88
    },
    .test_variable_small = 86080530548,
    .u8_array = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
    .u8_variable_length_array = {
        .data = {1, 5, 3},
        .num_elements = 3
    },
    .i8_array = {-128, -127, -126, -125, -124, 5, 6, 7, 8, 9},
    .i8_variable_length_array = {
        .data = {-128, -127, -126, -125, -124, 5, 6, 7, 8, 9},
        .num_elements = 10
    },
    .u16_array = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
    .u16_variable_length_array = {
        .data = {1, 5, 3},
        .num_elements = 3
    },
    .i16_array = {-32768, -32767, -32766, -32765, -32764, 5, 6, 7, 8, 9},
    .i16_variable_length_array = {
        .data = {-32768, -32767, -32766, -32765, -32764, 5, 6, 7, 8, 9},
        .num_elements = 10
    },
    .u32_array = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
    .u32_variable_length_array = {
        .data = {1, 5, 3},
        .num_elements = 3
    },
    .i32_array = {-2147483648, -2147483647, -2147483646, -2147483645, -2147483644, 5, 6, 7, 8, 9},
    .i32_variable_length_array = {
        .data = {-2147483648, -2147483647, -2147483646, -2147483645, -2147483644, 5, 6, 7, 8, 9},
        .num_elements = 10
    },
    .u64_array = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
    .u64_variable_length_array = {
        .data = {1, 5, 3},
        .num_elements = 3
    },
    .i64_array = {-922337203685475808, -922332036854775807, -922337236854775806, -922337036854775805, -923372036854775804, 5, 6, 7, 8, 9},
    .i64_variable_length_array = {
        .data = {-922337203685475808, -922337203854775807, -922337203684775806, -922337203854775805, -922372036854775804, 5, 6, 7, 8, 9},
        .num_elements = 10
    },
    .float32_array = {0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9},
    .float32_variable_length_array = {
        .data = {1.1, 5.5, 3.3},
        .num_elements = 3
    },
    .float64_array = {0.0, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9},
    .float64_variable_length_array = {
        .data = {1.1, 5.5, 3.3},
        .num_elements = 3
    },
    .bool_array = {true, false, true, false, true, false, true, false, true, false},
    .bool_variable_length_array = {
        .data = {true, false, true},
        .num_elements = 3
    },
    .char_array = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'},
    .char_variable_length_array = {
        .data = {'a', 'b', 'c'},
        .num_elements = 3
    }
};

const odin_objects_t odin_objects = {
    .test_variable_i8 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT8,
        .flags = 0,
        .global_index = 0x01000000,
        .element_size = sizeof(int8_t),
        .data = &odin_variables.test_variable_i8,
        .name_and_description = "test_variable_i8\0A test variable of type signed 8 bit integer",
        .extension = NULL
    },
    .test_variable_i16 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT16,
        .flags = 0,
        .global_index = 0x02000000,
        .element_size = sizeof(int16_t),
        .data = &odin_variables.test_variable_i16,
        .name_and_description = "test_variable_i16\0A test variable of type signed 16 bit integer",
        .extension = NULL
    },
    .test_variable_i32 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .global_index = 0x03000000,
        .element_size = sizeof(int32_t),
        .data = &odin_variables.test_variable_i32,
        .name_and_description = "test_variable_i32\0A test variable of type signed 32 bit integer",
        .extension = NULL
    },
    .test_variable_i64 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_INT64,
        .flags = 0,
        .global_index = 0x04000000,
        .element_size = sizeof(int64_t),
        .data = &odin_variables.test_variable_i64,
        .name_and_description = "test_variable_i64\0A test variable of type signed 64 bit integer",
        .extension = NULL
    },
    .test_variable_u8 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT8,
        .flags = 0,
        .global_index = 0x05000000,
        .element_size = sizeof(uint8_t),
        .data = &odin_variables.test_variable_u8,
        .name_and_description = "test_variable_u8\0A test variable of type unsigned 8 bit integer",
        .extension = NULL
    },
    .test_variable_u16 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .flags = 0,
        .global_index = 0x06000000,
        .element_size = sizeof(uint16_t),
        .data = &odin_variables.test_variable_u16,
        .name_and_description = "test_variable_u16\0A test variable of type unsigned 16 bit integer",
        .extension = NULL
    },
    .test_variable_u32 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .flags = 0,
        .global_index = 0x07000000,
        .element_size = sizeof(uint32_t),
        .data = &odin_variables.test_variable_u32,
        .name_and_description = "test_variable_u32\0A test variable of type unsigned 32 bit integer",
        .extension = NULL
    },
    .test_variable_u64 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT64,
        .flags = 0,
        .global_index = 0x08000000,
        .element_size = sizeof(uint64_t),
        .data = &odin_variables.test_variable_u64,
        .name_and_description = "test_variable_u64\0A test variable of type unsigned 64 bit integer",
        .extension = NULL
    },
    .test_variable_float32 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = 0,
        .global_index = 0x09000000,
        .element_size = sizeof(float),
        .data = &odin_variables.test_variable_float32,
        .name_and_description = "test_variable_float32\0A test variable of type 32 bit floating point",
        .extension = NULL
    },
    .test_variable_float64 = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT64,
        .flags = 0,
        .global_index = 0x0A000000,
        .element_size = sizeof(double),
        .data = &odin_variables.test_variable_float64,
        .name_and_description = "test_variable_float64\0A test variable of type 64 bit floating point",
        .extension = NULL
    },
    .test_variable_bool_false = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_BOOL,
        .flags = 0,
        .global_index = 0x0B000000,
        .element_size = sizeof(bool),
        .data = &odin_variables.test_variable_bool_false,
        .name_and_description = "test_variable_bool_false\0A test variable of type boolean",
        .extension = NULL
    },
    .test_variable_bool_true = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_BOOL,
        .flags = 0,
        .global_index = 0x0C000000,
        .element_size = sizeof(bool),
        .data = &odin_variables.test_variable_bool_true,
        .name_and_description = "test_variable_bool_true\0A test variable of type boolean",
        .extension = NULL
    },
    .test_variable_char = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_CHAR,
        .flags = 0,
        .global_index = 0x0D000000,
        .element_size = sizeof(char),
        .data = &odin_variables.test_variable_char,
        .name_and_description = "test_variable_char\0A test variable of type character",
        .extension = NULL
    },
    .group_A = {
        .group_A = {
            .other_child = {
                .odin_type = ODIN_TYPE_PARAMETER,
                .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
                .flags = 0,
                .global_index = 0x30200100,
                .element_size = sizeof(float),
                .data = &odin_variables.group_A.group_A.other_child,
                .name_and_description = "other_child\0A test variable",
                .extension = NULL
            }
        
        },
        .test_variable_A = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .global_index = 0x30020000,
            .element_size = sizeof(float),
            .data = &odin_variables.group_A.test_variable_A,
            .name_and_description = "test_variable_A\0A test variable",
            .extension = NULL
        },
        .test_variable_B = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
            .flags = 0,
            .global_index = 0x30030000,
            .element_size = sizeof(float),
            .data = &odin_variables.group_A.test_variable_B,
            .name_and_description = "test_variable_B\0A test variable",
            .extension = NULL
        },
        .test_variable_small = {
            .odin_type = ODIN_TYPE_PARAMETER,
            .element_type = ODIN_ELEMENT_TYPE_UINT8,
            .flags = 0,
            .global_index = 0x30050000,
            .element_size = sizeof(uint8_t),
            .data = &odin_variables.group_A.test_variable_small,
            .name_and_description = "test_variable_small\0A small test variable",
            .extension = NULL
        }
    
    },
    .test_variable_small = {
        .odin_type = ODIN_TYPE_PARAMETER,
        .element_type = ODIN_ELEMENT_TYPE_UINT64,
        .flags = 0,
        .global_index = 0x86000000,
        .element_size = sizeof(uint64_t),
        .data = &odin_variables.test_variable_small,
        .name_and_description = "test_variable_small\0A small test variable",
        .extension = NULL
    },
    .u8_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT8,
        .flags = 0,
        .global_index = 0x50000000,
        .element_size = sizeof(uint8_t),
        .data = &odin_variables.u8_array,
        .name_and_description = "u8_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .u8_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_UINT8,
        .flags = 0,
        .global_index = 0x51000000,
        .element_size = sizeof(uint8_t),
        .data = &odin_variables.u8_variable_length_array,
        .name_and_description = "u8_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .i8_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_INT8,
        .flags = 0,
        .global_index = 0x52000000,
        .element_size = sizeof(int8_t),
        .data = &odin_variables.i8_array,
        .name_and_description = "i8_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .i8_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_INT8,
        .flags = 0,
        .global_index = 0x53000000,
        .element_size = sizeof(int8_t),
        .data = &odin_variables.i8_variable_length_array,
        .name_and_description = "i8_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .u16_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .flags = 0,
        .global_index = 0x54000000,
        .element_size = sizeof(uint16_t),
        .data = &odin_variables.u16_array,
        .name_and_description = "u16_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .u16_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_UINT16,
        .flags = 0,
        .global_index = 0x55000000,
        .element_size = sizeof(uint16_t),
        .data = &odin_variables.u16_variable_length_array,
        .name_and_description = "u16_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .i16_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_INT16,
        .flags = 0,
        .global_index = 0x56000000,
        .element_size = sizeof(int16_t),
        .data = &odin_variables.i16_array,
        .name_and_description = "i16_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .i16_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_INT16,
        .flags = 0,
        .global_index = 0x57000000,
        .element_size = sizeof(int16_t),
        .data = &odin_variables.i16_variable_length_array,
        .name_and_description = "i16_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .u32_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .flags = 0,
        .global_index = 0x58000000,
        .element_size = sizeof(uint32_t),
        .data = &odin_variables.u32_array,
        .name_and_description = "u32_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .u32_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_UINT32,
        .flags = 0,
        .global_index = 0x59000000,
        .element_size = sizeof(uint32_t),
        .data = &odin_variables.u32_variable_length_array,
        .name_and_description = "u32_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .i32_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .global_index = 0x5A000000,
        .element_size = sizeof(int32_t),
        .data = &odin_variables.i32_array,
        .name_and_description = "i32_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .i32_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_INT32,
        .flags = 0,
        .global_index = 0x5B000000,
        .element_size = sizeof(int32_t),
        .data = &odin_variables.i32_variable_length_array,
        .name_and_description = "i32_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .u64_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_UINT64,
        .flags = 0,
        .global_index = 0x5C000000,
        .element_size = sizeof(uint64_t),
        .data = &odin_variables.u64_array,
        .name_and_description = "u64_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .u64_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_UINT64,
        .flags = 0,
        .global_index = 0x5D000000,
        .element_size = sizeof(uint64_t),
        .data = &odin_variables.u64_variable_length_array,
        .name_and_description = "u64_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .i64_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_INT64,
        .flags = 0,
        .global_index = 0x5E000000,
        .element_size = sizeof(int64_t),
        .data = &odin_variables.i64_array,
        .name_and_description = "i64_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .i64_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_INT64,
        .flags = 0,
        .global_index = 0x5F000000,
        .element_size = sizeof(int64_t),
        .data = &odin_variables.i64_variable_length_array,
        .name_and_description = "i64_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .float32_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = 0,
        .global_index = 0x60000000,
        .element_size = sizeof(float),
        .data = &odin_variables.float32_array,
        .name_and_description = "float32_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .float32_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT32,
        .flags = 0,
        .global_index = 0x61000000,
        .element_size = sizeof(float),
        .data = &odin_variables.float32_variable_length_array,
        .name_and_description = "float32_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .float64_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT64,
        .flags = 0,
        .global_index = 0x62000000,
        .element_size = sizeof(double),
        .data = &odin_variables.float64_array,
        .name_and_description = "float64_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .float64_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_FLOAT64,
        .flags = 0,
        .global_index = 0x63000000,
        .element_size = sizeof(double),
        .data = &odin_variables.float64_variable_length_array,
        .name_and_description = "float64_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .bool_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_BOOL,
        .flags = 0,
        .global_index = 0x64000000,
        .element_size = sizeof(bool),
        .data = &odin_variables.bool_array,
        .name_and_description = "bool_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .bool_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_BOOL,
        .flags = 0,
        .global_index = 0x65000000,
        .element_size = sizeof(bool),
        .data = &odin_variables.bool_variable_length_array,
        .name_and_description = "bool_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    },
    .char_array = {
        .odin_type = ODIN_TYPE_ARRAY,
        .element_type = ODIN_ELEMENT_TYPE_CHAR,
        .flags = 0,
        .global_index = 0x66000000,
        .element_size = sizeof(char),
        .data = &odin_variables.char_array,
        .name_and_description = "char_array\0A test variable",
        .extension = NULL,
        .max_elements = 10
    },
    .char_variable_length_array = {
        .odin_type = ODIN_TYPE_VECTOR,
        .element_type = ODIN_ELEMENT_TYPE_CHAR,
        .flags = 0,
        .global_index = 0x67000000,
        .element_size = sizeof(char),
        .data = &odin_variables.char_variable_length_array,
        .name_and_description = "char_variable_length_array\0My variable length array, allowing writes with a variable length, it also stores a reference to the length of the array",
        .extension = NULL,
        .max_elements = 50
    }
};

const ODIN_parameter_group_t odin_store = {
    .name_and_description = "root\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x00000000,
    .shift = 8,
    .count = 39,
    .parameters = {&odin_objects.test_variable_i8, &odin_objects.test_variable_i16, &odin_objects.test_variable_i32, &odin_objects.test_variable_i64, &odin_objects.test_variable_u8, &odin_objects.test_variable_u16, &odin_objects.test_variable_u32, &odin_objects.test_variable_u64, &odin_objects.test_variable_float32, &odin_objects.test_variable_float64, &odin_objects.test_variable_bool_false, &odin_objects.test_variable_bool_true, &odin_objects.test_variable_char, &odin_store_group_A, &odin_objects.test_variable_small, &odin_objects.u8_array, &odin_objects.u8_variable_length_array, &odin_objects.i8_array, &odin_objects.i8_variable_length_array, &odin_objects.u16_array, &odin_objects.u16_variable_length_array, &odin_objects.i16_array, &odin_objects.i16_variable_length_array, &odin_objects.u32_array, &odin_objects.u32_variable_length_array, &odin_objects.i32_array, &odin_objects.i32_variable_length_array, &odin_objects.u64_array, &odin_objects.u64_variable_length_array, &odin_objects.i64_array, &odin_objects.i64_variable_length_array, &odin_objects.float32_array, &odin_objects.float32_variable_length_array, &odin_objects.float64_array, &odin_objects.float64_variable_length_array, &odin_objects.bool_array, &odin_objects.bool_variable_length_array, &odin_objects.char_array, &odin_objects.char_variable_length_array}
};

const ODIN_parameter_group_t odin_store_group_A = {
    .name_and_description = "group_A\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x30000000,
    .shift = 8,
    .count = 4,
    .parameters = {&odin_store_group_A_group_A, &odin_objects.group_A.test_variable_A, &odin_objects.group_A.test_variable_B, &odin_objects.group_A.test_variable_small}
};

const ODIN_parameter_group_t odin_store_group_A_group_A = {
    .name_and_description = "group_A\0No description",
    .odin_type = ODIN_TYPE_GROUP,
    .global_index = 0x30200000,
    .shift = 8,
    .count = 1,
    .parameters = {&odin_objects.group_A.group_A.other_child}
};
