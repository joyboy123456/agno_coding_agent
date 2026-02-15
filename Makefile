# Web Builder Agent - 开发命令集
# 使用方法: make dev (一键启动前后端开发环境)

.PHONY: dev dev-backend dev-frontend stop install install-backend install-frontend clean

# ============================================================
# 一键启动（前后端同时运行，后台进程 + 日志合并输出）
# ============================================================

dev:
	@echo "=========================================="
	@echo "  Web Builder Agent - 开发模式"
	@echo "  后端: http://localhost:7777 (自动热重载)"
	@echo "  前端: http://localhost:3000 (自动热更新)"
	@echo "  按 Ctrl+C 停止所有服务"
	@echo "=========================================="
	@trap 'kill 0' EXIT; \
	cd backend && python agentos.py & \
	cd agent-ui && pnpm dev & \
	wait

# 单独启动后端
dev-backend:
	cd backend && python agentos.py

# 单独启动前端
dev-frontend:
	cd agent-ui && pnpm dev

# ============================================================
# 依赖安装
# ============================================================

install: install-backend install-frontend

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd agent-ui && pnpm install

# ============================================================
# CLI 模式（完整 Workflow: Developer + QA）
# ============================================================

# 交互模式
cli:
	cd backend && python main.py

# 指定 skill 运行，用法: make run SKILL=restaurant-menu
run:
	cd backend && python main.py $(SKILL)

# ============================================================
# 清理
# ============================================================

stop:
	@echo "正在停止所有服务..."
	@-pkill -f "agentos.py" 2>/dev/null || true
	@-pkill -f "next dev" 2>/dev/null || true
	@echo "已停止"

clean:
	rm -rf backend/tmp/*.db
	rm -rf backend/workspace/*/
	@echo "已清理临时文件和生成产物"
