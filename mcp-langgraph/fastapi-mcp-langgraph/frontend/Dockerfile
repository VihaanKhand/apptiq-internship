# Step 1: Build the app with Vite
FROM node:20-alpine AS builder

WORKDIR /app
COPY . .
RUN npm install && npm run build

# Step 2: Serve with NGINX
FROM nginx:1.26-alpine

# Copy built files to the correct default NGINX path
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy NGINX config
COPY nginx.conf /etc/nginx/conf.d/default.conf