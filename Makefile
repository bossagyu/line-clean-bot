.PHONY: build deploy test clean logs local-api local-invoke install sync

# Load .env file if it exists
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# Install dependencies
install:
	uv sync

# Sync dependencies
sync:
	uv sync

# Build the SAM application
build:
	sam build

# Deploy to AWS (requires CHANNEL_ACCESS_TOKEN environment variable)
deploy: build
	@if [ -z "$(CHANNEL_ACCESS_TOKEN)" ]; then \
		echo "Error: CHANNEL_ACCESS_TOKEN is not set"; \
		echo "Usage: CHANNEL_ACCESS_TOKEN=your_token make deploy"; \
		exit 1; \
	fi
	sam deploy --parameter-overrides ChannelAccessToken=$(CHANNEL_ACCESS_TOKEN)

# Deploy without confirmation prompt
deploy-no-confirm: build
	@if [ -z "$(CHANNEL_ACCESS_TOKEN)" ]; then \
		echo "Error: CHANNEL_ACCESS_TOKEN is not set"; \
		exit 1; \
	fi
	sam deploy --parameter-overrides ChannelAccessToken=$(CHANNEL_ACCESS_TOKEN) --no-confirm-changeset

# Run tests
test:
	uv run pytest test/

# Run tests with coverage
test-cov:
	uv run pytest test/ --cov=lib --cov-report=term-missing

# Clean build artifacts
clean:
	rm -rf .aws-sam/build

# View CloudWatch logs for process_user_message
logs:
	sam logs -n process_user_message --region ap-northeast-1 --tail

# View CloudWatch logs for push-message-periodically
logs-push:
	sam logs -n push-message-periodically --region ap-northeast-1 --tail

# Start local API server
local-api: build
	sam local start-api --env-vars env.json

# Local invoke for testing
local-invoke: build
	sam local invoke ProcessUserMessageFunction --env-vars env.json -e events/line_message.json

# Validate template
validate:
	sam validate

# Show deployment status
status:
	aws cloudformation describe-stacks --stack-name line-clean-bot --region ap-northeast-1 --query "Stacks[0].StackStatus" --output text
