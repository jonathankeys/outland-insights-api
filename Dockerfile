FROM amazoncorretto:21-alpine-jdk
ARG JAR_FILE=target/application.jar
COPY ./target/application.jar application.jar
ENTRYPOINT ["java", "-jar", "/application.jar"]
