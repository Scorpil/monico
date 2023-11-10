# Terminology

These are core terms Monic uses:

- **Monitor** is a core Monic entity representing a specific website monitoring task. It encapsulates all the details and settings required to periodically check a website's availability and performance, such as endpoint url, check frequency, regex pattern for data lookup etc. When a monitor is active, Monic periodically sends requests (i.e. _probes_) to the specified URL at the defined frequency. It then captures key data from the response, such as response time and HTTP status code. If a regex pattern is provided, Monic also checks the response content against this pattern.
- **Probe** is an individual instance of a monitoring check performed by Monic. Each probe is an action initiated by a Monitor to assess the current state of a specified website.
- **Scheduler** is an internal component in Monic responsible for orchestrating the execution of _Probes_ according to their defined frequencies. It serves as an automated timekeeper and task manager, ensuring that each Monitor's checks are performed accurately and timely.
- **Storage** is an abstraction layer between Monic and database or any other form of storage. Currently only PostgreSQL store is supported, but it's easy to extend the Store interface to use a different technology.
