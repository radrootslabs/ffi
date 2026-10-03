# Radroots FFI

Multi-language bindings and local package tooling for [Radroots](https://radroots.org).

Version 0.0.0 is an unpublished bootstrap. The current example returns `Radroots`
and prints the name. It exercises generation, native loading, language facades,
and installed-package consumers for C, C++, Go, Kotlin/Java, Python, Swift, and
TypeScript (Node.js and browser WebAssembly).

The small Rust implementation lives in `crates/example`, named
`radroots_ffi_example` and imported by adapters as `radroots`. It does not replace
the canonical Rust SDK in [radrootslabs/lib](https://github.com/radrootslabs/lib).
Connecting that SDK at an immutable public revision is a separate step.

| Directory | Purpose |
| --- | --- |
| `crates/` | Example core and UniFFI, Node.js, WebAssembly, and C adapters |
| `bindings/` | Language facades, generated bindings, manifests, and tests |
| `tools/radroots_ffi/` | Standalone generation, build, test, and local packaging commands |
| `tests/` | Installed-package consumers and intended platform metadata |
| `contracts/` | Initial repository identity and example API scope |

Start with [DEVELOPERS.md](DEVELOPERS.md) for toolchains and language-specific
commands. With Rust 1.97.1 and jq installed:

```sh
make setup-rust
make test-rust
make check-rust
```

`make help` lists the complete command surface.
Swift's root manifest consumes a locally built XCFramework;
run `make build-swift` first. Package names and remote-install examples in the
language READMEs describe intended distributions, not currently published
packages. Local package tests work without publishing the SDK.

The API prints to native stdout, or browser `console.log` after explicit WASM
initialization. See each language README for usage.

Original project material is available under either [MIT](LICENSE-MIT) or
[Apache-2.0](LICENSE-APACHE).
