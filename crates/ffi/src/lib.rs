uniffi::setup_scaffolding!();

#[uniffi::export]
pub fn name() -> String {
    radroots::name().to_owned()
}

#[uniffi::export]
pub fn print_name() {
    radroots::print_name();
}
