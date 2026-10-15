# Radroots FFI library capsule

This repository is a standalone public FFI-library capsule. Its approved first
release is version `0.0.0`, backed by the `radroots` Rust SDK in `crates/example`.
The SDK is publishable to crates.io; adapter crates remain unpublished. Existing
public 0.0.0 artifacts and tags are immutable and retain their original provenance.
Read `contracts/bootstrap.toml`, `Cargo.toml`, language manifests, and relevant
tests before changing source. Canonical lib/SDK integration is deferred.

- Keep public source independent of the private monorepo and its credentials.
- Preserve package/module identities and edit generators rather than generated
  bindings. Run the affected generator and freshness checks after input changes.
- Durable capsule commands belong in `tools/radroots_ffi`; Make is a thin shim.
- Run `cargo extbuild doctor` before the first mutating build/check/test/install/
  package/generation command, then use `cargo extbuild run -- <command>`.
- extbuild owns build-output routing. Do not add target-directory overrides.
- Do not add active `.github/**` workflows. Local act orchestration belongs to
  the private parent `.act/**`; the capsule remains independently testable.
- Signing, registry uploads, release promotion, and credentials are external to
  this capsule. Local packaging must never publish implicitly.
- Verify the narrowest affected Rust checks/tests and language consumers. Record
  missing runners and skipped checks without claiming platform qualification.
- Preserve independent Git history; commits require authorization and do not
  authorize pushes, tags, or publication.
