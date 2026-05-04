plugins {
    kotlin("plugin.spring")
    id("org.springframework.boot")
}

val kotestVersion: String by rootProject
val springdocVersion: String by rootProject

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    implementation("org.springframework.cloud:spring-cloud-config-server")
    implementation("org.springframework.vault:spring-vault-core")
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:$springdocVersion")

    testImplementation("io.kotest:kotest-runner-junit5-jvm:$kotestVersion")
    testImplementation("io.kotest:kotest-assertions-core-jvm:$kotestVersion")
}
