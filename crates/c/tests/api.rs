use radroots_c::*;
use std::mem::{align_of, offset_of, size_of};

#[test]
fn identity_and_layout() {
    assert_eq!(radroots_v1_abi_version(), 65536);
    assert_eq!(
        (RADROOTS_OK, RADROOTS_INVALID_ARGUMENT, RADROOTS_PANIC),
        (0, 1, 2)
    );
    assert_eq!(size_of::<RadrootsStatus>(), 4);
    assert_eq!(size_of::<RadrootsStringView>(), 2 * size_of::<usize>());
    assert_eq!(align_of::<RadrootsStringView>(), align_of::<usize>());
    assert_eq!(offset_of!(RadrootsStringView, data), 0);
    assert_eq!(offset_of!(RadrootsStringView, len), size_of::<usize>());
}

#[test]
fn repeated_and_concurrent() {
    std::thread::scope(|scope| {
        for _ in 0..8 {
            scope.spawn(|| {
                let mut previous: *const std::ffi::c_char = std::ptr::null();
                for _ in 0..1000 {
                    let mut view = RadrootsStringView {
                        data: std::ptr::null(),
                        len: 0,
                    };
                    assert_eq!(unsafe { radroots_v1_name(&mut view) }, RADROOTS_OK);
                    let bytes =
                        unsafe { std::slice::from_raw_parts(view.data.cast::<u8>(), view.len) };
                    assert_eq!(bytes, b"Radroots");
                    if !previous.is_null() {
                        assert_eq!(previous, view.data);
                    }
                    previous = view.data;
                }
            });
        }
    });
}

#[test]
fn null_is_invalid() {
    assert_eq!(
        unsafe { radroots_v1_name(std::ptr::null_mut()) },
        RADROOTS_INVALID_ARGUMENT
    );
}
