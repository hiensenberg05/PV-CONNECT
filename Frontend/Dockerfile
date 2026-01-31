# ============================================
# Frontend Dockerfile (Vite React)
# ============================================

FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run development server (use npm run build && serve for production)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
