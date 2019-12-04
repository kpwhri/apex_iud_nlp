
schema = {
    'corpus': {
        'directories': [
            'files',
        ],
    },
    'output': {
        'name': 'test_file_output',
        'kind': 'csv',  # sql, csv, etc.
        'path': '.',
    },
    'loginfo': {
        'ignore': True,
    },
}

print(schema)  # required, or config will not be read
