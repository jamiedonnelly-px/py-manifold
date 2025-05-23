#ifndef MANIFOLD2_UTILS_H
#define MANIFOLD2_UTILS_H

#include <cstdarg>  
#include <cstdio>   
#include <fstream>

inline int verbosePrinter(int verbose, const char* format, ...) {
    if (verbose == 1) {
        va_list args;
        va_start(args, format);  
        int result = vprintf(format, args);  
        va_end(args);
        fflush(stdout); // immediately flushes to stdout
        return result;
    } else {
        return 0;
    }
}

#endif
