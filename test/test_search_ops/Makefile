# Makefile para executar testes do search_ops

.PHONY: help install test test-cov test-parallel test-unit test-integration clean lint format

# Variáveis
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Mostra esta mensagem de ajuda
	@echo "$(BLUE)Comandos disponíveis para testes do window:$(NC)\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências de teste
	@echo "$(YELLOW)Instalando dependências...$(NC)"
	$(PIP) install -r test-requirements.txt

test: ## Executa todos os testes
	@echo "$(BLUE)Executando todos os testes...$(NC)"
	$(PYTEST) test_search_ops.py -v

test-cov: ## Executa testes com cobertura de código
	@echo "$(BLUE)Executando testes com cobertura...$(NC)"
	$(PYTEST) test_search_ops.py --cov=window --cov-report=html --cov-report=term-missing -v
	@echo "$(GREEN)Relatório de cobertura disponível em htmlcov/index.html$(NC)"

test-parallel: ## Executa testes em paralelo
	@echo "$(BLUE)Executando testes em paralelo...$(NC)"
	$(PYTEST) test_search_ops.py -n auto -v

test-unit: ## Executa apenas testes unitários
	@echo "$(BLUE)Executando testes unitários...$(NC)"
	$(PYTEST) test_search_ops.py -m "not integration" -v

test-integration: ## Executa apenas testes de integração
	@echo "$(BLUE)Executando testes de integração...$(NC)"
	$(PYTEST) test_search_ops.py -m integration -v

test-fast: ## Executa testes rápidos (exclui marcados como slow)
	@echo "$(BLUE)Executando testes rápidos...$(NC)"
	$(PYTEST) test_search_ops.py -m "not slow" -v

test-watch: ## Executa testes em modo watch (reexecuta quando arquivos mudam)
	@echo "$(BLUE)Modo watch ativado - testes serão reexecutados quando arquivos mudarem$(NC)"
	$(PYTEST) test_search_ops.py --looponfail

test-specific: ## Executa um teste específico (uso: make test-specific TEST=nome_do_teste)
	@echo "$(BLUE)Executando teste específico: $(TEST)$(NC)"
	$(PYTEST) test_search_ops.py::$(TEST) -v

lint: ## Executa linting do código
	@echo "$(YELLOW)Executando linting...$(NC)"
	flake8 search_ops.py test_search_ops.py --max-line-length=100 --ignore=E203,W503

format: ## Formata código com black
	@echo "$(YELLOW)Formatando código...$(NC)"
	black search_ops.py test_search_ops.py --line-length=100

clean: ## Remove arquivos temporários e cache
	@echo "$(YELLOW)Limpando arquivos temporários...$(NC)"
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf __pycache__/
	rm -rf *.pyc
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

test-ci: install lint test-cov ## Pipeline completa para CI/CD
	@echo "$(GREEN)Pipeline de CI/CD concluído com sucesso!$(NC)"

test-local: clean install test-cov ## Setup completo para desenvolvimento local
	@echo "$(GREEN)Setup local concluído!$(NC)"

test-docker: ## Executa testes em container Docker
	@echo "$(BLUE)Executando testes em Docker...$(NC)"
	docker run --rm -v $(PWD):/app -w /app python:3.9 bash -c "pip install -r test-requirements.txt && make test-cov"

test-debug: ## Executa testes em modo debug
	@echo "$(BLUE)Executando testes em modo debug...$(NC)"
	$(PYTEST) test_search_ops.py --pdb -v

test-profile: ## Executa testes com window de performance
	@echo "$(BLUE)Executando testes com window...$(NC)"
	$(PYTEST) test_search_ops.py --profile -v

test-report: ## Gera relatório detalhado dos testes
	@echo "$(BLUE)Gerando relatório de testes...$(NC)"
	$(PYTEST) test_search_ops.py --html=report.html --self-contained-html -v
	@echo "$(GREEN)Relatório disponível em report.html$(NC)"

quality-check: lint format test-cov ## Executa todas as verificações de qualidade
	@echo "$(GREEN)Verificações de qualidade concluídas!$(NC)"
