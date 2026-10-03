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
        exclusiveContent {
            forRepository { maven { url = uri("repository") } }
            filter { includeGroup("org.radroots") }
        }
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
