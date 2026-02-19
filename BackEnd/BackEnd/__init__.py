import pymysql

# 1. Engañar a Django para que use pymysql como si fuera mysqlclient
pymysql.install_as_MySQLdb()

# 2. Forzar a que la versión reportada sea compatible con lo que pide Django
pymysql.version_info = (2, 2, 1, "final", 0)