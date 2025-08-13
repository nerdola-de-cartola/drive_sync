#!/bin/bash

# Script para desinstalar o serviço drive-sync do systemd

set -e  # Parar em caso de erro

SERVICE_NAME="drive-sync"
SERVICE_FILE="${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "🗑️  Desinstalando serviço ${SERVICE_NAME}..."

# Verificar se o usuário tem privilégios sudo
if ! sudo -n true 2>/dev/null; then
    echo "❌ Este script precisa de privilégios sudo para remover o serviço systemd"
    echo "Execute: sudo ./uninstall-service.sh"
    exit 1
fi

# Parar o serviço se estiver rodando
echo "⏹️  Parando serviço..."
sudo systemctl stop "${SERVICE_NAME}" 2>/dev/null || echo "Serviço já estava parado"

# Desabilitar o serviço
echo "❌ Desabilitando serviço..."
sudo systemctl disable "${SERVICE_NAME}" 2>/dev/null || echo "Serviço já estava desabilitado"

# Remover arquivo de serviço
if [ -f "${SYSTEMD_DIR}/${SERVICE_FILE}" ]; then
    echo "🗑️  Removendo arquivo de serviço..."
    sudo rm "${SYSTEMD_DIR}/${SERVICE_FILE}"
fi

# Recarregar configuração do systemd
echo "🔄 Recarregando configuração do systemd..."
sudo systemctl daemon-reload

echo "✅ Desinstalação concluída!"
echo "O serviço ${SERVICE_NAME} foi removido completamente do sistema."
