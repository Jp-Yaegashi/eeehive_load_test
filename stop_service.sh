#!/bin/sh

stop_service() {
    SERVICE=$1
    echo "$SERVICE を停止します"
    sudo systemctl stop "$SERVICE"

    if sudo systemctl is-active --quiet "$SERVICE"; then
        echo "❌ $SERVICE はまだ active です（停止失敗）"
    else
        echo "✅ $SERVICE を停止しました"
    fi
    echo "--------------------------------"
}

stop_service mysql.service
stop_service mouse_alive.service
stop_service eeehive_alive.service
stop_service event_001.service
stop_service event_002.service
stop_service antenna.service
stop_service index.service
stop_service monitor.service
stop_service screen.service
stop_service update.service
stop_service grafana-server.service
