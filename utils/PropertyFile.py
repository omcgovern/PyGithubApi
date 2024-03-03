class PropertyFile:

    def __init__(self, file):
        separator = "="
        self.keys = {}

        # I named your file conf and stored it
        # in the same directory as the script

        with open(file) as f:
            for line in f:
                if separator in line:
                    # Find the name and value by splitting the string
                    name, value = line.split(separator, 1)

                    # Assign key value pair to dict
                    # strip() removes white space from the ends of strings
                    self.keys[name.strip()] = value.strip()

    def get_properties(self):
        return self.keys
