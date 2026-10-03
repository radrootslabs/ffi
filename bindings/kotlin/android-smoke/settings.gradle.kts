pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        maven { url = uri("repository") }
    }
}

rootProject.name = "radroots_consumer"

if (!file("repository").exists()) {
    val sdk = file(providers.gradleProperty("sdkSource").orNull ?: "..")
    includeBuild(sdk.resolve("android"))
    includeBuild(sdk) {
        dependencySubstitution {
            substitute(module("org.radroots:radroots")).using(project(":lib"))
        }
    }
}
