.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: lint
lint: ## Run linters in format mode
	black ./bot/src ./bot/tests ./scrapper/src ./scrapper/tests
	mypy ./scrapper/src ./scrapper/tests
	ruff check ./bot/src ./bot/tests ./scrapper/src ./scrapper/tests
	pytest ./bot/tests ./scrapper/tests --dead-fixtures --dup-fixtures 

.PHONY: test
test: ## Runs pytest with coverage
	pytest ./tests 
