.DEFAULT_GOAL := help
.PHONY: test-packaged-python
test-packaged-python:
	@bash tools/radroots_ffi/make.sh $@
.PHONY: check-bootstrap check-api check-generation
check-bootstrap check-api check-generation:
	@bash tools/radroots_ffi/make.sh $@
.PHONY: package-c package-cpp test-c-package test-cpp-package package-python package-swift test-swift-consumer build-kotlin-all
package-c package-cpp test-c-package test-cpp-package package-python package-swift test-swift-consumer build-kotlin-all:
	@bash tools/radroots_ffi/make.sh $@
.PHONY: check-rust
check-rust:
	@bash tools/radroots_ffi/make.sh check-rust
.PHONY: help doctor setup setup-apple setup-android setup-linux generate generate-python generate-kotlin generate-swift generate-go build build-rust build-python build-typescript build-node build-wasm build-kotlin build-swift build-swift-apple build-go build-android build-linux check check-generated format test test-python test-node test-wasm test-kotlin test-go test-swift test-linux verify

help:
	@bash tools/radroots_ffi/make.sh help

doctor:
	@bash tools/radroots_ffi/make.sh doctor

setup:
	@bash tools/radroots_ffi/make.sh setup

setup-apple:
	@bash tools/radroots_ffi/make.sh setup-apple

setup-android:
	@bash tools/radroots_ffi/make.sh setup-android

setup-linux:
	@bash tools/radroots_ffi/make.sh setup-linux

generate:
	@bash tools/radroots_ffi/make.sh generate

generate-python:
	@bash tools/radroots_ffi/make.sh generate-python

generate-kotlin:
	@bash tools/radroots_ffi/make.sh generate-kotlin

generate-swift:
	@bash tools/radroots_ffi/make.sh generate-swift

generate-go:
	@bash tools/radroots_ffi/make.sh generate-go

build:
	@bash tools/radroots_ffi/make.sh build

build-rust:
	@bash tools/radroots_ffi/make.sh build-rust

build-python:
	@bash tools/radroots_ffi/make.sh build-python

build-typescript:
	@bash tools/radroots_ffi/make.sh build-typescript

build-node:
	@bash tools/radroots_ffi/make.sh build-node

build-wasm:
	@bash tools/radroots_ffi/make.sh build-wasm

build-kotlin:
	@bash tools/radroots_ffi/make.sh build-kotlin

build-swift:
	@bash tools/radroots_ffi/make.sh build-swift

.PHONY: check-swift-local
check-swift-local:
	@bash tools/radroots_ffi/make.sh check-swift-local

build-swift-apple:
	@bash tools/radroots_ffi/make.sh build-swift-apple

build-go:
	@bash tools/radroots_ffi/make.sh build-go

build-android:
	@bash tools/radroots_ffi/make.sh build-android

build-linux:
	@bash tools/radroots_ffi/make.sh build-linux

check:
	@bash tools/radroots_ffi/make.sh check

check-generated:
	@bash tools/radroots_ffi/make.sh check-generated

format:
	@bash tools/radroots_ffi/make.sh format

test:
	@bash tools/radroots_ffi/make.sh test

test-python:
	@bash tools/radroots_ffi/make.sh test-python

test-node:
	@bash tools/radroots_ffi/make.sh test-node

test-wasm:
	@bash tools/radroots_ffi/make.sh test-wasm

test-kotlin:
	@bash tools/radroots_ffi/make.sh test-kotlin

test-go:
	@bash tools/radroots_ffi/make.sh test-go

test-swift:
	@bash tools/radroots_ffi/make.sh test-swift

test-linux:
	@bash tools/radroots_ffi/make.sh test-linux

verify:
	@bash tools/radroots_ffi/make.sh verify

.PHONY: setup-go
setup-go:
	@bash tools/radroots_ffi/make.sh setup-go

