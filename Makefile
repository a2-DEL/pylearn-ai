# PyLearn AI 部署快捷命令
# 首次部署：cp .env.example .env && make up

.PHONY: help up up-pg up-monitor down logs ps build

help:
	@echo "PyLearn AI 部署命令："
	@echo "  make up          启动 backend+frontend+redis（默认）"
	@echo "  make up-pg       额外启用 PostgreSQL"
	@echo "  make up-monitor  额外启用 Prometheus+Grafana 监控栈"
	@echo "  make down        停止并移除容器"
	@echo "  make logs        查看日志"
	@echo "  make ps          查看运行状态"
	@echo "  make build       重新构建镜像"

up:
	docker compose up -d

up-pg:
	docker compose --profile pg up -d

up-monitor:
	docker compose --profile pg --profile monitor up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

build:
	docker compose build
