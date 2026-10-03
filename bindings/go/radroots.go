package radroots

import native "github.com/radrootslabs/ffi/bindings/go/internal/native"

const Name = "Radroots"

func ProjectName() string {
	return native.Name()
}

func PrintName() {
	native.PrintName()
}
