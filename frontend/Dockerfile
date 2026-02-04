# Development stage
FROM oven/bun:1 AS development

WORKDIR /app

COPY package.json bun.lock* /app/

RUN bun install

COPY . /app/

RUN bun run generate-client

EXPOSE 5173

CMD ["bun", "run", "dev", "--host", "0.0.0.0"]


# Build stage
FROM oven/bun:1 AS build-stage

WORKDIR /app

COPY package.json bun.lock* /app/

RUN bun install

COPY . /app/

RUN bun run generate-client

RUN bun run build


# Production stage
FROM nginx:1 AS production

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
