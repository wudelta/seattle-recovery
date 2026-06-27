# ======================================================================
# FILE: webserver/Dockerfile (PATCH 1 OF 1)
# START: HIGH_PERFORMANCE_NGINX_PROXY_BASE
# ======================================================================
FROM nginx:1.25-alpine

# Erase the default landing page configuration file out of the image layer
RUN rm /etc/nginx/conf.d/default.conf

# Mount our custom async telemetry proxy rules file straight into Nginx
COPY default.conf /etc/nginx/conf.d/default.conf
# ======================================================================
# END: HIGH_PERFORMANCE_NGINX_PROXY_BASE (PATCH 1 OF 1)
# ======================================================================
