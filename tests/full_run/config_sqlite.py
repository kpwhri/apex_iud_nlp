
schema = {
    'corpus': {
        'connections': [  # database connections
            {
                'name': 'example_text',
                'connection_string': r'sqlite:///example.db',
                'name_col': 'id',
                'text_col': 'note_text'
            },
        ]
    },
    'output': {
        'name': 'test_sqlite_output',
        'kind': 'csv',  # sql, csv, etc.
        'path': '.',
    },
    'loginfo': {
        'ignore': True,
    },
}

print(schema)  # required, or config will not be read
