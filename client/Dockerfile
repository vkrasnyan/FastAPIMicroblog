FROM nginx

# Удаляем стандартные конфиги
RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Копируем статические файлы фронта
COPY /client/static /app/static

# Копируем кастомный конфиг Nginx
COPY /client/nginx.conf /etc/nginx/nginx.conf
