package main

import (
	"archive/zip"
	"fmt"
	"io"
	"os"

	"golang.org/x/mod/module"
	"golang.org/x/mod/sumdb/dirhash"
	modzip "golang.org/x/mod/zip"
)

func files(path string) (map[string]string, error) {
	reader, err := zip.OpenReader(path)
	if err != nil {
		return nil, err
	}
	defer reader.Close()
	result := map[string]string{}
	for _, file := range reader.File {
		if _, exists := result[file.Name]; exists {
			return nil, fmt.Errorf("duplicate module ZIP member")
		}
		stream, err := file.Open()
		if err != nil {
			return nil, err
		}
		content, err := io.ReadAll(stream)
		stream.Close()
		if err != nil {
			return nil, err
		}
		result[file.Name] = string(content)
	}
	return result, nil
}

func check() error {
	if len(os.Args) != 5 {
		return fmt.Errorf("usage: go_zip_check repository revision prepared_zip output_zip")
	}
	module := module.Version{Path: "github.com/radrootslabs/ffi/bindings/go", Version: "v0.0.0"}
	output, err := os.Create(os.Args[4])
	if err != nil {
		return err
	}
	err = modzip.CreateFromVCS(output, module, os.Args[1], os.Args[2], "bindings/go")
	closeErr := output.Close()
	if err != nil {
		return err
	}
	if closeErr != nil {
		return closeErr
	}
	before, err := files(os.Args[3])
	if err != nil {
		return err
	}
	after, err := files(os.Args[4])
	if err != nil {
		return err
	}
	if len(before) != len(after) {
		return fmt.Errorf("module ZIP VCS inventory differs: prepared=%d vcs=%d", len(before), len(after))
	}
	for name, content := range before {
		actual, exists := after[name]
		if !exists || actual != content {
			return fmt.Errorf("module ZIP VCS member differs: %s", name)
		}
	}
	prepared, err := dirhash.HashZip(os.Args[3], dirhash.Hash1)
	if err != nil {
		return err
	}
	vcs, err := dirhash.HashZip(os.Args[4], dirhash.Hash1)
	if err != nil {
		return err
	}
	if prepared != vcs {
		return fmt.Errorf("module ZIP h1 differs")
	}
	fmt.Println(prepared)
	return nil
}

func main() {
	if err := check(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
