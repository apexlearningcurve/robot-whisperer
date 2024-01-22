# Control robot with your words

## System requirements:

Project is linux based if you want to run on windows you will need [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)

## Setup

Install Poetry:

```bash
sudo apt install pipx
pipx install poetry==1.4.0
poetry config virtualenvs.in-project true
```

Install the project dependencies

```bash
poetry install
```

## To do list:

- [ ] Define calling functions
- [ ] Find LLM
- [ ] Create synthetic dataset
- [ ] Fine-tune the model
- [ ] Test function calling
