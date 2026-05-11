FROM maven:3.9-amazoncorretto-21 AS build
WORKDIR /app

# Cache dependencies separately (only re-downloads if pom.xml changes)
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source and build
COPY src ./src
RUN rm -f src/main/resources/application-secrets.properties
RUN rm -f src/main/resources/keystore.p12
RUN mvn package -DskipTests

# Run stage
FROM amazoncorretto:21-al2023-headless
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8443

ENTRYPOINT ["java", "-jar", "app.jar"]