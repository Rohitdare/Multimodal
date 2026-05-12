def validate_output(schema_class, parsed_output):

    if schema_class is None:
        return parsed_output, None

    try:

        validated = schema_class(**parsed_output)

        return validated.model_dump(), None

    except Exception as e:

        return None, str(e)
