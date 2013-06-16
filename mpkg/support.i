%module support
%{
#include "mpkgsupport/mpkgsupport.h"

%}

%include <std_string.i>
int compareVersions(const std::string& version1, const std::string& build1, const std::string& version2, const std::string& build2);
