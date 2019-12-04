"""
Example configuration file.

* Non-necessary items can be omitted
* For input data, handles lists of directories or database connections
    *
"""

schema = {
    'corpus': {
        'directories': [
            'PATH_1',
            'PATH_2',
            'PATH_3',
        ],
        'version': None,  # only include if using corpus-dump deployment
        'connections': [  # database connections
            {
                'name': 'TABLE_NAME',
                'connection_string': 'CONNECTION_STRING',
                'driver': 'DRIVER',
                'server': 'DB_SERVER',
                'database': 'DB_DATABASE',
                'name_col': 'COLUMN_DOCUMENT_LABEL',
                'text_col': 'COLUMN_DOCUMENT_TEXT'
            },
        ]
    },
    'annotations': [
        'FILE_CONTAINING_ANNOTATIONS'
    ],
    'output': {
        'name': 'TABLE_OR_FILE_NAME',
        'kind': 'sql_csv',  # sql, csv, etc.
        'path': 'DIRECTORY_PATH',
        'driver': 'DB_DRIVER',
        'server': 'DB_SERVER',
        'database': 'DB_DATABASE',
    },
    'select': {
        'start': 1,
        'end': 200,
        'encoding': 'utf8',
        'filenames': ['FILE_1', 'FILE_2'],  # only these filenames
    },
    'algorithm': {  # see options in apex.algo.__init__.py
        'names': [
            'ALGORITHM_1',
            'ALGORITHM_2',
        ]
    },
    'loginfo': {
        'directory': 'LOG_DIRECTORY',
        'ignore': False,  # ignore writing log information
    },
    'skipinfo': {
        # For large datasets, a "SKIP" result can be returned;
        #  these skipped values will be skipped in the algorithm
        #  every time it is re-run; this can significantly reduce
        #  processing time
        'path': 'PATH_TO_FILE',
        'rebuild': False,  # If true, rebuild this file
        'ignore': False,  # If true, ignore skip file for this run
    },
    'logger': {
        'verbose': False
    }
}

print(schema)  # required, or config will not be read
