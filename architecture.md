# Terminology

There are a few core concepts Monic uses. Extranal user only needs to understand these:

- **Monitor** is a core Monic entity representing a specific website monitoring task. It encapsulates all the details and settings required to periodically check a website's availability and performance, such as endpoint url, check frequency, regex pattern for data lookup etc. When a monitor is active, Monic periodically sends requests (i.e. _probes_) to the specified URL at the defined frequency. It then captures key data from the response, such as response time and HTTP status code. If a regex pattern is provided, Monic also checks the response content against this pattern.
- **Probe** is an individual instance of a monitoring check performed by Monic. Each probe is an action initiated by a Monitor to assess the current state of a specified website.

There are a few more internal concepts, which are necessary to undersand for someone who works on Monic:

- **Manager** is an internal scheduling component in Monic responsible for orchestrating the execution of _Probes_ according to their defined frequencies. Important: it does not execute _Probes_, only schedules their execution.
- **Worker** is a component that is responsible for performing monitoring checks (_Probes_) and recording the execution results. Multiple worker singles are allowed to run concurrently to enable scaling.
- **Storage** is an abstraction layer between Monic and database or any other form of storage. Currently only PostgreSQL store is supported, but it's easy to extend the Store interface to use a different technology.
