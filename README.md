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

Monic is simple by design. The only piece of information Monic needs to run is the PostgreSQL connection string.
The connection string can be specified either through the environment variable `MONIC_POSTGRES_URI` or through the value `POSTGRES_URI` in the `~/.monic.toml` config file.

```
# example ~/.monic.toml
POSTGRES_URI="postgres://user:pwd@host:5432/monic"
```

TODO: configuration example

## Known Issues

Installing `psycopg2` fails on Apple Silicon inside of venv. If you stumble upon this issue, it's easy enough to fix by pointing clang linker to the openssl:

```
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
```

More here: https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl