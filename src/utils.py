# Example helper: capitalize player names
def format_name(name):
    return " ".join([word.capitalize() for word in name.split()])
