# Sem build step (e2e.html e' puro HTML/CSS/JS, sem bundler) - so' precisa
# de um servidor estatico. nginx:alpine e' multi-arch (roda nativo tanto na
# sua maquina quanto na ARM64 do professor).
FROM nginx:alpine
COPY e2e.html /usr/share/nginx/html/index.html
EXPOSE 80
