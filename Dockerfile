FROM eclipse-temurin:25-jdk AS build
WORKDIR /workspace

COPY gradlew settings.gradle.kts build.gradle.kts ./
COPY gradle.properties ./
COPY gradle ./gradle
COPY app ./app

RUN ./gradlew :app:common-config:bootJar --no-daemon

FROM eclipse-temurin:25-jre
WORKDIR /app

COPY --from=build /workspace/app/common-config/build/libs/*.jar /app/common-config.jar

EXPOSE 8085
ENTRYPOINT ["java", "-jar", "/app/common-config.jar"]