.PHONY: doctor-go
doctor-go:
	@bash tools/radroots_ffi/make.sh doctor-go

.PHONY: check-go-generator
check-go-generator:
	@bash tools/radroots_ffi/make.sh check-go-generator

.PHONY: build-go-all
build-go-all:
	@bash tools/radroots_ffi/make.sh build-go-all

.PHONY: build-node-all build-android-aar
build-node-all:
	@bash tools/radroots_ffi/make.sh build-node-all
build-android-aar:
	@bash tools/radroots_ffi/make.sh build-android-aar

.PHONY: setup-rust
setup-rust:
	@bash tools/radroots_ffi/make.sh setup-rust

.PHONY: setup-python
setup-python:
	@bash tools/radroots_ffi/make.sh setup-python

.PHONY: setup-typescript
setup-typescript:
	@bash tools/radroots_ffi/make.sh setup-typescript

.PHONY: setup-kotlin
setup-kotlin:
	@bash tools/radroots_ffi/make.sh setup-kotlin

.PHONY: setup-swift
setup-swift:
	@bash tools/radroots_ffi/make.sh setup-swift

.PHONY: doctor-rust
doctor-rust:
	@bash tools/radroots_ffi/make.sh doctor-rust

.PHONY: doctor-python
doctor-python:
	@bash tools/radroots_ffi/make.sh doctor-python

.PHONY: doctor-typescript
doctor-typescript:
	@bash tools/radroots_ffi/make.sh doctor-typescript

.PHONY: doctor-kotlin
doctor-kotlin:
	@bash tools/radroots_ffi/make.sh doctor-kotlin

.PHONY: doctor-swift
doctor-swift:
	@bash tools/radroots_ffi/make.sh doctor-swift

.PHONY: test-rust
test-rust:
	@bash tools/radroots_ffi/make.sh test-rust

.PHONY: setup-browser
setup-browser:
	@bash tools/radroots_ffi/make.sh setup-browser

.PHONY: test-browser
test-browser:
	@bash tools/radroots_ffi/make.sh test-browser

.PHONY: test-ios
test-ios:
	@bash tools/radroots_ffi/make.sh test-ios

.PHONY: test-android
test-android:
	@bash tools/radroots_ffi/make.sh test-android

.PHONY: test-swift-platforms
test-swift-platforms:
	@bash tools/radroots_ffi/make.sh test-swift-platforms

.PHONY: test-go-platforms
test-go-platforms:
	@bash tools/radroots_ffi/make.sh test-go-platforms

.PHONY: setup-checks setup-c setup-cpp doctor-c doctor-cpp generate-c check-generated-c build-c build-cpp install-c test-c test-c-static test-c-shared test-c-abi test-c-consumer test-cpp test-cpp-consumer test-cpp-no-exceptions package-typescript package-typescript-all package-go package-kotlin package-kotlin-all package-android test-typescript-consumer test-browser-consumer test-go-consumer test-kotlin-consumer test-python-types stage-swift-dev check-support update-support check-python format-python check-typescript format-typescript check-go format-go check-kotlin format-kotlin check-swift format-swift check-c format-c check-cpp format-cpp
setup-checks setup-c setup-cpp doctor-c doctor-cpp generate-c check-generated-c build-c build-cpp install-c test-c test-c-static test-c-shared test-c-abi test-c-consumer test-cpp test-cpp-consumer test-cpp-no-exceptions package-typescript package-typescript-all package-go package-kotlin package-kotlin-all package-android test-typescript-consumer test-browser-consumer test-go-consumer test-kotlin-consumer test-python-types stage-swift-dev check-support update-support check-python format-python check-typescript format-typescript check-go format-go check-kotlin format-kotlin check-swift format-swift check-c format-c check-cpp format-cpp:
	@bash tools/radroots_ffi/make.sh $@

.PHONY: test-tooling
test-tooling:
	@bash tools/radroots_ffi/make.sh test-tooling
