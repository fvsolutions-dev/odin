#include "odin.h"

const char *ODIN_error_to_string(int error)
{
    switch (error)
    {
    case ODIN_SUCCESS:
        return "Success";
    case ODIN_ERROR_NO_PARAMETER:
        return "No parameter";
    case ODIN_ERROR_PARAMETER_NOT_FOUND:
        return "Parameter not found";
    case ODIN_ERROR_SIZE_MISMATCH:
        return "Size mismatch";
    case ODIN_ERROR_PERMISSION_DENIED:
        return "Permission denied";
    case ODIN_ERROR_UNSUPPORTED_FORMAT:
        return "Unsupported format";
    case ODIN_ERROR_NOT_SUPPORTED:
        return "Not supported";
        
    case ODIN_ERROR:
        return "General error";
    default:
        return "Unknown error";
    }
}
