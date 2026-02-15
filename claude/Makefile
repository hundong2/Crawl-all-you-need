ROOT_DIR := $(shell pwd)
VENV_DIR := $(ROOT_DIR)/venv
PID_FILE := $(ROOT_DIR)/.app.pid
LOG_FILE := $(ROOT_DIR)/.app.log
PORT := 7860
APP_DIR := $(ROOT_DIR)

.PHONY: help setup start stop restart status logs clean

help: ## Show this help message
	@echo "Site-to-Document Generator"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment variables:"
	@echo "  OPENAI_API_KEY      OpenAI API key"
	@echo "  ANTHROPIC_API_KEY   Anthropic API key"
	@echo "  GEMINI_API_KEY      Google Gemini API key"

setup: ## Install dependencies and set up the project
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	@$(VENV_DIR)/bin/pip install -r $(APP_DIR)/requirements.txt --quiet
	@echo "Installing Playwright browser..."
	@$(VENV_DIR)/bin/playwright install chromium 2>&1 | tail -1
	@echo ""
	@echo "Setup complete! Run 'make start' to launch the app."

start: ## Start the app (http://localhost:7860)
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "App is already running (PID: $$(cat $(PID_FILE)))"; \
		echo "  http://localhost:$(PORT)"; \
	else \
		echo "Starting Site-to-Document Generator..."; \
		cd $(APP_DIR) && $(VENV_DIR)/bin/python app.py >> $(LOG_FILE) 2>&1 & \
		echo $$! > $(PID_FILE); \
		sleep 3; \
		if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
			echo "App started (PID: $$(cat $(PID_FILE)))"; \
			echo "  http://localhost:$(PORT)"; \
		else \
			echo "Failed to start. Check logs: make logs"; \
			rm -f $(PID_FILE); \
		fi; \
	fi

stop: ## Stop the running app
	@if [ -f $(PID_FILE) ]; then \
		PID=$$(cat $(PID_FILE)); \
		if kill -0 $$PID 2>/dev/null; then \
			kill $$PID; \
			echo "App stopped (PID: $$PID)"; \
		else \
			echo "App is not running (stale PID file)"; \
		fi; \
		rm -f $(PID_FILE); \
	else \
		echo "App is not running"; \
	fi

restart: stop start ## Restart the app

status: ## Show app status
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "App is running (PID: $$(cat $(PID_FILE)))"; \
		echo "  http://localhost:$(PORT)"; \
	else \
		echo "App is not running"; \
		rm -f $(PID_FILE) 2>/dev/null; \
	fi

logs: ## Show app logs
	@if [ -f $(LOG_FILE) ]; then \
		tail -50 $(LOG_FILE); \
	else \
		echo "No log file found"; \
	fi

clean: stop ## Stop app and remove generated files
	@rm -f $(PID_FILE) $(LOG_FILE)
	@echo "Cleaned up"
