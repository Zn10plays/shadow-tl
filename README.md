# Shadow translator 
The goal of this repo is to provide consistent translation capabalites for the shadow project

### Setup
#### Install

Following code to copy repo
```bash
git clone
git submodule update --recursive --remote
```

the project uses venvs (python or conda, whatever you like)
```bash
# tested with py ver = 3.11.7
conda create -p ./venv
conda activate ./venv

pip install -r requirements.txt
```


#### Environ
the following environment variables must be set prior to any use
- **VLLM_BACKEND_URL**: http://localhost:8000/v1 # note no final /v1
- **VLLM_KEY**: api key to access the vllm server, default null
- **VLLM_DEFAULT_MODEL**: default model, for testing google/gemma-3-1b-it

### Usage
This can be considered a template project. All work happens in the **main** file.
```bash
python main.py
``` 