include(CheckCXXSourceCompiles)
include(CheckLibraryExists)

# BestClient browser redesign build hook.
# This is intentionally inert for normal branches. The redesign branch carries
# .design/browser-redesign.patch and CI applies it once before compiling.
set(_BESTCLIENT_BROWSER_REDESIGN_PATCH "${PROJECT_SOURCE_DIR}/.design/browser-redesign.patch")
set(_BESTCLIENT_BROWSER_SOURCE "${PROJECT_SOURCE_DIR}/src/game/client/components/menus_browser.cpp")
if(EXISTS "${_BESTCLIENT_BROWSER_REDESIGN_PATCH}" AND EXISTS "${_BESTCLIENT_BROWSER_SOURCE}")
  file(READ "${_BESTCLIENT_BROWSER_SOURCE}" _BESTCLIENT_BROWSER_SOURCE_TEXT)
  string(FIND "${_BESTCLIENT_BROWSER_SOURCE_TEXT}" "namespace BrowserVisual" _BESTCLIENT_BROWSER_REDESIGN_MARKER)
  if(_BESTCLIENT_BROWSER_REDESIGN_MARKER EQUAL -1)
    find_program(_BESTCLIENT_GIT_EXECUTABLE git)
    if(NOT _BESTCLIENT_GIT_EXECUTABLE)
      message(FATAL_ERROR "Browser redesign patch is present, but git was not found")
    endif()
    execute_process(
      COMMAND "${_BESTCLIENT_GIT_EXECUTABLE}" apply --check "${_BESTCLIENT_BROWSER_REDESIGN_PATCH}"
      WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
      RESULT_VARIABLE _BESTCLIENT_BROWSER_PATCH_CHECK
      ERROR_VARIABLE _BESTCLIENT_BROWSER_PATCH_ERROR
    )
    if(NOT _BESTCLIENT_BROWSER_PATCH_CHECK EQUAL 0)
      message(FATAL_ERROR "Browser redesign patch no longer applies cleanly: ${_BESTCLIENT_BROWSER_PATCH_ERROR}")
    endif()
    execute_process(
      COMMAND "${_BESTCLIENT_GIT_EXECUTABLE}" apply "${_BESTCLIENT_BROWSER_REDESIGN_PATCH}"
      WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
      RESULT_VARIABLE _BESTCLIENT_BROWSER_PATCH_RESULT
      ERROR_VARIABLE _BESTCLIENT_BROWSER_PATCH_ERROR
    )
    if(NOT _BESTCLIENT_BROWSER_PATCH_RESULT EQUAL 0)
      message(FATAL_ERROR "Failed to apply browser redesign patch: ${_BESTCLIENT_BROWSER_PATCH_ERROR}")
    endif()
    message(STATUS "Applied BestClient native browser redesign")
  endif()
endif()

# Sometimes linking against libatomic is required for atomic ops, if
# the platform doesn't support lock-free atomics.

function(check_working_cxx_atomics varname)
  set(OLD_CMAKE_REQUIRED_FLAGS ${CMAKE_REQUIRED_FLAGS})
  set(CMAKE_REQUIRED_FLAGS "${CMAKE_REQUIRED_FLAGS} -std=c++11")
  check_cxx_source_compiles("
#include <atomic>
#include <cstdint>
std::atomic<int> x1;
std::atomic<short> x2;
std::atomic<char> x3;
std::atomic<uint64_t> x (0);
int main() {
  uint64_t i = x.load(std::memory_order_relaxed);
  (void)i;
  ++x3;
  ++x2;
  return ++x1;
}
" ${varname})
  set(CMAKE_REQUIRED_FLAGS ${OLD_CMAKE_REQUIRED_FLAGS})
endfunction(check_working_cxx_atomics)

if(NOT DEFINED COMPILER_IS_GCC_COMPATIBLE)
  if(MSVC OR APPLE)
    set(COMPILER_IS_GCC_COMPATIBLE OFF)
  else()
    set(COMPILER_IS_GCC_COMPATIBLE ON)
  endif()
endif()

if(NOT COMPILER_IS_GCC_COMPATIBLE)
  set(HAVE_ATOMICS_WITHOUT_LIB ON)
else()
  # Check for 64 bit atomic operations.
  # First check if atomics work without the library.
  check_working_cxx_atomics(HAVE_ATOMICS_WITHOUT_LIB)
  # If not, check if the library exists, and atomics work with it.
  if(NOT HAVE_ATOMICS_WITHOUT_LIB)
    check_library_exists(atomic __atomic_load_8 "" HAVE_LIBATOMICS)
    mark_as_advanced(HAVE_LIBATOMICS)
    if(NOT HAVE_LIBATOMICS)
      message(FATAL_ERROR "Host compiler appears to require libatomic, but cannot find it.")
    endif()
    list(APPEND CMAKE_REQUIRED_LIBRARIES "atomic")
    check_working_cxx_atomics(HAVE_ATOMICS_WITH_LIB)
    if(NOT HAVE_ATOMICS_WITH_LIB)
      message(FATAL_ERROR "Host compiler must support std::atomic!")
    endif()
    list(APPEND CMAKE_C_STANDARD_LIBRARIES "-latomic")
    list(APPEND CMAKE_CXX_STANDARD_LIBRARIES "-latomic")
  endif()
endif()
