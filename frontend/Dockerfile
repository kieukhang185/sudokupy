FROM node:20-alpine AS frontend-build

WORKDIR /usr/src/app

COPY frontend/package.json frontend/package-lock.json* ./frontend/

WORKDIR /usr/src/app/frontend

RUN npm install || true

COPY frontend/ .

RUN npm run build

# ---- nginx ----
FROM nginx:alpine

# Nginx conf replaces default
COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built static files
COPY --from=frontend-build /usr/src/app/frontend/dist /usr/share/nginx/html

EXPOSE 80
