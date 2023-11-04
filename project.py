import sys
import inspect
import argparse
import logging.config
import os
import subprocess
import shutil
import json
from pathlib import Path


class Project:
    log_level = None
    logging_config = None
    logger = None
    utility_methods = None
    project_dir = None
    commands = None
    test_entry = None

    def __init__(self, args=None):
        try:
            if args is None:
                args = []

            parser = argparse.ArgumentParser()

            parser.add_argument(
                '-ll', '--log-level',
                nargs='?',
                type=str,
                default='INFO'
            )
            parser.add_argument(
                'commands',
                nargs='*',
                type=str,
                default=['default']
            )
            parser.add_argument(
                '-te', '--test-entry',
                nargs='?',
                type=str,
                default='tests/test_core.py::TestCore::test_1'
            )

            arguments = parser.parse_args(args[1:])

            self.log_level = arguments.log_level

            self.logging_config = {
                'version': 1,
                'formatters': {
                    'messageFormatter': {
                        'format': '%(asctime)s|%(levelname)s|%(threadName)s|%(name)s|%(funcName)s|%(filename)s|%(lineno)d: %(message)s'
                    }
                },
                'handlers': {
                    'consoleHandler': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'messageFormatter',
                        'stream': 'ext://sys.stdout'
                    }
                },
                'loggers': {
                    'root': {
                        'level': self.log_level,
                        'handlers': ['consoleHandler']
                    }
                }
            }

            logging.config.dictConfig(self.logging_config)

            self.logger = logging.getLogger('.'.join([__class__.__module__, __class__.__name__]))

            self.utility_methods = []
            for method in inspect.getmembers(self, predicate=inspect.ismethod):
                if method[0] != '__init__' and method[0] != 'run':
                    self.utility_methods.append(method[0])

            self.project_dir = str(os.path.normpath(Path(__file__).parent))
            self.commands = arguments.commands
            self.test_entry = arguments.test_entry
        except Exception as e:
            self.logger.exception(e, stack_info=True)
            raise e

    def build(self):
        try:
            buildDir = str(os.path.normpath(Path(self.project_dir).joinpath('build')))
            envDir = str(os.path.normpath(Path(buildDir).joinpath('py-main-env')))
            pythonFile1 = str(os.path.normpath(Path(envDir).joinpath('Scripts', 'python.exe')))
            pythonFile2 = str(os.path.normpath(Path(envDir).joinpath('bin', 'python')))
            pythonCommand = None
            pyiMakespecFile1 = str(os.path.normpath(Path(envDir).joinpath('Scripts', 'pyi-makespec.exe')))
            pyiMakespecFile2 = str(os.path.normpath(Path(envDir).joinpath('bin', 'pyi-makespec')))
            pyiMakespecCommand = None
            pyinstallerFile1 = str(os.path.normpath(Path(envDir).joinpath('Scripts', 'pyinstaller.exe')))
            pyinstallerFile2 = str(os.path.normpath(Path(envDir).joinpath('bin', 'pyinstaller')))
            pyinstallerCommand = None

            if pythonCommand is None:
                if Path(pythonFile1).exists():
                    pythonCommand = pythonFile1
                elif Path(pythonFile2).exists():
                    pythonCommand = pythonFile2

            if pyiMakespecCommand is None:
                if Path(pyiMakespecFile1).exists():
                    pyiMakespecCommand = pyiMakespecFile1
                elif Path(pyiMakespecFile2).exists():
                    pyiMakespecCommand = pyiMakespecFile2

            if pyinstallerCommand is None:
                if Path(pyinstallerFile1).exists():
                    pyinstallerCommand = pyinstallerFile1
                elif Path(pyinstallerFile2).exists():
                    pyinstallerCommand = pyinstallerFile2

            if pythonCommand is None:
                # create env
                self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}' create env")
                try:
                    subprocess.run(
                        ['py', '-m', 'venv', envDir],
                        cwd=self.project_dir,
                        check=True,
                        text=True,
                        timeout=3 * 60
                    )
                except subprocess.CalledProcessError as e:
                    if e.stdout is not None:
                        self.logger.error(f"stdout: '{e.stdout}'")
                    if e.stderr is not None:
                        self.logger.error(f"stderr: '{e.stderr}'")
                    raise e

                if Path(pythonFile1).exists():
                    pythonCommand = pythonFile1
                elif Path(pythonFile2).exists():
                    pythonCommand = pythonFile2
                else:
                    raise Exception(f"Not exists pythonFile1: '{pythonFile1}' and pythonFile2: '{pythonFile2}'")

                # install dependencies
                self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}' install dependencies")
                try:
                    subprocess.run(
                        [pythonCommand, '-m', 'pip', 'install', '.'],
                        cwd=self.project_dir,
                        check=True,
                        text=True,
                        timeout=3 * 60
                    )
                except subprocess.CalledProcessError as e:
                    if e.stdout is not None:
                        self.logger.error(f"stdout: '{e.stdout}'")
                    if e.stderr is not None:
                        self.logger.error(f"stderr: '{e.stderr}'")
                    raise e

            if pyiMakespecCommand is None or pyinstallerCommand is None:
                # install dependencies
                self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}' install dependencies")
                try:
                    subprocess.run(
                        [pythonCommand, '-m', 'pip', 'install', '.[pyinstaller]'],
                        cwd=self.project_dir,
                        check=True,
                        text=True,
                        timeout=3 * 60
                    )
                except subprocess.CalledProcessError as e:
                    if e.stdout is not None:
                        self.logger.error(f"stdout: '{e.stdout}'")
                    if e.stderr is not None:
                        self.logger.error(f"stderr: '{e.stderr}'")
                    raise e

                if Path(pyiMakespecFile1).exists():
                    pyiMakespecCommand = pyiMakespecFile1
                elif Path(pyiMakespecFile2).exists():
                    pyiMakespecCommand = pyiMakespecFile2
                else:
                    raise Exception(f"Not exists pyiMakespecFile1: '{pyiMakespecFile1}' and pyiMakespecFile2: '{pyiMakespecFile1}'")

                if Path(pyinstallerFile1).exists():
                    pyinstallerCommand = pyinstallerFile1
                elif Path(pyinstallerFile2).exists():
                    pyinstallerCommand = pyinstallerFile2
                else:
                    raise Exception(f"Not exists pyinstallerFile1: '{pyinstallerFile1}' and pyinstallerFile2: '{pyinstallerFile2}'")

            if not Path(buildDir).joinpath('sphinx.spec').exists():
                # create spec
                self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}' create spec")
                try:
                    subprocess.run(
                        [
                            pyiMakespecCommand,
                            '--specpath', 'build',
                            '--collect-all', 'sphinx',
                            '--collect-all', 'sphinxcontrib.applehelp',
                            '--collect-all', 'sphinxcontrib.devhelp',
                            '--collect-all', 'sphinxcontrib.htmlhelp',
                            '--collect-all', 'sphinxcontrib.jquery',
                            '--collect-all', 'sphinxcontrib.jsmath',
                            '--collect-all', 'sphinxcontrib.qthelp',
                            '--collect-all', 'sphinxcontrib.serializinghtml',
                            '--collect-all', 'linuxdoc',
                            '--collect-all', 'breathe',
                            '--collect-all', 'mlx.traceability',
                            '--collect-all', 'docxbuilder',
                            '--collect-all', 'rst2pdf',
                            '--collect-all', 'latex2mathml',
                            '--add-data', 'py-main-env/Lib/site-packages/mlx/assets/*:mlx/assets',
                            '--add-data', 'py-main-env/Lib/site-packages/rst2pdf/styles/*:styles',
                            '--add-data', 'py-main-env/Lib/site-packages/rst2pdf/templates/*:templates',
                            '--contents-directory', '_internal',
                            '--name', 'exqudens-sphinx',
                            'src/exqudens/sphinx.py'
                        ],
                        cwd=self.project_dir,
                        check=True,
                        text=True,
                        timeout=3 * 60
                    )
                except subprocess.CalledProcessError as e:
                    if e.stdout is not None:
                        self.logger.error(f"stdout: '{e.stdout}'")
                    if e.stderr is not None:
                        self.logger.error(f"stderr: '{e.stderr}'")
                    raise e

            if not Path(buildDir).joinpath('dist').exists():
                # create executable dir
                self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}' create executable dir")
                try:
                    subprocess.run(
                        [
                            pyinstallerCommand,
                            '--workpath', 'build/pyinstaller-build',
                            '--distpath', 'build/dist',
                            'build/exqudens-sphinx.spec'
                        ],
                        cwd=self.project_dir,
                        check=True,
                        text=True,
                        timeout=3 * 60
                    )
                    shutil.copytree(
                        Path(buildDir).joinpath('dist', 'exqudens-sphinx', '_internal', 'styles'),
                        Path(buildDir).joinpath('dist', 'exqudens-sphinx', 'styles')
                    )
                    shutil.copytree(
                        Path(buildDir).joinpath('dist', 'exqudens-sphinx', '_internal', 'templates'),
                        Path(buildDir).joinpath('dist', 'exqudens-sphinx', 'templates')
                    )
                except subprocess.CalledProcessError as e:
                    if e.stdout is not None:
                        self.logger.error(f"stdout: '{e.stdout}'")
                    if e.stderr is not None:
                        self.logger.error(f"stderr: '{e.stderr}'")
                    raise e
        except Exception as e:
            self.logger.exception(e, stack_info=True)
            raise e

    def clean_build(self):
        try:
            buildDir = str(os.path.normpath(Path(self.project_dir).joinpath('build')))
            envDir = str(os.path.normpath(Path(buildDir).joinpath('py-main-env')))
            specFile = str(os.path.normpath(Path(buildDir).joinpath('sphinx.spec')))
            pyinstallerBuildDir = str(os.path.normpath(Path(buildDir).joinpath('pyinstaller-build')))
            distDir = str(os.path.normpath(Path(buildDir).joinpath('dist')))

            if (
                not Path(envDir).exists()
                and not Path(specFile).exists()
                and not Path(pyinstallerBuildDir).exists()
                and not Path(distDir).exists()
            ):
                return

            self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}'")

            if Path(envDir).exists():
                shutil.rmtree(envDir)

            if Path(specFile).exists():
                os.remove(specFile)

            if Path(pyinstallerBuildDir).exists():
                shutil.rmtree(pyinstallerBuildDir)

            if Path(distDir).exists():
                shutil.rmtree(distDir)
        except Exception as e:
            self.logger.exception(e, stack_info=True)
            raise e

    def test(self):
        try:
            buildDir = str(os.path.normpath(Path(self.project_dir).joinpath('build')))
            envDir = str(os.path.normpath(Path(buildDir).joinpath('py-test-env')))
            pythonFile1 = str(os.path.normpath(Path(envDir).joinpath('Scripts', 'python.exe')))
            pythonFile2 = str(os.path.normpath(Path(envDir).joinpath('bin', 'python')))
            pythonCommand = None
            conftestFile = str(os.path.normpath(Path(self.project_dir).joinpath('tests', 'conftest.py')))

            if Path(pythonFile1).exists():
                pythonCommand = pythonFile1
            elif Path(pythonFile2).exists():
                pythonCommand = pythonFile2

            if pythonCommand is None:
                # create env
                self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}' create env")
                try:
                    subprocess.run(
                        ['py', '-m', 'venv', envDir],
                        cwd=self.project_dir,
                        check=True,
                        text=True,
                        timeout=3 * 60
                    )
                except subprocess.CalledProcessError as e:
                    if e.stdout is not None:
                        self.logger.error(f"stdout: '{e.stdout}'")
                    if e.stderr is not None:
                        self.logger.error(f"stderr: '{e.stderr}'")
                    raise e

                if Path(pythonFile1).exists():
                    pythonCommand = pythonFile1
                elif Path(pythonFile2).exists():
                    pythonCommand = pythonFile2
                else:
                    raise Exception(f"Not exists pythonFile1: '{pythonFile1}' and pythonFile2: '{pythonFile2}'")

                # install dependencies
                self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}' install dependencies")
                try:
                    subprocess.run(
                        [pythonCommand, '-m', 'pip', 'install', '.[test]'],
                        cwd=self.project_dir,
                        check=True,
                        text=True,
                        timeout=3 * 60
                    )
                except subprocess.CalledProcessError as e:
                    if e.stdout is not None:
                        self.logger.error(f"stdout: '{e.stdout}'")
                    if e.stderr is not None:
                        self.logger.error(f"stderr: '{e.stderr}'")
                    raise e

            # test
            self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}'")
            try:
                subprocess.run(
                    [
                        pythonCommand,
                        '-m',
                        'pytest',
                        f"--log-cli-format={self.logging_config['formatters']['messageFormatter']['format']}",
                        '--log-cli-level=NOTSET',
                        '-c',
                        conftestFile,
                        '-x',
                        self.test_entry
                    ],
                    cwd=self.project_dir,
                    check=True,
                    text=True,
                    timeout=3 * 60
                )
            except subprocess.CalledProcessError as e:
                if e.stdout is not None:
                    self.logger.error(f"stdout: '{e.stdout}'")
                if e.stderr is not None:
                    self.logger.error(f"stderr: '{e.stderr}'")
                raise e
        except Exception as e:
            self.logger.exception(e, stack_info=True)
            raise e

    def clean_test(self):
        try:
            buildDir = str(os.path.normpath(Path(self.project_dir).joinpath('build')))
            envDir = str(os.path.normpath(Path(buildDir).joinpath('py-test-env')))

            if not Path(envDir).exists():
                return

            self.logger.info(f"execute '{inspect.currentframe().f_code.co_name}'")

            if Path(envDir).exists():
                shutil.rmtree(envDir)
        except Exception as e:
            self.logger.exception(e, stack_info=True)
            raise e

    def clean(self):
        try:
            self.clean_build()
            self.clean_test()
        except Exception as e:
            self.logger.exception(e, stack_info=True)
            raise e

    def run(self):
        try:
            if len(self.commands) == 1 and self.commands[0] == 'default':
                self.clean()
                self.build()
                self.test()
            else:
                for command in self.commands:
                    if command not in self.utility_methods:
                        raise Exception(f"command: '{command}' not in utility_methods: {self.utility_methods}")
                for command in self.commands:
                    method = getattr(self, command)
                    method()
        except Exception as e:
            self.logger.exception(e, stack_info=True)
            raise e


if __name__ == '__main__':
    args = sys.argv
    project = Project(args)
    result = project.run()
    sys.exit(result)
