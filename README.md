# CryptoAware

CryptoAware is set of APIs which are used in the WatchTower project to handle processing of user provided exports from
various cryptocurrency exchanges. The APIs are used to extract and process the data from the exports and store it in a 
Memgraph database. The data is then used to generate reports and conversational interfaces for the user.

## Installation
The project is written in Python and uses the following libraries:
- FastAPI
- Memgraph
- Pandas
- Langchain

Install virtualenv:
```bash
sudo apt install python3-venv
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required libraries:
```bash
pip install -r requirements.txt
```

Copy the `.env.example` file to `.env` and fill in the required values.


## Usage

### Without Docker & Docker Compose
To start the FastAPI server, run the following command:
```bash
fastapi run main.py
```

The server will start on `http://localhost:8000`.

### With Docker & Docker Compose
To start the FastAPI server using Docker, run the following command:
```bash
docker-compose up
```

The server will start on `http://localhost:8000`.

## Contributing
To contribute to the project, please follow the steps below:
1. Fork the repository
2. Create a new branch
3. Make your changes
4. Create a pull request
5. Wait for the pull request to be reviewed
6. Merge the pull request
7. Celebrate your contribution!
8. Repeat

## Development Tips

### Pre-commit
The project uses the `pre-commit` library to run various tools before committing your code. To install the pre-commit
hooks, run the following command:
```bash
pre-commit install
```

[//]: # ()
[//]: # (### Code Formatting)

[//]: # (The project uses the `black` code formatter to format the code. To format your code, run the following command:)

[//]: # (```bash)

[//]: # (black .)

[//]: # (```)

### Linting
The project uses the `flake8` linter to check the code for errors. To lint your code, run the following command:
```bash
flake8 .
```

[//]: # (- Use the `black` code formatter to format your code)

[//]: # (- Use the `isort` library to sort your imports)

[//]: # (- Use the `flake8` linter to check your code for errors)

[//]: # (- Use the `pytest` library to write tests for your code)

[//]: # (- Use the `pre-commit` library to run the above tools before committing your code)

[//]: # (- )