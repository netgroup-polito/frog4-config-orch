def dump_json_file(filepath):
    try:
        with open(filepath) as file:
            json_data = file.read()
        file.close()
        return json_data
    except Exception as ex:
        raise IOError(str(ex))