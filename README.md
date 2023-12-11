# Monico [![codecov](https://codecov.io/gh/Scorpil/monico/graph/badge.svg?token=2N7NG9INLT)](https://codecov.io/gh/Scorpil/monico)

<p align="center">
  <img alt="Monico Logo" src="https://github.com/Scorpil/monico/blob/main/monico-logo.svg" width="200"/>
</p>

## Introduction

Monico is a simple command-line utility for efficiently monitoring and analyzing the availability of websites.

Monico CLI is built with a focus on ease of use, flexibility, and reliability. It allows configuring website monitoring to collect essential data such as response times, status codes, and content checks, storing all information in a structured format for easy retrieval and analysis.

## Features

- **Easy Configuration**: Set up monitors for websites with a simple CLI.
- **Flexible Monitoring**: Define custom intervals and content checks for each monitor.
- **Data Insights**: Review monitoring data directly from CLI.
- **Secure and Reliable**: Built with security and reliability in mind, ensuring your monitoring is always up and running.

## Setup and Configuration

### Prerequisites
You need Python 3.11 to run `monico`. Additionally, make sure you have PostgreSQL libraries installed on your system. For Mac:
```
brew install libpq
```

For Ubuntu linux:
```
sudo apt-get install libpq-dev
```

### Installation

`monico` is distributed as a standard python package. Installing it in your system is as simple as:

```
git clone <repo-url> monic
cd monico/
pip install .
```

_Note_: Installing `psycopg2` fails on Apple Silicon inside of venv. If you stumble upon this issue, it's easy enough to fix by pointing clang linker to the openssl:

```
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
```

More here: https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl

### Configuration

Verify that `monico` is installed:
```
$ monico version
0.1.dev0
```

_Note:_ it's also possible to use monico through Python module syntax e.g:
```
$ python -m monico version
0.1.dev0
```

Monico is configured through config file `.monico.toml` in user home directory or using environment variables. Supported configuration options:

- `postgres_uri` (or environment variable `MONICO_POSTGRES_URI`): **required**, connection string to connect to database
- `log_level` (or environment variable `LOG_LEVEL`): optional, controls logging verbicity. Valid values are `DEBUG`, `INFO`, `WARNING`, `ERROR` and `CRITICAL`. Default is `WARNING`.

**Create the configuration file before continuing setup:**

Example `~/.monico.toml`
```
postgres_uri="postgres://user:pwd@host:5432/monico"
log_level="INFO"
```

When configuration is created, run `monico setup` to initialize the database. In future, to re-initialize the database use `monico setup --force` (careful, this will destroy all pre-existing data!).

## Simple Execution

Open two terminals. In the first one run
```
monico run
```

In the second one, create the monitor, for example:
```
monico create --id scorpil --endpoint "https://scorpil.com" --name "Scorpil's Blog" --interval 5 --body-regexp "The Long Road to [A-Za-z0-9/]+"
```

Now it's possible to watch the monitor execution results with `status` command:
```
monico status --id scorpil --live
```

To see the full list of available CLI commands run
```
$ monico --help
Usage: monico [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create       Creates a new monitor
  delete       Deletes a monitor.
  list         Lists configured monitors.
  run          Starts both manager and worker processes concurrently.
  run-manager  Starts the manager process.
  run-worker   Starts the worker process.
  setup        Initializes the database
  status       Displays status of a monitor
  version      Prints the version
```

You can also print help for every command:
```
$ monico create --help
Usage: monico create [OPTIONS]

  Creates a new monitor

Options:
  --id TEXT           ID of the monitor
  --name TEXT         Name of the monitor
  --endpoint TEXT     URL to monitor
  --interval INTEGER  Monitoring interval in seconds
  --body-regexp TEXT  Regular expression to match in the response body
  --help              Show this message and exit.
```

## Advanced execution

### Separate workers
`monico` consists of two major parts:
- **Manager** process is only responsible for scheduling tasks (probes). Manager is lightweight so performance-wise it is enough to run a single manager instance at a time. However, it's ok to run multiple manager instances concurrently for redundancy.
- **Worker** process performs HTTP requests and records results. It is possible to run multiple instances of worker for improved scalability and availability guarantees.

`monico run` runs both processes concurrently, but it's possible to run them seperately with `monico run-manager` and `monico run-worker` respectively. It's possible to run multiple instances of each process for scalability and reliability.

Complete app state is stored in database, so it's possible to e.g. run manager/workers processes on a server and control them from a local environment just by configuring `monico` to use the same database.

### Running in Docker

It's possible to run `monico` in Docker by building an image as follows:

```
docker build . -t monico
```

Then running monico as follows:

```
docker run -tie MONICO_POSTGRES_URI="<your-postgres-uri>" monico <arguments>
```

For example:
```
docker run -tie MONICO_POSTGRES_URI="postgres://user:pwd@host:5432/monico" monico status --id my-monitor --live
```

## Testing

To execute tests, you need to install development dependencies:
```
pip install '.[dev]'
```

Now you can run unit tests with
```
make test-unit
```

For integration tests you also need to export environment variable `MONICO_TEST_POSTGRES_URI`` (note the `_TEST_` part), e.g:
```
export MONICO_TEST_POSTGRES_URI="postgres://user:pwd@host:5432/monico"
```

To run integrations tests:
```
make test-integration
```

To run all tests and calculate code-coverage percentage:
```
make test
```

# Architecture

There are a few core concepts Monico uses:

- **Monitor** is a core Monico entity representing a specific website monitoring task. It encapsulates all the details and settings required to periodically check a website's availability and performance, such as endpoint url, check frequency, regex pattern for data lookup etc. When a monitor is active, Monico periodically sends requests (i.e. _probes_) to the specified URL at the defined frequency. It then captures key data from the response, such as response time and HTTP status code. If a regex pattern is provided, Monico also checks the response content against this pattern.
- **Task** is a scheduled item of work, i.e. check that is to be executed.
- **Probe** is an individual instance of a monitoring check performed by Monico. Each probe is an action initiated by a Monitor to assess the current state of a specified website.
- **Manager** is an internal scheduling component in Monico responsible for orchestrating the execution of _Probes_ according to their defined frequencies. It does this be creating tasks for workers to pick up.
- **Worker** is a component that is responsible for performing monitoring checks (_Probes_) and recording the execution results. Multiple worker singles are allowed to run concurrently to enable scaling.

![architecture diagram](https://github.com/Scorpil/monico/blob/main/monico-architecture.jpg)

# TODO

- Test coverage is at 88% and could be improved. The main culprit here is just time constraints.
- Tests around CLI commands require database connection right now. This can be eliminated by reorganising the code in a minor way and mocking a few places.
- Locking batch size should be configurable