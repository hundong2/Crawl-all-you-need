.PHONY: help setup start stop clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup    - Install dependencies (Python & Node.js)"
	@echo "  make start    - Start Backend (5556) and Frontend (5555)"
	@echo "  make stop     - Stop all running processes"
	@echo "  make clean    - Remove virtual environment and node_modules"

setup:
	@echo "Setting up Python environment..."
	python3 -m venv venv
	@echo "Installing backend dependencies..."
	. venv/bin/activate && pip install -r backend/requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

start:
	@echo "Starting Backend on port 5556..."
	@. venv/bin/activate && nohup uvicorn backend.main:app --reload --port 5556 > backend.log 2>&1 & echo $$! > backend.pid
	@echo "Starting Frontend on port 5555..."
	@cd frontend && nohup npm run dev -- --port 5555 > ../frontend.log 2>&1 & echo $$! > ../frontend.pid
	@echo "Application started!"
	@echo "Frontend: http://localhost:5555"
	@echo "Backend: http://localhost:5556"

stop:
	@echo "Stopping processes..."
	@-kill `cat backend.pid` 2>/dev/null && rm backend.pid || echo "Backend not running or PID file missing"
	@-kill `cat frontend.pid` 2>/dev/null && rm frontend.pid || echo "Frontend not running or PID file missing"
	@pkill -f "uvicorn backend.main:app" || true
	@pkill -f "vite" || true
	@echo "Stopped."

clean:
	@echo "Cleaning up..."
	@rm -rf venv
	@rm -rf frontend/node_modules
	@rm -f backend.log frontend.log backend.pid frontend.pid
	@echo "Cleaned."
