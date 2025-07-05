# Base stage for shared configuration
FROM node:18-alpine as base

WORKDIR /app

# Copy package files
COPY package*.json ./

# Development stage
FROM base as development

# Install all dependencies including dev dependencies
RUN npm install

# Set environment for development
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Copy project files for development
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application in development mode with host binding
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]

# Build stage
FROM base as builder

# Install dependencies
RUN npm ci

# Copy project files
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine as production

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy built application from builder
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]