#: set shell to bash to make shell builtin behaviour consistent
SHELL := /usr/bin/env bash

#: install dependencies; set dev_only for only development dependencies or use the install_dev target
install:
ifeq ($(dev_only),) # dev_only not set
	poetry install
else
	poetry install --only dev
endif

#: install only development dependencies
install_dev:
	poetry install --only dev

#: build a release package
build: install
	poetry build --no-cache -v

#: build and publish a package
publish: install
	poetry publish -u '__token__' -p ${PYPI_TOKEN}

#: cleans up smoke test output
clean-smoke-tests:
	rm -rf ./smoke-tests/collector/data.json
	rm -rf ./smoke-tests/collector/data-results/*.json
	rm -rf ./smoke-tests/report.*

#: clean all the caches and any dist
clean-cache:
	rm -rf dist/*
	rm -rf tgt/opentelemetry/__pycache__/
	rm -rf src/tgt/opentelemetry/__pycache__/
	rm -rf examples/hello-world-flask/__pycache__
	rm -rf examples/hello-world-flask/dist/*
	rm -rf examples/hello-world/__pycache__
	rm -rf examples/hello-world/dist/*

#: clean smoke test output, caches, builds
clean: clean-smoke-tests clean-cache

#: run the unit tests with a clean environment, create coverage report html
test: build
	mkdir -p test-results
	unset ${OUR_CONFIG_ENV_VARS} && poetry run coverage run -m pytest tests --junitxml=test-results/junit.xml
	poetry run coverage html

#: nitpick lint
lint: install_dev
	poetry run pylint src

#: nitpick style
style: install_dev
	poetry run pycodestyle src

#: clear data from smoke tests
smoke-tests/collector/data.json:
	@echo ""
	@echo "+++ Zhuzhing smoke test's Collector data.json"
	@touch $@ && chmod o+w $@

#: smoke test the hello-world app using http/protobuf protocol and configure_opentelemetry()
smoke-sdk-http: smoke-tests/collector/data.json
	@echo ""
	@echo "+++ Running HTTP smoke tests on configure_opentelemetry()"
	@echo ""
	cd smoke-tests && bats ./smoke-sdk-http.bats --report-formatter junit --output ./

#: smoke test the flask app using http protocol and opentelemetry_instrument
smoke-sdk-http-flask: smoke-tests/collector/data.json
	@echo ""
	@echo "+++ Running HTTP Flask smoke tests on opentelemetry_instrument"
	@echo ""
	cd smoke-tests && bats ./smoke-sdk-http-flask.bats --report-formatter junit --output ./

#: smoke test both example apps using grpc and then http/protobuf protocols
smoke-sdk: smoke-sdk-http smoke-sdk-http-flask

#: placeholder for smoke tests, simply build the app
smoke:
	@echo ""
	@echo "+++ Temporary Placeholder."
	@echo ""
	cd smoke-tests && docker-compose up --build app-sdk-grpc

#: placeholder for smoke tests, tear down the app
unsmoke:
	@echo ""
	@echo "+++ Spinning down the smokers."
	@echo ""
	cd smoke-tests && docker-compose down --volumes

EXAMPLE_SERVICE_NAME ?= otel-python-example
run_example: export OTEL_SERVICE_NAME := $(EXAMPLE_SERVICE_NAME)
#: fire up an instrumented Python web service; set HONEYCOMB_API_KEY to send data for real
run_example:
	cd examples/hello-world-flask && \
	poetry install && \
	poetry run opentelemetry-instrument flask run

JOB ?= test-3.10

.PHONY: install build test lint run_example forbidden_in_real_ci

### Utilities

# ^(a_|b_|c_) :: name starts with any of 'a_', 'b_', or 'c_'
# [^=]        :: [^ ] is inverted set, so any character that isn't '='
# +           :: + is 1-or-more of previous thing
#
# So the match the prefixes, then chars up-to-but-excluding the first '='.
#   example: OTEL_VAR=HEY -> OTEL_VAR
#
# egrep to get the extended regex syntax support.
# --only-matching to output only what matches, not the whole line.
OUR_CONFIG_ENV_VARS := $(shell env | egrep --only-matching "^(HONEYCOMB_|OTEL_)[^=]+")
