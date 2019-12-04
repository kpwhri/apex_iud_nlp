"""
Interact with database through SQL Alchemy library
"""
import argparse
import sqlalchemy as sqla
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

DRIVER_TO_DBAPI = {
    'SQL Server': 'mssql+pyodbc',
    'MySQL': 'mysql+pyodbc',  # untested, subject to change
    'PostgreSQL': 'postgresql+psycopg2',  # untested, subject to change
}

Base = declarative_base()

CURRENT_ENGINE = {
}


class TableWrapper(object):
    """Wrap this around tables obtained from automap base to get easier column access"""

    def __init__(self, table):
        self.table = table

    def __getitem__(self, item):
        return self.table.__dict__[item]  # but this includes some other items
        # return self.table.__table__._columns[item]  # relies on private access

    def __getattr__(self, item):
        return getattr(self.table, item)


def get_new_session(engine=None, name=None):
    if engine:
        return sessionmaker(bind=engine)()
    else:
        return sessionmaker(bind=CURRENT_ENGINE[name])()


def add_dbargs_to_argparser(parser=None):
    """

    :param parser: existing argparser, or None to create one
    :return: argparse.ArgumentParser
    """
    if not parser:
        parser = argparse.ArgumentParser(fromfile_prefix_chars='@!')
    parser.add_argument('--dbapi',
                        help='DBAPI (see SqlAlchemy doco).')
    parser.add_argument('--database', required=True,
                        help='Database name.')
    parser.add_argument('--server', required=True,
                        help='Server name to connect to.')
    parser.add_argument('--driver', required=True,
                        help='Driver. No need to specify dbapi if driver in list: {}'.format(
                            ', '.join(DRIVER_TO_DBAPI.keys())))
    return parser


def get_engine_from_args(argstring, name=None):
    """

    :param argstring: sys.argv, or equivalent
    :param name:
    :return:
    """
    return get_engine(name=name,
                      **vars(add_dbargs_to_argparser().parse_known_args(argstring)[0]))


def get_tables(engine, *tablenames, schema='dbo'):
    metadata = MetaData(engine, schema=schema)
    autobase = automap_base(metadata=metadata)
    autobase.prepare(engine, reflect=True)
    tables = []
    for tablename in tablenames:
        if tablename in autobase.classes.keys():
            try:
                tables.append(autobase.classes[tablename])
                continue  # don't throw error if reached
            except AttributeError as ae:
                print(ae)
        # throw error if table name found
        raise ValueError('Table {}.{} does not exist or does not have a primary key.'
                         ' Add a primary key (ALTER TABLE {} ADD ID INTEGER IDENTITY(1,1)'
                         ' Or set the primary key '
                         ' ALTER TABLE {} ALTER COLUMN ID INTEGER NOT NULL '
                         ' ALTER TABLE {} ADD CONSTRAINT {}_pk PRIMARY KEY (ID)'
                         ''.format(schema, tablename, tablename, tablename, tablename, tablename))
    return tables


def get_engine(name=None, **kwargs):
    """

    :param name: name to give new connection; name of connection to retrieve
    :param kwargs:
        * dbapi
        * database
        * server
        * driver
        * pool_size
    :return:
    """
    server = kwargs.get('server', None)
    connection_string = kwargs.get('connection_string', None)
    if CURRENT_ENGINE and not server and not connection_string:
        try:
            return CURRENT_ENGINE[name]
        except KeyError:
            pass
        if len(CURRENT_ENGINE) == 1:
            return CURRENT_ENGINE[list(CURRENT_ENGINE.keys())[0]]
        else:
            raise ValueError('Multiple connections: unknown which connection to retrieve.')
    elif server:
        load_session(name=name, **kwargs)
    elif connection_string:
        load_session(name=name, **kwargs)
    return CURRENT_ENGINE[name]


def load_session(pool_size=5, name=None, **kwargs):
    """
    Create a session, with the specified connection.
    :param: connection string or tuple(driver, server, database)
    :return:
    """
    global CURRENT_ENGINE
    constr = get_connection_string(**kwargs)
    if pool_size == 0 or 'sqlite' in constr:
        CURRENT_ENGINE[name] = sqla.create_engine(constr, poolclass=NullPool)
    else:
        CURRENT_ENGINE[name] = sqla.create_engine(constr, pool_size=pool_size)
    return sessionmaker(bind=CURRENT_ENGINE[name])()


def get_connection_string(**kwargs):
    try:
        return kwargs['connection_string']
    except KeyError:
        return get_connection_string_from_args(**kwargs)


def get_connection_string_from_args(dbapi=None, database=None, server=None, driver=None, **kwargs):
    if not database or not server or not driver:
        raise ValueError('Database configuration requires driver, server, and database to be specified.')

    if driver and not dbapi:
        try:
            dbapi = DRIVER_TO_DBAPI[driver]
        except KeyError:
            raise ValueError('Could not infer DBAPI from driver "{}".'.format(driver))

    return '{dbapi}://@{server}/{database}?driver={driver}'.format(
        dbapi=dbapi, server=server, database=database, driver=driver)
