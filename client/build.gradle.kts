plugins {
    `java-library`
    `maven-publish`
    signing
}

group = "de.tum.in.ase.athene"
version = "0.0.2"

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
        languageVersion.set(JavaLanguageVersion.of(16))
    }
}

dependencies {
    implementation("com.google.protobuf", "protobuf-java", "3.15.8")
}

publishing {
    publications {
        create<MavenPublication>("main") {
            from(components["java"])

            pom {
                name.set("Athene Client")
                url.set("https://github.com/ls1intum/Athene")
                description.set("A system to support (semi-)automated assessment of textual exercises.")
                licenses {
                    license {
                        name.set("MIT License")
                        url.set("https://github.com/ls1intum/Athene/blob/master/LICENSE.md'")
                    }
                }
                developers {
                    developer {
                        id.set("jpbernius")
                        name.set("Jan Philip Bernius")
                        email.set("janphilip.bernius@tum.de")
                        url.set("https://ase.in.tum.de/bernius")
                        organization.set("Technical University of Munich, Applied Software Engineering")
                        organizationUrl.set("https://ase.in.tum.de")

                    }
                }
                scm {
                    connection.set("scm:git:https://github.com/ls1intum/Athene.git")
                    developerConnection.set("scm:git:ssh://git@github.com:ls1intum/Athene.git'")
                    url.set("https://github.com/ls1intum/Athene")
                }
            }
        }
    }
    repositories {
        maven {
            val releasesRepoUrl = uri("https://oss.sonatype.org/service/local/staging/deploy/maven2/")
            val snapshotsRepoUrl = uri("https://oss.sonatype.org/content/repositories/snapshots")
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
