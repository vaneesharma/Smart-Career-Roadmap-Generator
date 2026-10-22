# mysqlclient (the usual MySQL driver for Django) needs a C compiler and the
# MySQL C connector to install, which frequently fails on Windows and on
# newer Python versions that don't have prebuilt wheels yet.
#
# PyMySQL is a pure-Python MySQL driver, so it installs with a normal
# "pip install" on any platform/Python version, with no compilation step.
# These two lines make Django use it as a drop-in replacement for
# mysqlclient - everything else (models, queries, settings) stays the same.
import pymysql
pymysql.install_as_MySQLdb()
