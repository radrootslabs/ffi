#include <cassert>
#include <initializer_list>
#include <radroots/radroots.hpp>

extern "C" void radroots_test_status(radroots_status code);

int main() {
    static_assert(noexcept(radroots::name()));
    static_assert(noexcept(radroots::print_name()));
    for (radroots_status code :
         {RADROOTS_INVALID_ARGUMENT, RADROOTS_PANIC, 99}) {
        radroots_test_status(code);
        const auto result = radroots::name();
        assert(!result);
        assert(result.value.empty());
        assert(static_cast<std::uint32_t>(result.code) == code);
        assert(static_cast<std::uint32_t>(radroots::print_name()) == code);
    }
    radroots_test_status(RADROOTS_OK);
    const auto empty = radroots::name();
    assert(empty);
    assert(empty.value.empty());
    assert(radroots::print_name() == radroots::status::ok);
    return 0;
}
