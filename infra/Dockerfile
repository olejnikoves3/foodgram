FROM nginx:1.25.4-alpine
RUN sed -i '/http {/a\    server_tokens off;' /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/templates/default.conf.template