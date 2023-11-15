# Monic

## Introduction

Monic is a simple command-line utility for efficiently monitoring and analyzing the availability of websites.

Monic CLI is built with a focus on ease of use, flexibility, and reliability. It allows configuring website monitoring to collect essential data such as response times, status codes, and content checks, storing all information in a structured format for easy retrieval and analysis.

## Features

- **Easy Configuration**: Set up monitors for websites with a simple CLI.
- **Flexible Monitoring**: Define custom intervals and content checks for each monitor.
- **Data Insights**: Review monitoring data directly from CLI.
- **Secure and Reliable**: Built with security and reliability in mind, ensuring your monitoring is always up and running.

## Setup and Configuration

`monic` is distributed as a standard python package. Installing it in your system is as simple as:

```
git clone <repo-url> monic
cd monic/
pip install .
```

Verify that `monic` is installed:
```
$ monic version
0.1.0-dev
```

Monic is configured through config file `.monic.toml` in your home directory or using environment variables. Supported configuration options:

- `postgres_uri` (or env variable `MONIC_POSTGRES_URI`): **required**, connection string to connect to database
- `log_level` (or env variable `LOG_LEVEL`): optional, controls logging verbicity. Valid values are `DEBUG`, `INFO`, `WARNING`, `ERROR` and `CRITICAL`. Default is `WARNING`.

**Create the configuration file before continuing setup:**

Example `~/.monic.toml`
```
postgres_uri="postgres://user:pwd@host:5432/monic"
log_level="INFO"
```

When configuration is created, run `monic setup` to initialize the database. In future, to re-initialize the database use `monic setup --force` (this will destroy all your data!).

## Simple Execution

Open two terminals. In the first one run
```
monic run
```

In the second one, create the monitor, for example:
```
monic create --id scorpil --endpoint "https://scorpil.com" --name "Scorpil's Blog" --interval 5 --body-regexp "The Long Road to [A-Za-z0-9/]+"
```

Now it's possible to watch the monitor execution results with `status` command:
```
monic status --id scorpil --live
```

## Advanced execution

### Separate workers
`monic` consists of two major parts:
- **Manager** process is only responsible for scheduling tasks (probes). Manager is lightweight so performance-wise it is enough to run a single manager instance at a time. However, it's ok to run multiple manager instances concurrently for redundancy.
- **Worker** process performs HTTP requests and records results. It is possible to run multiple instances of worker for improved scalability and availability guarantees.

`monic run` runs both processes concurrently, but it's possible to run them seperately with `monic run-manager` and `monic run-worker respectively`.

### Running in Docker

It's possible to run `monic` in Docker by building an image as follows:

```
docker build . -t monic
```

Then running monic as follows:

```
docker run -tie MONIC_POSTGRES_URI="<your-postgres-uri>" monic <arguments>
```

For example:
```
docker run -tie MONIC_POSTGRES_URI="postgres://user:pwd@host:5432/monic" monic status --id my-monitor --live
```

## Testing

To execute tests, you need to install development dependencies:
```
pip install -r requirements-dev.txt
```

Now you can run unit tests with
```
make test-unit
```

For integration tests you also need to export environment variable MONIC_TEST_POSTGRES_URI, e.g:
```
export MONIC_TEST_POSTGRES_URI="postgres://user:pwd@host:5432/monic"
```

To run integrations tests:
```
make test-integration
```

To run all tests and calculate code-coverage percentage:
```
make test
```

## Known Issues

Installing `psycopg2` fails on Apple Silicon inside of venv. If you stumble upon this issue, it's easy enough to fix by pointing clang linker to the openssl:

```
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
```

More here: https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl