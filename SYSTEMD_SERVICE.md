# Serviço Systemd - Drive Sync

Este guia explica como configurar o Drive Sync como um serviço systemd para rodar automaticamente na inicialização do sistema.

## Instalação

### 1. Instalar o serviço

```bash
sudo ./install-service.sh
```

### 2. Iniciar o serviço

```bash
sudo systemctl start drive-sync
```

### 3. Verificar status

```bash
sudo systemctl status drive-sync
```

## Comandos de Gerenciamento

### Controle básico
```bash
# Iniciar serviço
sudo systemctl start drive-sync

# Parar serviço
sudo systemctl stop drive-sync

# Reiniciar serviço
sudo systemctl restart drive-sync

# Verificar status
sudo systemctl status drive-sync
```

### Logs
```bash
# Ver logs em tempo real
sudo journalctl -u drive-sync -f

# Ver logs das últimas linhas
sudo journalctl -u drive-sync -n 50

# Ver logs desde hoje
sudo journalctl -u drive-sync --since today
```

### Auto-inicialização
```bash
# Habilitar para iniciar automaticamente (já feito na instalação)
sudo systemctl enable drive-sync

# Desabilitar auto-inicialização
sudo systemctl disable drive-sync
```

## Configuração

O serviço usa as mesmas configurações do arquivo `.env` no diretório do projeto:
- `WATCH_DIR`: Diretório a ser monitorado
- `CREDENTIALS_DIR`: Diretório das credenciais do Google Drive
- `DATA_DIR`: Diretório do banco de dados
- `SUPER_FOLDER`: Pasta base para cálculos de caminho relativo

## Desinstalação

Para remover completamente o serviço:

```bash
sudo ./uninstall-service.sh
```

## Troubleshooting

### Serviço não inicia
1. Verifique se todas as dependências estão instaladas
2. Verifique se o arquivo `.env` existe e está configurado corretamente
3. Verifique os logs: `sudo journalctl -u drive-sync -n 20`

### Problemas de permissão
- O serviço roda com o usuário `matheus-lucas`
- Certifique-se de que este usuário tem acesso aos diretórios configurados

### Verificar configuração do serviço
```bash
# Ver configuração atual
sudo systemctl cat drive-sync

# Recarregar após mudanças no arquivo .service
sudo systemctl daemon-reload
sudo systemctl restart drive-sync
```

## Estrutura de arquivos

```
drive_sync/
├── drive-sync.service          # Arquivo de configuração do systemd
├── install-service.sh          # Script de instalação
├── uninstall-service.sh        # Script de desinstalação
├── .env                        # Configurações de ambiente
└── src/main.py                 # Aplicação principal
```

## Segurança

O serviço inclui configurações de segurança:
- `PrivateTmp=true`: Diretório /tmp privado
- `NoNewPrivileges=true`: Não permite escalação de privilégios
- `ProtectKernelTunables=true`: Protege parâmetros do kernel
- `ProtectControlGroups=true`: Protege cgroups
- `RestrictRealtime=true`: Restringe capacidades de tempo real
