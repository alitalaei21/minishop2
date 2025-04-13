# Gold Price API

A Kotlin application that fetches and stores gold prices.

## Running with Docker

### Prerequisites
- Docker
- Docker Compose

### Build and Run
To build and run the application:

```bash
docker-compose up -d
```

This will:
1. Build the Docker image
2. Start the container in detached mode
3. Store the price data in a persistent volume

### Accessing Data
The gold price data is stored in a JSON file at:
- Inside the container: `/app/price.json` and `/app/price_data/price.json`
- On your host: `./price_data/price.json`

### Logs
To view the logs:

```bash
docker-compose logs -f
```

### Stopping
To stop the container:

```bash
docker-compose down
```

## Development

To build without Docker:

```bash
./gradlew build
```

To run without Docker:

```bash
./gradlew run
``` 