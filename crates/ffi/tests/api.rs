#[test]
fn identity() {
    assert_eq!(radroots_ffi::name(), "Radroots");
}

#[test]
fn repeated_calls() {
    for _ in 0..1000 {
        assert_eq!(radroots_ffi::name(), "Radroots");
    }
}

#[test]
fn concurrent_calls() {
    std::thread::scope(|scope| {
        for _ in 0..8 {
            scope.spawn(|| {
                for _ in 0..128 {
                    assert_eq!(radroots_ffi::name(), "Radroots");
                }
            });
        }
    });
}

#[test]
fn print_name() {
    let output = std::process::Command::new(
        std::env::current_exe()
            .unwrap()
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .join("examples/print-name"),
    )
    .output()
    .unwrap();
    assert!(output.status.success());
    assert_eq!(output.stdout, b"Radroots\n");
    assert!(output.stderr.is_empty());
}
