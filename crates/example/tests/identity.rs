#[test]
fn identity_is_radroots() {
    assert_eq!(radroots_ffi_example::NAME, "Radroots");
    assert_eq!(radroots_ffi_example::name(), "Radroots");
}
