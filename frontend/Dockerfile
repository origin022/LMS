# 1. Base Stage: Install dependencies
FROM node:20-slim AS base
WORKDIR /app
COPY package*.json ./
RUN npm install

# 2. Development Stage: For local dev with hot-reloading (used by docker-compose)
FROM base AS dev
COPY . .
# Expose Vite's default port
EXPOSE 5173
# Start Vite development server, listening on all network interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# 3. Builder Stage: For production build
FROM base AS builder
COPY . .
RUN npm run build

# 4. Production Stage: Serve static files using Nginx
FROM nginx:stable-alpine AS production
RUN echo 'server { \
    listen 80; \
    location / { \
    root /usr/share/nginx/html; \
    index index.html; \
    try_files $uri $uri/ /index.html; \
    } \
    }' > /etc/nginx/conf.d/default.conf

COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]