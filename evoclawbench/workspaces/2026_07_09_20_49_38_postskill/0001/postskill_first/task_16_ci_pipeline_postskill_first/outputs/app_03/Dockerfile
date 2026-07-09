FROM golang:1.22-alpine AS builder
WORKDIR /app
RUN apk add --no-cache git
COPY go.mod ./
COPY . .
ENV CGO_ENABLED=0 GOOS=linux
RUN go build -o bin/gateway ./cmd/gateway

FROM scratch
WORKDIR /app
COPY --from=builder /app/bin/gateway /gateway
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD ["/gateway", "healthcheck"]
ENTRYPOINT ["/gateway"]
