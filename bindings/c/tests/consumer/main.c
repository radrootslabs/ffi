#include <radroots/radroots.h>
#include <string.h>

int main(void) {
    radroots_string_view name = {NULL, 0};
    if (radroots_v1_abi_version() != RADROOTS_ABI_VERSION ||
        radroots_v1_name(&name) != RADROOTS_OK ||
        name.len != sizeof("Radroots") - 1 ||
        memcmp(name.data, "Radroots", name.len) != 0) {
        return 1;
    }
    return radroots_v1_print_name() == RADROOTS_OK ? 0 : 1;
}
