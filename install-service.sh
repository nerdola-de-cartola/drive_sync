#!/bin/bash

# Script para instalar o serviço drive-sync no systemd

set -e  # Parar em caso de erro

PROJECT_DIR="/home/matheus-lucas/drive_sync"
SERVICE_NAME="drive-sync"
SERVICE_FILE="${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "🚀 Instalando serviço ${SERVICE_NAME}..."

# Verificar se o arquivo de serviço existe
if [ ! -f "${PROJECT_DIR}/${SERVICE_FILE}" ]; then
    echo "❌ Erro: Arquivo ${SERVICE_FILE} não encontrado em ${PROJECT_DIR}"
    exit 1
fi

# Verificar se o usuário tem privilégios sudo
if ! sudo -n true 2>/dev/null; then
    echo "❌ Este script precisa de privilégios sudo para instalar o serviço systemd"
    echo "Execute: sudo ./install-service.sh"
    exit 1
fi

echo "📁 Copiando arquivo de serviço para ${SYSTEMD_DIR}..."
sudo cp "${PROJECT_DIR}/${SERVICE_FILE}" "${SYSTEMD_DIR}/"

echo "🔄 Recarregando configuração do systemd..."
sudo systemctl daemon-reload

echo "✅ Habilitando serviço para iniciar automaticamente..."
sudo systemctl enable "${SERVICE_NAME}"

echo "🎯 Verificando status do serviço..."
sudo systemctl status "${SERVICE_NAME}" --no-pager || true

echo ""
echo "📋 Comandos úteis para gerenciar o serviço:"
echo "  Iniciar:    sudo systemctl start ${SERVICE_NAME}"
echo "  Parar:      sudo systemctl stop ${SERVICE_NAME}"
echo "  Reiniciar:  sudo systemctl restart ${SERVICE_NAME}"
echo "  Status:     sudo systemctl status ${SERVICE_NAME}"
echo "  Logs:       sudo journalctl -u ${SERVICE_NAME} -f"
echo "  Desabilitar: sudo systemctl disable ${SERVICE_NAME}"
echo ""
echo "✨ Instalação concluída! Execute 'sudo systemctl start ${SERVICE_NAME}' para iniciar o serviço."
