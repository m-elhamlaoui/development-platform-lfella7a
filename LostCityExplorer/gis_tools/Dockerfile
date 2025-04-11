FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (if needed)
RUN npm run build

# Expose port for the service
EXPOSE 3001

# Run the application
CMD ["npm", "start"] 