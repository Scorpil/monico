# Monic

## Introduction

Monic is a command-line utility for efficiently monitoring and analyzing the availability and performance of websites.

Monic CLI is built with a focus on ease of use, flexibility, and reliability. It employs direct methods to probe websites and collect essential data such as response times, status codes, and content checks, storing all information in a structured format for easy retrieval and analysis.

## Features

- **Easy Configuration**: Set up monitors for websites with a simple CLI.
- **Flexible Monitoring**: Define custom intervals and content checks for each monitor.
- **Data Insights**: Review monitoring data directly from CLI.
- **Secure and Reliable**: Built with security and reliability in mind, ensuring your monitoring is always up and running.

## Setup and Configuration

Monic is simple by design. Monic is configured through config file `.monic.toml` in your home directory or using environment variables. Supported configuration options:

- `postgres_uri` (or env variable `MONIC_POSTGRES_URI`): **required**, connection string to connect to database
- `log_level` (or env variable `LOG_LEVEL`): optional, controls logging verbicity. Valid values are `DEBUG`, `INFO`, `WARNING`, `ERROR` and `CRITICAL`. Default is `WARNING`.

Example `~/.monic.toml`
```
postgres_uri="postgres://user:pwd@host:5432/monic"
log_level="INFO"
```

When configuration is set, run `monic setup` to initialize the database. To re-set the database in future use `monic setup -f` (this will destroy all your data!).

## Execution

`monic` consists of two major parts:
- **Manager** process is only responsible for scheduling tasks (probes). Manager is lightweight so performance-wise it is enough to run a single manager instance at a time. However, it's ok to run multiple manager instances concurrently for redundancy.
- **Worker** process performs HTTP requests and records results. It is possible to run multiple instances of worker for improved scalability and availability guarantees.

# TODO: describe controls; docker config

## Known Issues

Installing `psycopg2` fails on Apple Silicon inside of venv. If you stumble upon this issue, it's easy enough to fix by pointing clang linker to the openssl:

```
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
```

More here: https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl