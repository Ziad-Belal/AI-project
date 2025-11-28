# Example helper: capitalize product names
def format_name(name):
    return " ".join([word.capitalize() for word in name.split()])
