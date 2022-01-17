FROM nginx:latest
COPY nginx.conf /etc/nginx/nginx.conf
COPY /dist/t4cclient /usr/share/nginx/html
