FROM gradle:8.7-jdk21 AS build

WORKDIR /app
COPY . .
RUN gradle build --no-daemon

FROM eclipse-temurin:21-jre

WORKDIR /app
COPY --from=build /app/build/libs/*.jar ./app.jar
COPY --from=build /app/price.json ./price.json

# Create a volume to persist the price.json file
VOLUME /app/price_data

CMD ["java", "-jar", "app.jar"] 