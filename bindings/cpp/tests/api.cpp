#include <cassert>
#include <radroots/radroots.hpp>
#include <thread>
#include <vector>

static_assert(noexcept(radroots::name()));
static_assert(noexcept(radroots::print_name()));

int main() {
    std::vector<std::thread> workers;
    for (int i = 0; i < 8; ++i) {
        workers.emplace_back([] {
            for (int j = 0; j < 1000; ++j) {
                const auto result = radroots::name();
                assert(result);
                assert(result.value == "Radroots");
            }
        });
    }
    for (auto &worker : workers) {
        worker.join();
    }
    return radroots::print_name() == radroots::status::ok ? 0 : 1;
}
