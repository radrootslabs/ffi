package radroots

import native "radroots.org/internal/native"

const Name = "Radroots"

func ProjectName() string {
	return native.Name()
}

func PrintName() {
	native.PrintName()
}
