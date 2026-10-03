#[napi_derive::napi]
pub fn name() -> String {
    radroots::name().to_owned()
}

#[napi_derive::napi]
pub fn print_name() {
    radroots::print_name();
}
