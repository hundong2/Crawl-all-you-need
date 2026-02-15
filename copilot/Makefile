# Makefile for AI Web Crawler

VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
STREAMLIT = $(VENV_DIR)/bin/streamlit
APP_FILE = app.py
PID_FILE = .streamlit_pid
LOG_FILE = output.log

.PHONY: help setup start stop status clean logs

help:
	@echo "Available commands:"
	@echo "  make setup    - Create virtual environment and install dependencies"
	@echo "  make start    - Start the application in the background"
	@echo "  make stop     - Stop the running application"
	@echo "  make restart  - Restart the application"
	@echo "  make status   - Check if the application is running"
	@echo "  make logs     - Show the last 50 lines of the application logs"
	@echo "  make clean    - Remove temporary files"

setup:
	@echo "Setting up environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv $(VENV_DIR); \
	fi
	@echo "Installing dependencies..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements.txt
	@echo "Installing Playwright browsers..."
	@$(PYTHON) -m playwright install
	@echo "Setup complete."

start:
	@if [ -f $(PID_FILE) ]; then \
		PID=$$(cat $(PID_FILE)); \
		if ps -p $$PID > /dev/null; then \
			echo "Application is already running (PID: $$PID)."; \
		else \
			echo "PID file exists but process is dead. Cleaning up..."; \
			rm $(PID_FILE); \
			echo "Starting application..."; \
			nohup $(STREAMLIT) run $(APP_FILE) > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE); \
			echo "Application started (PID: $$(cat $(PID_FILE)))."; \
			echo "Logs are being written to $(LOG_FILE)."; \
		fi \
	else \
		echo "Starting application..."; \
		nohup $(STREAMLIT) run $(APP_FILE) > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE); \
		echo "Application started (PID: $$(cat $(PID_FILE)))."; \
		echo "Logs are being written to $(LOG_FILE)."; \
	fi

stop:
	@if [ -f $(PID_FILE) ]; then \
		PID=$$(cat $(PID_FILE)); \
		echo "Stopping application (PID: $$PID)..."; \
		kill $$PID 2>/dev/null || true; \
		rm $(PID_FILE); \
		echo "Application stopped."; \
	else \
		echo "Application is not running (PID file not found)."; \
		PIDS=$$(pgrep -f "$(STREAMLIT) run $(APP_FILE)" || true); \
		if [ -n "$$PIDS" ]; then \
			echo "Found running processes without PID file. Killing them..."; \
			echo "$$PIDS" | xargs kill; \
			echo "Stopped."; \
		fi \
	fi

restart: stop start

status:
	@if [ -f $(PID_FILE) ]; then \
		PID=$$(cat $(PID_FILE)); \
		if ps -p $$PID > /dev/null; then \
			echo "Application is running (PID: $$PID)."; \
		else \
			echo "Application is NOT running (stale PID file found)."; \
		fi \
	else \
		echo "Application is NOT running."; \
	fi

logs:
	@if [ -f $(LOG_FILE) ]; then \
		tail -n 50 $(LOG_FILE); \
	else \
		echo "No log file found."; \
	fi

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -f $(PID_FILE)
	rm -f $(LOG_FILE)
	@echo "Cleaned up temporary files."
