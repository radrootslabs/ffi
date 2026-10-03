# Radroots Kotlin FFI library

Version 0.0.0 is unpublished. From the repository root, use `make test-kotlin`
for local verification. Registry installation examples describe intended distributions.

Kotlin FFI library for Radroots.

```kotlin
implementation("org.radroots:radroots:0.0.0")
```

```kotlin
import org.radroots.Radroots

check(Radroots.name() == "Radroots")
Radroots.printName()
```
