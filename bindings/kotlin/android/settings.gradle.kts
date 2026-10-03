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
    }
}

rootProject.name = "radroots-android"

includeBuild("..") {
    name = "radroots"
    dependencySubstitution { substitute(module("org.radroots:radroots")).using(project(":lib")) }
}
