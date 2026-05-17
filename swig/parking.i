%module parking

%{
#include "parking_core.h"
%}

%include "stdint.i"

%include "parking_core.h"

%inline %{
/* Helpers for Python when typemaps are not generated */
%}
