def camel_to_snake(name: str) -> str:
    """Convert name from CamelCase to snake_case.

    Args:
        name: A symbol name, such as a class name.

    Returns:
        Name in snake case.

    Examples:
        >>> camel_to_snake("camelCase")
        'camel_case'
        >>> camel_to_snake("ThisIsATest")
        'this_is_a_test'
        >>> camel_to_snake("ABC")
        'abc'
    """
    # Special case for all uppercase strings
    if name.isupper():
        return name.lower()

    pattern = re.compile(r"(?<!^)(?<!_)(?:[A-Z][a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$))")
    return pattern.sub(lambda m: f"_{m.group(0).lower()}", name).lower()
