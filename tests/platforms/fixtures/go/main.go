package main

import (
	"sync"

	"radroots.org"
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
