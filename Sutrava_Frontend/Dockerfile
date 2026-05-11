# Use Node.js for building the Vite/React application
FROM node:20-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Pass build arguments (e.g. Backend API URL)
ARG VITE_BACKEND_URL
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

# Build the Vite application
RUN npm run build

# Use Nginx to serve the static files
FROM nginx:alpine

# Copy built assets from builder phase
COPY --from=builder /app/dist /usr/share/nginx/html

# Provide a custom Nginx configuration to handle React Router (if needed)
# For simple static sites, the default is fine, but handling SPA routing is safer
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
