#include <radroots/radroots.hpp>

int main() {
    const auto result = radroots::name();
    if (!result || result.value != "Radroots") {
        return 1;
    }
    return radroots::print_name() == radroots::status::ok ? 0 : 1;
}
