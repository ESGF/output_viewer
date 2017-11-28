import configparser
import sys
import os
import glob


class ViewerConfig(object):
    """
    Easy access to the various config files associated with output_viewer.
    """

    def __init__(self):
        self.path = os.path.expanduser("~/.output_viewer")
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.parser = configparser.SafeConfigParser()
        for f in glob.iglob(os.path.join(self.path, "*.cfg")):
            with open(f) as fp:
                self.parser.readfp(fp)
    
    def get(self, section, key):
        if self.parser.has_section(section):
            if self.parser.has_option(section, key):
                return self.parser.get(section, key)
        return None
    
    def set(self, section, key, value):
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, key, str(value))

    def extract_section(self, section, cfg=None):
        if cfg is None:
            cfg = configparser.SafeConfigParser()
        if self.parser.has_section(section):
            options = self.parser.options(section)
        else:
            options = []

        cfg.add_section(section)
        for o in options:
            cfg.set(section, o, self.parser.get(section, o))
        return cfg
    
    def save(self):
        """
        Saves the configurations out into a variety of understandable files in $HOME/.output_viewer.

        Maps the [upload] section to one file, and each of the server configs to servers.cfg.
        """
        with open(os.path.join(self.path, "upload.cfg"), "w") as upload_file:
            new_cfg = self.extract_section("upload")
            new_cfg.write(upload_file)

        with open(os.path.join(self.path, "servers.cfg"), "w") as server_file:
            cfg = configparser.SafeConfigParser()    
            for section in self.parser.sections():
                if section == "upload":
                    continue
                self.extract_section(section, cfg=cfg)
            cfg.write(server_file)

