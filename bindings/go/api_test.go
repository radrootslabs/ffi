package radroots_test

import (
	"os/exec"
	"sync"
	"testing"

	"radroots.org"
)

func TestIdentity(t *testing.T) {
	const identity = radroots.Name
	if identity != "Radroots" || radroots.ProjectName() != "Radroots" {
		t.Fatal("public identity differs")
	}
}

func TestRepeatedCalls(t *testing.T) {
	for range 1000 {
		if got := radroots.ProjectName(); got != "Radroots" {
			t.Fatalf("ProjectName() = %q", got)
		}
	}
}

func TestConcurrentCalls(t *testing.T) {
	var group sync.WaitGroup
	for range 8 {
		group.Go(func() {
			for range 128 {
				if got := radroots.ProjectName(); got != "Radroots" {
					t.Errorf("ProjectName() = %q", got)
				}
			}
		})
	}
	group.Wait()
}

func TestPrintName(t *testing.T) {
	output, err := exec.Command("go", "run", "./testdata/print-name").Output()
	if err != nil {
		t.Fatal(err)
	}
	if string(output) != "Radroots\n" {
		t.Fatalf("PrintName output = %q", output)
	}
}
