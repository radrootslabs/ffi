#include <radroots/radroots.h>
#include <stddef.h>
#include <stdio.h>

_Static_assert(sizeof(radroots_status) == 4, "status width");
_Static_assert(RADROOTS_ABI_VERSION == 65536, "ABI identity");
_Static_assert(RADROOTS_OK == 0, "success status");
_Static_assert(RADROOTS_INVALID_ARGUMENT == 1, "argument status");
_Static_assert(RADROOTS_PANIC == 2, "panic status");

int main(void) {
    printf("{\"pointer_bits\":%zu,\"size\":%zu,\"alignment\":%zu,\"data_"
           "offset\":%zu,\"len_offset\":%zu}\n",
           sizeof(void *) * 8, sizeof(radroots_string_view),
           _Alignof(radroots_string_view), offsetof(radroots_string_view, data),
           offsetof(radroots_string_view, len));
    return 0;
}
