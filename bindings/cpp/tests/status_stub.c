#include <radroots/radroots.h>

static radroots_status selected;

void radroots_test_status(radroots_status code) { selected = code; }

uint32_t radroots_v1_abi_version(void) { return RADROOTS_ABI_VERSION; }

radroots_status radroots_v1_name(radroots_string_view *output) {
    output->data = selected == RADROOTS_OK ? NULL : "ignored";
    output->len = selected == RADROOTS_OK ? 0 : 7;
    return selected;
}

radroots_status radroots_v1_print_name(void) { return selected; }
