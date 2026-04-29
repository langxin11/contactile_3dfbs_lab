#!/bin/bash
# Contactile 3DFBS Lab — 环境变量
# 用法: source config/env.sh

export CONTACTILE_PORT="${CONTACTILE_PORT:-/dev/ttyACM0}"
export CONTACTILE_BAUD="${CONTACTILE_BAUD:-9600}"
export CONTACTILE_SENSOR_COUNT="${CONTACTILE_SENSOR_COUNT:-1}"
export CONTACTILE_LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
