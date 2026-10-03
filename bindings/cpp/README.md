# Radroots C++ SDK

Version 0.0.0 is unpublished. From the repository root, use `make test-cpp`
for local verification. Registry installation examples describe intended distributions.

C++ SDK for Radroots.

Build locally with `make build-cpp`; use
`find_package(RadrootsCpp CONFIG REQUIRED)` and `Radroots::cpp` or
`Radroots::cpp_static`. The development prefix is `build/native/install`.
See [Developers](../../DEVELOPERS.md) for ownership, status, and qualification contracts.

```cpp
#include <radroots/radroots.hpp>
#include <iostream>

int main() {
    const auto result = radroots::name();
    if (!result) {
        return 1;
    }
    std::cout << result.value << '\n';
    return radroots::print_name() == radroots::status::ok ? 0 : 1;
}
```
