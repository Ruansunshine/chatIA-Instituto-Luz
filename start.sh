#!/bin/bash
# Sobe o projeto inteiro detectando sozinho se tem GPU NVIDIA disponivel -
# nao precisa saber de antemao se a maquina tem GPU ou nao. Versao Linux/Mac
# do start.ps1 (Windows).
set -e

if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
  echo "GPU NVIDIA detectada - subindo com aceleracao de GPU."
  docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
else
  echo "Nenhuma GPU NVIDIA detectada - subindo em CPU (funciona igual, so mais lento na IA)."
  docker compose up -d --build
fi
