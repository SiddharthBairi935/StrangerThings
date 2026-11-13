use lucas_rust_smoke::add;

#[test]
fn integration_adds_two_numbers() {
    assert_eq!(add(20, 22), 42);
}