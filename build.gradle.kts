import io.spring.gradle.dependencymanagement.dsl.DependencyManagementExtension
import org.jetbrains.kotlin.gradle.dsl.KotlinJvmProjectExtension
import org.springframework.boot.gradle.plugin.SpringBootPlugin

plugins {
    kotlin("jvm") apply false
    kotlin("plugin.spring") apply false
    id("org.springframework.boot") apply false
    id("io.spring.dependency-management") apply false
}

allprojects {
    group = "dev.hyunec"
    version = "0.0.1-SNAPSHOT"
}

subprojects {
    apply(plugin = "org.jetbrains.kotlin.jvm")
    apply(plugin = "io.spring.dependency-management")

    val javaVersion: String by rootProject
    val springCloudVersion: String by rootProject

    the<DependencyManagementExtension>().apply {
        imports {
            mavenBom(SpringBootPlugin.BOM_COORDINATES)
            mavenBom("org.springframework.cloud:spring-cloud-dependencies:$springCloudVersion")
        }
    }

    extensions.configure<KotlinJvmProjectExtension> {
        jvmToolchain(javaVersion.toInt())
    }

    dependencies {
        "implementation"("org.jetbrains.kotlin:kotlin-reflect")
    }

    tasks.withType<Test>().configureEach {
        useJUnitPlatform()
    }
}
