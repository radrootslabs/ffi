# Radroots C FFI library

C FFI library for Radroots.
Build and install locally with `make install-c`; use
`find_package(Radroots CONFIG REQUIRED)` and `Radroots::c_shared` or
`Radroots::c_static`. `Radroots::c` selects shared linkage.
The development prefix is `build/native/install`. See [Developers](../../DEVELOPERS.md)
for the borrowed-memory safety contract, status meanings, and qualification limits.

```c
#include <radroots/radroots.h>
#include <stdio.h>

int main(void) {
    radroots_string_view name = {NULL, 0};
    if (radroots_v1_name(&name) != RADROOTS_OK) {
        return 1;
    }
    fwrite(name.data, 1, name.len, stdout);
    putchar('\n');
    return radroots_v1_print_name() == RADROOTS_OK ? 0 : 1;
}
```
