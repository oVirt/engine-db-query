# engine-db-query

[![Copr build status](https://copr.fedorainfracloud.org/coprs/ovirt/ovirt-master-snapshot/package/engine-db-query/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/ovirt/ovirt-master-snapshot/package/engine-db-query/)

Welcome to the Engine Database Query tool source repository.

This repository is hosted on [gerrit.ovirt.org:engine-db-query](https://gerrit.ovirt.org/#/admin/projects/engine-db-query)
and a **backup** of it is hosted on [GitHub:engine-db-query](https://github.com/oVirt/engine-db-query)


## About

`engine-db-query` is a tool and python module to query engine database.
The argument can be a pure SQL statement or SQL file.
It is possible also to control the output format, like CSV, JSON or python like.

## How to contribute

### Submitting patches

Patches are welcome!

Please submit patches to [gerrit.ovirt.org:engine-db-query](https://gerrit.ovirt.org/#/admin/projects/engine-db-query).
If you are not familiar with the review process for Gerrit patches you can read about [Working with oVirt Gerrit](https://ovirt.org/develop/dev-process/working-with-gerrit.html)
on the [oVirt](https://ovirt.org/) website.

**NOTE**: We might not notice pull requests that you create on Github, because we only use Github for backups.


### Found a bug or documentation issue?
To submit a bug or suggest an enhancement for Engine Database Query tool please use
[oVirt Bugzilla for engine-db-query component](https://bugzilla.redhat.com/enter_bug.cgi?product=Red%20Hat%20Enterprise%20Virtualization%20Manager&component=ovirt-engine-db-query).

If you find a documentation issue on the oVirt website please navigate and click "Report an issue on GitHub" in the page footer.


## Still need help?
If you have any other questions, please join [oVirt Users forum / mailing list](https://lists.ovirt.org/admin/lists/users.ovirt.org/) and ask there.



## Building

**Generate an RPM**:

```bash
    $ autoreconf -ivf && ./configure && make rpm
```

## Examples


**CSV output (Engine Host)**

```bash
    $ engine-db-query --statement "SELECT * FROM cluster" \
                      --json
```

**CSV output (Engine Host)**

```bash
    $ engine-db-query --statement "SELECT * FROM cluster" \
                      --csv
```

**JSON output (Remote Host)**

```bash
    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement "SELECT * FROM cluster" \
                      --json
```

**JSON output, adding name Clusters (Remote Host)**

```bash
    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement "SELECT * FROM cluster" \
                      --json \
                      --json-name "Clusters"
```

**CSV output (Remote Host)**

```bash
    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement "SELECT * FROM cluster" \
                      --csv
```

**Statement as SQL file (Remote Host)**

```bash
    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement my-file.sql
```

## Python Module


`engine-db-query` also provides a python module in case users prefer
to execute the calls from their own software.

**Example**:

```python
    from engine_db_query import Database

    with Database(
            host="192.168.122.80",
            user="engine",
            password="superpass",
            database="engine",
            port="5432"
    ) as d:
        # Execute a stored procedure
        d.execute("stored_procedures/sp_cluster_query_minimum_3_6_compat_version.sql")

        # Execute a SQL query and return a array of dict
        r = d.execute("SELECT * FROM cluster")
        for i in r:
            print(i["name"])

        # Execute and generate the output as CSV
        print(d.execute("SELECT * FROM cluster", output_type="csv"))

        # Execute and generate the output as JSON
        print(d.execute("SELECT * FROM cluster", output_type="json")

        # Execute and add a name into JSON
        print(d.execute("SELECT * FROM cluster", output_type="json", name="Hosts"))
```

## FAQ

**Where are the credentials for PostgreSQL?**

  /etc/ovirt-engine/engine.conf.d/10-setup-database.conf
