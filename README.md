### Setup

the following environment variables must be set prior to any use
- **VLLM_BACKEND_URL**: http://localhost:8000/v1 # note no final /v1
- **VLLM_KEY**: api key to access the vllm server, default null
- **VLLM_DEFAULT_MODEL**: default model, for testing google/gemma-3-1b-it