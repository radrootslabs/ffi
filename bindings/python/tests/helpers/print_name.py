import radroots

if radroots.print_name() is not None:
    raise RuntimeError("print_name must return None")
