plugins {
    id("java")
    kotlin("jvm")
    application
}

group = "code.ameer"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.1")
    implementation("org.jsoup:jsoup:1.19.1")
    implementation("redis.clients:jedis:5.2.0")
    implementation("com.google.code.gson:gson:2.12.1")
    testImplementation(platform("org.junit:junit-bom:5.10.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    implementation(kotlin("stdlib-jdk8"))
}

application {
    mainClass.set("code.ameer.MainKt")
}

tasks.jar {
    manifest {
        attributes["Main-Class"] = "code.ameer.MainKt"
    }
    
    // Include all runtime dependencies in the fat JAR
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
    
    from(sourceSets.main.get().output)
    dependsOn(configurations.runtimeClasspath)
    from({
        configurations.runtimeClasspath.get().filter { it.name.endsWith("jar") }.map { zipTree(it) }
    })
}

tasks.test {
    useJUnitPlatform()
}
kotlin {
    jvmToolchain(21)
}