# Radroots Kotlin SDK

Version 0.0.0 is unpublished. From the repository root, use `make test-kotlin`
for local verification. Registry installation examples describe intended distributions.

Kotlin SDK for Radroots.

```kotlin
implementation("org.radroots:radroots:0.0.0")
```

```kotlin
import org.radroots.Radroots

check(Radroots.name() == "Radroots")
Radroots.printName()
```
