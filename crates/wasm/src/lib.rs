use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn name() -> String {
    radroots::name().to_owned()
}
