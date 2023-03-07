import os
import subprocess
import sys

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

if DB_HOST and DB_PORT and DB_NAME and DB_USER and DB_PASSWORD:
    cmd_execute = f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    # if using root with grant permission for new database:
    #     1. require env DB_ROOT_PASSWORD.
    #     2. uncomment under cmd_execute.
    #     3. replace {DB_USER} to root in cmd variable.
    # cmd_execute += f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'%';"
    # cmd_execute += "FLUSH PRIVILEGES;"

    cmd = f"mysql --host {DB_HOST} --port {DB_PORT} -u {DB_USER} -p{DB_PASSWORD} "
    cmd += f" -e \"{cmd_execute}\""
    sys.stdout.writelines('SQL CMD: ' + cmd + '\n')
    subprocess.run(cmd, shell=True)
else:
    raise ValueError('The initial must be require host, port, db name, user, password for connect mysql.')
