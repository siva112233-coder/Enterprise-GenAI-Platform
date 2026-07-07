# =============================================================================
# Enterprise GenAI Platform — Frontend Dockerfile
# =============================================================================

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy lockfile and package.json
COPY frontend/package*.json ./
RUN npm ci

# Copy source code and build
COPY frontend/ .
RUN npm run build

# Production serve stage (Nginx)
FROM nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
