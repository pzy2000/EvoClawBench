FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml ./
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-jammy AS runtime
WORKDIR /app
ENV JAVA_OPTS="-Xms256m -Xmx512m -XX:+UseContainerSupport"
COPY --from=builder /app/target/*.jar /app/app.jar
RUN useradd --create-home --shell /bin/bash spring && chown -R spring:spring /app
USER spring
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 CMD java -jar /app/app.jar --spring.main.web-application-type=none --management.endpoint.health.probes.enabled=true || exit 1
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/app.jar"]
