#include <assert.h>
#include <pthread.h>
#include <radroots/radroots.h>
#include <string.h>

static void *exercise(void *argument) {
    (void)argument;
    const char *previous = NULL;
    for (int i = 0; i < 1000; ++i) {
        radroots_string_view name = {NULL, 0};
        assert(radroots_v1_name(&name) == RADROOTS_OK);
        assert(name.len == sizeof("Radroots") - 1);
        assert(memcmp(name.data, "Radroots", name.len) == 0);
        assert(previous == NULL || previous == name.data);
        previous = name.data;
    }
    return NULL;
}

int main(void) {
    assert(radroots_v1_abi_version() == RADROOTS_ABI_VERSION);
    assert(radroots_v1_name(NULL) == RADROOTS_INVALID_ARGUMENT);
    pthread_t threads[8];
    for (int i = 0; i < 8; ++i) {
        assert(pthread_create(&threads[i], NULL, exercise, NULL) == 0);
    }
    for (int i = 0; i < 8; ++i) {
        assert(pthread_join(threads[i], NULL) == 0);
    }
    return 0;
}
