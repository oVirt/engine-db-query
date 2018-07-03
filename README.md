# engine-db-query

About
=====
**engine-db-query** is a tool and python module to query engine database. 
The argument can be a pure SQL statement or SQL file.
It is posible also control the output format, like CSV, JSON or python like.

Building
========

**Generate an RPM**:

    $ autoreconf -ivf && ./configure && make rpm

Examples
========

**CSV output (Engine Host)**

    $ engine-db-query --statement "SELECT * FROM cluster" \
                      --json

**CSV output (Engine Host)**

    $ engine-db-query --statement "SELECT * FROM cluster" \
                      --csv

**JSON output (Remote Host)**

    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement "SELECT * FROM cluster" \
                      --json

**JSON output, adding name Clusters (Remote Host)**

    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement "SELECT * FROM cluster" \
                      --json \
                      --json-name "Clusters"

**CSV output (Remote Host)**

    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement "SELECT * FROM cluster" \
                      --csv

**Statement as SQL file (Remote Host)**

    $ engine-db-query --username engine \
                      --password superpass123 \
                      --fqdn MY_ENGINE_FQDN \
                      --statement my-file.sql


Python Module
=============
engine-db-query also provides a python module in case users prefer
to execute the calls from their own software.

**Example**:

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


FAQ
===

**Where is the credentials for PostgreSQL?**

  /etc/ovirt-engine/engine.conf.d/10-setup-database.conf
