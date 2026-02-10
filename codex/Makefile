ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
APP_DIR := $(ROOT_DIR)
PID_FILE := $(ROOT_DIR)/.codex-app.pid
LOG_FILE := $(ROOT_DIR)/.codex-app.log
PYTHON_BIN := $(ROOT_DIR)/.venv/bin/python

.PHONY: start stop restart status logs

start:
	@if [ -f "$(PID_FILE)" ] && kill -0 "$$(cat "$(PID_FILE)")" >/dev/null 2>&1; then \
		echo "SiteBooker is already running (pid=$$(cat "$(PID_FILE)"))"; \
		exit 0; \
	fi
	@if [ -f "$(PID_FILE)" ]; then rm -f "$(PID_FILE)"; fi
	@echo "Starting SiteBooker..."
	@if [ ! -x "$(PYTHON_BIN)" ]; then \
		echo "Python runtime not found: $(PYTHON_BIN)"; \
		echo "Run 'uv sync' first to create .venv"; \
		exit 1; \
	fi
	@cd "$(APP_DIR)" && (nohup env PYTHONPATH="$(ROOT_DIR)/src" "$(PYTHON_BIN)" -m sitebooker.main > "$(LOG_FILE)" 2>&1 & echo $$! > "$(PID_FILE)")
	@sleep 1
	@if kill -0 "$$(cat "$(PID_FILE)")" >/dev/null 2>&1; then \
		echo "Started (pid=$$(cat "$(PID_FILE)"))"; \
		echo "Log: $(LOG_FILE)"; \
	else \
		echo "Failed to start. Check $(LOG_FILE)"; \
		if [ -f "$(LOG_FILE)" ]; then tail -n 20 "$(LOG_FILE)"; fi; \
		rm -f "$(PID_FILE)"; \
		exit 1; \
	fi

stop:
	@if [ ! -f "$(PID_FILE)" ]; then \
		echo "SiteBooker is not running (no pid file)"; \
	else \
		PID="$$(cat "$(PID_FILE)")"; \
		if kill -0 "$$PID" >/dev/null 2>&1; then \
			echo "Stopping SiteBooker (pid=$$PID)..."; \
			kill "$$PID"; \
			sleep 1; \
			if kill -0 "$$PID" >/dev/null 2>&1; then \
				echo "Force killing (pid=$$PID)..."; \
				kill -9 "$$PID"; \
			fi; \
		else \
			echo "Process already stopped (stale pid=$$PID)"; \
		fi; \
		rm -f "$(PID_FILE)"; \
		echo "Stopped"; \
	fi

restart: stop start

status:
	@if [ -f "$(PID_FILE)" ] && kill -0 "$$(cat "$(PID_FILE)")" >/dev/null 2>&1; then \
		echo "SiteBooker is running (pid=$$(cat "$(PID_FILE)"))"; \
	else \
		echo "SiteBooker is not running"; \
	fi

logs:
	@if [ -f "$(LOG_FILE)" ]; then \
		tail -n 50 "$(LOG_FILE)"; \
	else \
		echo "No log file yet: $(LOG_FILE)"; \
	fi
