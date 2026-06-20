# Build stage
FROM node:20-alpine as build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . ./
RUN npm run build

# Production stage
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
# Copy custom nginx config if we want to support React Router routes, but standard static serve is fine
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
