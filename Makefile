.PHONY: dev-backend dev-frontend dev

dev-backend:
	cd backend && .venv/bin/uvicorn main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	make -j2 dev-backend dev-frontend
