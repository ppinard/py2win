""""""

# Standard library modules.
import os
import sys
import glob
import shutil
import zipfile
import tarfile
import fnmatch
import subprocess
from distutils import sysconfig
from distutils.ccompiler import new_compiler
import logging
logger = logging.getLogger(__name__)

# Third party modules.
import requests
import requests_cache
requests_cache.install_cache()

# Local modules.

# Globals and constants variables.

class EmbedPython:

    PYTHON_SOURCE_BASEURL = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    PYTHON_EMBED_BASEURL = 'https://www.python.org/ftp/python/{version}/python-{version}-embed-{arch}.zip'
    GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'
    PYTHON_MANIFEST_URL = 'https://raw.githubusercontent.com/python/cpython/master/PC/python.manifest'

    PYTHON_GUI_MAIN_CODE = """
#include <windows.h>
#include <stdio.h>
#include "Python.h"

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                   LPWSTR lpstrCmd, int nShow)
{{
    wchar_t *args[] = {{ L"-I", L"-c", L"import {module}; {module}.{method}()" }};
    return Py_Main(3, args);
}}
    """
    
    """
    According to the Python sys.argv documentation, "If the command was executed using the -c command line option to the interpreter, argv[0] is set to the string '-c'".
    This causes problem with argument parsers which expects the program name to be the first argument.
    The ``sys.argv`` are therefore modified to set first argument as the executable.
    """
    PYTHON_CONSOLE_MAIN_CODE = """
#include <stdio.h>
#include <Python.h>

int main(int argc, char *argv[])
{{
    wchar_t** _argv = PyMem_Malloc(sizeof(wchar_t*)*(argc + 2));
    _argv[0] = L"-I";
    _argv[1] = L"-c";
    _argv[2] = L"import sys; sys.argv[0] = sys.executable; import {module}; {module}.{method}()";
    for (int i=1; i<argc; i++) {{
      wchar_t* arg = Py_DecodeLocale(argv[i], NULL);
      _argv[i + 2] = arg;
    }}
    
    int returncode = Py_Main(argc + 2, _argv);
    
    PyMem_Free(_argv);
    
    return returncode;
}}
    """

    def __init__(self, project_name, project_version, extra_wheel_dir=None):
        """
        Creates the class to create an embedded distribution.

        Use :meth:`add_wheel` to add wheel(s) associated to the project.
        Use :meth:`add_script` to specify which script to convert to an executable.
        Then call :meth:`run`.

        :arg project_name: project name
        :arg project_version: project version (e.g. ``0.1.2``)
        :arg extra_wheel_dir: directory containing wheels to use instead of
            downloading them from PyPI
        """
        self.project_name = project_name
        self.project_version = project_version
        self.extra_wheel_dir = extra_wheel_dir
        self.requirements = []
        self.wheel_filepaths = []
        self.scripts = []
        self.pypi_packages = []

    def _download_file(self, url, filepath):
        """
        Downloads file at *url* and saves it at *filepath*.
        https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        """
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            raise IOError('Cannot download {}'.format(url))

        with open(filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        r.close()

    def _download_python_embedded(self, workdir):
        filepath = os.path.join(workdir, 'python_embed.zip')

        try:
            version = '{0.major}.{0.minor}.{0.micro}'.format(sys.version_info)
            is_64bits = sys.maxsize > 2 ** 32
            arch = 'amd64' if is_64bits else 'win32'
            url = self.PYTHON_EMBED_BASEURL.format(version=version, arch=arch)

            logger.info('downloading {0}'.format(url))
            self._download_file(url, filepath)

            logger.info('extracting zip in {0}'.format(workdir))
            with zipfile.ZipFile(filepath, 'r') as zf:
                zf.extractall(workdir)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def _prepare_python(self, workdir):
        logger.info('extracting python3X.zip')

        for filepath in glob.glob(os.path.join(workdir, 'python*.zip')):
            with zipfile.ZipFile(filepath, 'r') as zf:
                zf.extractall(os.path.join(workdir, 'Lib'))

            os.remove(filepath)

        for filepath in glob.glob(os.path.join(workdir, '*._pth')):
            os.remove(filepath)

    def _fix_lib2to3(self, workdir):
        logger.info('fixing lib2to3')

        tarfilepath = os.path.join(workdir, 'python_source.tgz')

        try:
            version = '{0.major}.{0.minor}.{0.micro}'.format(sys.version_info)
            url = self.PYTHON_SOURCE_BASEURL.format(version=version)

            logger.info('downloading {0}'.format(url))
            self._download_file(url, tarfilepath)

            logger.info('extracting files in {0}'.format(workdir))
            with tarfile.open(tarfilepath) as tar:
                for member in tar.getmembers():
                    if not fnmatch.fnmatch(member.name, 'Python-*/Lib/lib2to3/fixes/*.py') and \
                            not fnmatch.fnmatch(member.name, 'Python-*/Lib/lib2to3/pgen2/*.py'):
                        continue

                    logger.debug('extracting {0}'.format(member.name))
                    buf = tar.extractfile(member)

                    _, path = member.name.split('/', 1)
                    filepath = os.path.join(workdir, path)
                    with open(filepath, 'wb') as fp:
                        fp.write(buf.read())

                    buf.close()
        finally:
            if os.path.exists(tarfilepath):
                os.remove(tarfilepath)

    def _install_pip(self, python_executable):
        filepath = os.path.join(os.path.dirname(python_executable), 'get-pip.py')

        try:
            logger.info('downloading {0}'.format(self.GET_PIP_URL))
            self._download_file(self.GET_PIP_URL, filepath)

            args = [python_executable, filepath]
            logger.debug('running {0}'.format(' '.join(args)))
            subprocess.run(args, check=True)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def _install_wheels(self, python_executable):
        if not self.wheel_filepaths:
            return

        args = [python_executable, '-m', 'pip', 'install', '-U']
        if self.extra_wheel_dir:
            args += ['--find-links', self.extra_wheel_dir]

        args.extend(self.wheel_filepaths)

        if self.extra_wheel_dir:
            for filepath in glob.glob(os.path.join(self.extra_wheel_dir, '*.whl')):
                args.append(filepath)

        logger.debug('running {0}'.format(' '.join(args)))
        subprocess.run(args, check=True)

    def _install_requirements(self, python_executable):
        if not self.requirements:
            return

        args = [python_executable, '-m', 'pip', 'install', '-U']
        if self.extra_wheel_dir:
            args += ['--find-links', self.extra_wheel_dir]

        args.extend(self.requirements)

        logger.debug('running {0}'.format(' '.join(args)))
        subprocess.run(args, check=True)

    def _install_pypi_packages(self, python_executable):
        if not self.pypi_packages:
            return

        args = [python_executable, '-m', 'pip', 'install', '-U']
        args.extend(self.pypi_packages)
        subprocess.run(args, check=True)

    def _create_main(self, workdir, module, method, executable_name, console=True):
        # Create code
        logger.info('writing main executable code')

        c_filepath = os.path.join(workdir, executable_name + '.c')

        if console:
            content = self.PYTHON_CONSOLE_MAIN_CODE.format(module=module, method=method)
        else:
            content = self.PYTHON_GUI_MAIN_CODE.format(module=module, method=method)

        with open(c_filepath, 'w') as fp:
            fp.write(content)

        # Create manifest
        logger.info('downloading Python manifest')

        manifest_filepath = os.path.join(workdir, executable_name + '.exe.manifest')

        self._download_file(self.PYTHON_MANIFEST_URL, manifest_filepath)

        # Compile
        logger.info('compiling main executable code')

        objects = []
        try:
            compiler = new_compiler(verbose=True)
            compiler.initialize()

            py_include = sysconfig.get_python_inc()
            plat_py_include = sysconfig.get_python_inc(plat_specific=1)
            compiler.include_dirs.append(py_include)
            if plat_py_include != py_include:
                compiler.include_dirs.append(plat_py_include)

            compiler.library_dirs.append(os.path.join(sys.base_exec_prefix, 'libs'))

            objects = compiler.compile([c_filepath])
            output_progname = os.path.join(workdir, executable_name)
            compiler.link_executable(objects, output_progname)
        finally:
            if os.path.exists(c_filepath):
                os.remove(c_filepath)
            if os.path.exists(manifest_filepath):
                os.remove(manifest_filepath)
            for filepath in objects:
                os.remove(filepath)

    def _create_zip(self, workdir, dist_dir, fullname):
        logger.info('creating zip')
        zipfilepath = os.path.join(dist_dir, fullname + ".zip")

        with zipfile.ZipFile(zipfilepath, "w") as zf:
            for dirpath, _dirnames, filenames in os.walk(workdir):
                for name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    if os.path.isfile(path):
                        zf.write(path, path)

    def add_wheel(self, filepath):
        """
        Adds a wheel to be installed.
        """
        self.wheel_filepaths.append(filepath)

    def add_requirement(self, requirement):
        """
        Adds a requirement to be installed (e.g. a PyPI package).
        """
        self.requirements.append(requirement)

    def add_script(self, module, method, executable_name, console=True):
        """
        Adds a console script to be converted to an exectuable.

        :arg module: module containing the method to start the script
            (e.g. ``package1.sample.gui``)
        :arg method: name of method to execute
            (e.g. ``main``)
        :arg executable_name: filename of the final executable
        :arg console: whether the script should run as a console script or
            a GUI script.
        """
        self.scripts.append([module, method, executable_name, console])

    def add_pypi_package(self, package):
        self.pypi_packages.append(package)

    def run(self, dist_dir, clean=True, zip_dist=False):
        """
        Creates an embedded distribution with the specified wheel(s) and script(s).

        :arg dist_dir: destination directory
        :arg clean: whether to remove all existing files in the destination directory
        :arg zip_dist: whether to create a zip of the distribution
        """
        if sys.platform != 'win32':
            raise OSError('Only windows platform supported')
        if sys.version_info.major != 3:
            raise OSError('Only Python 3 supported')

        # Create working directory
        fullname = '{0}-{1}'.format(self.project_name, self.project_version)
        workdir = os.path.join(dist_dir, fullname)
        if os.path.exists(workdir) and clean:
            shutil.rmtree(workdir)
        os.makedirs(workdir, exist_ok=True)

        # Install python
        python_executable = os.path.join(workdir, 'python.exe')
        if not os.path.exists(python_executable):
            self._download_python_embedded(workdir)
            self._prepare_python(workdir)
            self._fix_lib2to3(workdir)

        # Install pip
        self._install_pip(python_executable)

        # Install wheels, pypi and requirements
        self._install_wheels(python_executable)
        self._install_requirements(python_executable)
        self._install_pypi_packages(python_executable)

        # Process entry points
        for module, method, executable_name, console in self.scripts:
            self._create_main(workdir, module, method, executable_name, console)

        # Create zip
        if zip_dist:
            self._create_zip(workdir, dist_dir, fullname)

        return workdir
