# Radroots TypeScript FFI library

TypeScript FFI library for Radroots.

```bash
npm install radroots
```

```ts
import { name, printName } from "radroots";

console.assert(name() === "Radroots");
printName();
```

For browsers, use the WebAssembly entry point and initialize it before calling
the API:

```ts
import { initialize, name, printName } from "radroots/browser";

await initialize();
console.assert(name() === "Radroots");
printName();
```

Serve the generated `.wasm` asset alongside its JavaScript module. Browser
initialization accepts an explicit module or URL when the application serves
the asset elsewhere. This entry point uses browser WebAssembly, not WASI.

## Source layout

| Directory | Ownership |
| --- | --- |
| `src/` | Handwritten TypeScript public entry points |
| `native/` | napi-rs generated Node loader and declarations; ignored local `.node` binaries |
| `wasm/` | wasm-bindgen generated browser glue and declarations; ignored `.wasm` binary and packaging metadata |
| `test/` | Node API tests, WASM tests under Node, Chromium browser tests, fixtures and consumer type checks |
| `dist/` | Ignored compiled JavaScript and declarations |

Generated source is maintained through the pinned generators, never edited by
hand. Platform npm packages are generated into the FFI library's ignored
`build/typescript/npm/<platform-arch-abi>/` staging directory. Their package
names remain `@radroots/native-<platform-arch-abi>`; only active targets are
generated. Local archives are written to `build/dist/npm/` at the FFI library root.

See the repository's `DEVELOPERS.md` for prerequisites and Make commands.
