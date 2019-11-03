""""""

# Standard library modules.
from distutils.cmd import Command
from distutils import log
from distutils.command.build import show_compilers

# Third party modules.

# Local modules.
from py2win.embed import EmbedPython

# Globals and constants variables.


class bdist_windows(Command):

    description = "Build windows executable"

    user_options = [
        (
            "dist-dir=",
            "d",
            "directory to put final built distributions in " "[default: dist]",
        ),
        ("extra-wheel-dir=", None, "directory containing wheels already downloaded"),
        ("zip", None, "create zip of the program at the end"),
        ("no-clean", None, "do not remove the existing distribution"),
    ]

    boolean_options = ["zip", "no-clean"]

    help_options = [
        ("help-compiler", None, "list available compilers", show_compilers),
    ]

    def initialize_options(self):
        self.dist_dir = None
        self.compiler = None
        self.extra_wheel_dir = None
        self.zip = False
        self.no_clean = False

    def finalize_options(self):
        if self.dist_dir is None:
            self.dist_dir = "dist"

    def _parse_entry_point(self, entry_point):
        executable_name, value = entry_point.split("=")
        module, method = value.split(":")

        executable_name = executable_name.strip()
        module = module.strip()
        method = method.strip()

        return module, method, executable_name

    def run(self):
        project_name = self.distribution.get_name()
        project_version = self.distribution.get_version()
        embed = EmbedPython(project_name, project_version, self.extra_wheel_dir)

        # Build wheel
        log.info("preparing a wheel file of application")
        self.run_command("bdist_wheel")

        # Add wheel
        for command, _version, filepath in self.distribution.dist_files:
            if command != "bdist_wheel":
                continue
            embed.add_wheel(filepath)

        # Add entry points
        for entry_point in self.distribution.entry_points.get("console_scripts", []):
            module, method, executable_name = self._parse_entry_point(entry_point)
            embed.add_script(module, method, executable_name, console=True)

        for entry_point in self.distribution.entry_points.get("gui_scripts", []):
            module, method, executable_name = self._parse_entry_point(entry_point)
            embed.add_script(module, method, executable_name, console=False)

        # Run
        embed.run(self.dist_dir, not self.no_clean, self.zip)
