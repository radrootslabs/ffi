package main

import (
	"sync"

	"github.com/radrootslabs/ffi/bindings/go"
)

func main() {
	if radroots.Name != "Radroots" {
		panic("name")
	}
	var group sync.WaitGroup
	for range 16 {
		group.Go(func() {
			for range 1000 {
				if radroots.ProjectName() != "Radroots" {
					panic("name")
				}
			}
		})
	}
	group.Wait()
	radroots.PrintName()
}
