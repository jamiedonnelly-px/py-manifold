#include <cstdarg>  
#include <cstdio>   
#include <fstream>

int verbosePrinter(int verbose, const char* format, ...) {
    if (verbose == 1) {
        va_list args;
        va_start(args, format);  
        int result = vprintf(format, args);  
        va_end(args);
        return result;
    } else {
        return 0;
    }
}


