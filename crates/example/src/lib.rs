pub const NAME: &str = "Radroots";

#[must_use]
pub const fn name() -> &'static str {
    NAME
}

pub fn print_name() {
    println!("{NAME}");
}
