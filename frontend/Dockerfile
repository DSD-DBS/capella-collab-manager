FROM node:14 as build

COPY ./ /work/
WORKDIR /work
RUN npm install
RUN npm run build

FROM nginx:latest
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /work/dist/t4cclient /usr/share/nginx/html
