#!/usr/bin/python
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import psycopg2
import json
import sys
import os
import logging
import time
import hashlib


from datetime import datetime
from distutils.util import strtobool
from .config import ENGINE_DB_CONF_FILE


class Database():

    def __init__(
        self,
        host,
        port,
        user,
        password,
        database,
        logfile=None
    ):
        """
        Params:

        host     - PostgreSQL Host
        port     - PostgreSQL Port
        user     - PostgreSQL User
        password - PostgreSQL Password
        database - PostgreSQL Database
        logfile  - Log file for the database transactions
        """

        self.connection = None
        self.cursor = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.path_sql = None
        self.logfile = logfile
        self.logger = self._configure_logging()

        self.logger.debug("====== start ========")

        self.logger.debug("\n\tCONNECTION PARAMS:\n"
                          "\t\thost: {host},\n"
                          "\t\tport: {port},\n"
                          "\t\tuser: {user},\n"
                          "\t\tpass: ******,\n"
                          "\t\tdatabase: {database},"
                          "\n".format(
                              host=self.host,
                              port=self.port,
                              user=self.user,
                              database=self.database
                          ))

    def _configure_logging(self):
        """
        The logging settings
        """

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        # logging: File
        if self.logfile is not None:
            file_handler = logging.FileHandler(self.logfile)
            file_handler.setLevel(logging.DEBUG)
            file_fmt = logging.Formatter("%(asctime)s %(message)s",
                                         "%m/%d/%Y %I:%M:%S %p")

        # logging: Stdout
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setLevel(logging.INFO)

        stdout_fmt = logging.Formatter("%(message)s",
                                       "%m/%d/%Y %I:%M:%S %p")

        stdout_handler.setFormatter(stdout_fmt)
        logger.addHandler(stdout_handler)

        # logging: File
        if self.logfile is not None:
            file_handler.setFormatter(file_fmt)
            logger.addHandler(file_handler)

        logging.captureWarnings(True)

        return logger

    def connect(
        self
    ):
        """
        Connect to PostgreSQL server using args from __init__()
        and set self.connection for general use
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                dbname=self.database,
                user=self.user,
                port=self.port,
                password=self.password
            )
        except Exception:
            self.logger.exception('connection failed')
            return

        if hasattr(self.connection, 'autocommit'):
            self.connection.autocommit = True
        else:
            self.connection.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
            )

    def execute(
        self,
        statement,
        output_type=None,
        id_json=None,
        name=None,
        description=None,
        desc_type=None,
        bugzilla=None,
        knowledge_base=None
    ):
        """
        Execute SQL query or SQL file

        Params:
            statement   - SQL query or file

            output_type - json will return JSON
                          csv will return CSV
                          None will return array of dict

            JSON Params:
            ===============
            id_json        - id for the json msg, see query_return_json()
            name           - name for json, see query_return_json()
            description    - A description to be included in the json return
            desc_type      - type of description: Error, Debug, Warning or Info
            knowledge_base - URL to a knowledge base article
            bugzilla       - Bugzilla URL

        Returns:
            self.query_return_array_dict()
                or
            self.query_return_csv()
                or
            self.query_return_json()
        """
        if os.path.exists(statement):
            self.path_sql = statement
            self.logger.debug("file: %s" % statement)
            with open(statement, 'r', encoding="utf-8") as f:
                statement = f.read().strip()

        cursor = self.connection.cursor()

        self.logger.debug("\n\tOUTPUT TYPE: %s\n" % output_type)
        if output_type is None:
            return self.query_return_array_dict(
                cursor,
                statement
            )

        elif "csv" in output_type.lower():
            return self.query_return_csv(
                cursor,
                statement
            )

        elif "json" in output_type.lower():
            if desc_type is not None:
                if (desc_type.lower() != "info" and
                        desc_type.lower() != "debug" and
                        desc_type.lower() != "warning" and
                        desc_type.lower() != "error"):
                    raise RuntimeError("Message Type should be: Info, "
                                       "Debug, Warning or Error")

            return self.query_return_json(
                cursor=cursor,
                statement=statement,
                id_json=id_json,
                name=name,
                description=description,
                desc_type=desc_type,
                bugzilla=bugzilla,
                knowledge_base=knowledge_base
            )

    def query_return_array_dict(
        self,
        cursor,
        statement
    ):
        """
        Params:
            cursor    - cursor pointer
            statement - SQL query or file

        Returns:
            array dict object
        """
        ret = []

        self.logger.debug("\n\tSQL QUERY ARRAY DICT:\n %s" % statement)
        try:
            cursor.execute(
                statement
            )
        except psycopg2.ProgrammingError:
            self.logger.exception(
                "A syntax error occurred, command was: %s",
                statement,
            )
        except Exception:
            self.logger.exception(
                "An error occurred when executing SQL, command was: %s",
                statement
            )

        if cursor.description is not None:
            cols = [d[0] for d in cursor.description]
            while True:
                entry = cursor.fetchone()
                if entry is None:
                    break
                ret.append(dict(list(zip(cols, entry))))
        return ret

    def query_return_csv(
        self,
        cursor,
        statement,
    ):
        """
        Params:
            cursor      - cursor pointer
            statement   - SQL query or file

        Returns:
            CSV format
        """
        query = (
            """
            COPY (
                {0}
            ) TO STDOUT WITH CSV DELIMITER E'\|' HEADER
            """.format(
                statement
            )  # noqa: W605
        )

        self.logger.debug("\n\tSQL QUERY FOR CSV:\n %s" % query)
        try:
            cursor.copy_expert(
                query,
                sys.stdout
            )
        except psycopg2.ProgrammingError:
            self.logger.exception("%s", query)
        except Exception:
            self.logger.exception(
                "An error occurred when executing SQL, command was: %s",
                statement
            )

    def query_return_json(
        self,
        cursor,
        statement,
        id_json=None,
        description=None,
        desc_type=None,
        name=None,
        bugzilla=None,
        knowledge_base=None
    ):
        """
            cursor         - cursor pointer
            id_json        - ID to be included in the json message
            statement      - SQL query or file
            description    - A description to be included in the json return
            desc_type      - type of description: Error, Warning or Info
            name           - Add a name to json
            knowledge_base - URL to a knowledge base article
            bugzilla       - URL to bugzilla

            When adding a name to json it will be in such format:

            Example:
            {
                "name": "check_windows_with_incorrect_timezone",
                ....
            }
        """

        query = (
            """
            SELECT
                row_to_json(t)
            FROM
               ({0}) t
            """.format(statement)
        )

        self.logger.debug("\n\tSQL QUERY FOR JSON:\n %s" % query)

        start_time = time.time()
        try:
            cursor.execute(
                query
            )
        except psycopg2.ProgrammingError:
            self.logger.exception("%s", query)
        except Exception:
            self.logger.exception(
                "An error occurred when executing SQL, command was: %s",
                statement
            )
        time_exec = time.time() - start_time

        ret = cursor.fetchall()

        if not ret:
            return

        file_name = ''
        if self.path_sql:
            file_name = self.path_sql.split("/")[-1]

        file_name = file_name.encode("utf-8")
        json_output = (
            '{start_json} '
            '"id_host": "{id_host}"'
            ',"when": "{date}"'
            ',"time": "{time_exec}"'
            ', "name": "{name}"'
            ', "description": "{description}"'
            ', "type": "{desc_type}"'
            ', "kb": "{kb_url}"'
            ', "bugzilla": "{bug_url}"'
            ', "file": "{f}", "path": "{p}"'
            ', "id": "{s}", "hash": "{m}"'
            ', "result": {result}'
            '{end_json}'.format(
                start_json="{",
                id_host=id_json,
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                name=name,
                description=description,
                time_exec=time_exec,
                desc_type=desc_type,
                kb_url=knowledge_base,
                bug_url=bugzilla,
                result=json.dumps(ret),
                f=file_name,
                p=self.path_sql,
                s=hashlib.sha256(file_name).hexdigest(),
                m=hashlib.md5(file_name).hexdigest(),
                end_json="}")
        )

        return json_output.strip()

    def disconnect(self):
        """
        Disconnect Database Method
        """
        if self.connection:
            self.connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("====== end ========")
        self.disconnect()


def load_engine_credentials():

    engine_conf = {
        'host': None,
        'port': None,
        'user': None,
        'password': None,
        'database': None,
        'secured': None,
        'secured_validation': None,
        'driver': None,
        'url': None,
    }

    with open(ENGINE_DB_CONF_FILE) as f:
        for line in f:
            conf_key, conf_value = line.split('=', 1)
            conf_value = conf_value.strip('\n')

            # By default the 10-setup-database.conf includes " "
            # between the values of keys, we should remove it
            conf_value = conf_value[1:-1]

            if 'ENGINE_DB_HOST' == conf_key:
                engine_conf['host'] = conf_value

            elif 'ENGINE_DB_PORT' == conf_key:
                engine_conf['port'] = int(conf_value)

            elif 'ENGINE_DB_USER' == conf_key:
                engine_conf['user'] = conf_value

            elif 'ENGINE_DB_PASSWORD' == conf_key:
                engine_conf['password'] = conf_value

            elif 'ENGINE_DB_DATABASE' == conf_key:
                engine_conf['database'] = conf_value

            elif 'ENGINE_DB_SECURED' == conf_key:
                engine_conf['secured'] = bool(
                    strtobool(conf_value)
                )

            elif 'ENGINE_DB_SECURED_VALIDATION' == conf_key:
                engine_conf['secured_validation'] = bool(
                    strtobool(conf_value)
                )

            elif 'ENGINE_DB_DRIVER' == conf_key:
                engine_conf['driver'] = conf_value

            elif 'ENGINE_DB_URL' == conf_key:
                engine_conf['url'] = conf_value

    return engine_conf


# vim: expandtab tabstop=4 shiftwidth=4
