plugins {
    `java-library`
    `maven-publish`
    signing
}

group = "de.tum.cit.ase"
version = "1.0.0"

tasks.register("version") {
    println("$version")
}

val isRelease = !"$version".endsWith("-SNAPSHOT")

repositories {
    mavenCentral()
}

java {
    withJavadocJar()
    withSourcesJar()
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(20))
    }
}

dependencies {
    implementation("com.google.protobuf", "protobuf-java", "3.20.3")
}

publishing {
    publications {
        create<MavenPublication>("main") {
            from(components["java"])

            pom {
                name.set("Athena Client")
                url.set("https://github.com/ls1intum/Athena")
                description.set("A system to support (semi-)automated assessment of textual exercises.")
                licenses {
                    license {
                        name.set("MIT License")
                        url.set("https://github.com/ls1intum/Athena/blob/main/LICENSE.md'")
                    }
                }
                developers {
                    developer {
                        id.set("jpbernius")
                        name.set("Jan Philip Bernius")
                        email.set("janphilip.bernius@tum.de")
                        url.set("https://ase.cit.tum.de/bernius")
                        organization.set("Technical University of Munich, Applied Software Engineering")
                        organizationUrl.set("https://ase.cit.tum.de")

                    }
                }
                scm {
                    connection.set("scm:git:https://github.com/ls1intum/Athena.git")
                    developerConnection.set("scm:git:ssh://git@github.com:ls1intum/Athena.git'")
                    url.set("https://github.com/ls1intum/Athena")
                }
            }
        }
    }
    repositories {
        maven {
            val releasesRepoUrl = uri("https://s01.oss.sonatype.org/service/local/staging/deploy/maven2/")
            val snapshotsRepoUrl = uri("https://s01.oss.sonatype.org/content/repositories/snapshots")
            url = if (isRelease) releasesRepoUrl else snapshotsRepoUrl
            credentials {
                username = System.getenv("OSSRH_USERNAME")
                password = System.getenv("OSSRH_PASSWORD")
            }
        }
    }
}

signing {
    setRequired { isRelease }

    useInMemoryPgpKeys(System.getenv("GPG_KEY"), System.getenv("GPG_PASSPHRASE"))

    sign(publishing.publications["main"])
}
