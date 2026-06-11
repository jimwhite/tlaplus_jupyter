import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

from tlaplus_jupyter.kernel import TLAPlusKernel


class TestJavaCommand(TestCase):

    def make_kernel_with_tla_tools(self):
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)

        vendor = os.path.join(tempdir.name, 'vendor')
        os.mkdir(vendor)
        jar = os.path.join(vendor, 'tla2tools.jar')
        with open(jar, 'w'):
            pass

        kernel = TLAPlusKernel()
        kernel.vendor_path = vendor
        return kernel, jar

    def test_java_command_uses_tla_tools_jar(self):
        kernel, jar = self.make_kernel_with_tla_tools()

        with patch.dict(os.environ, {}, clear=True), \
                patch('tlaplus_jupyter.kernel.shutil.which', return_value='/usr/bin/java'):
            self.assertEqual(kernel.java_command(), [
                '/usr/bin/java',
                '-XX:+UseParallelGC',
                '-Dtlc2.TLC.ide=tlaplus_jupyter',
                '-cp', jar,
            ])

    def test_java_command_uses_tla_tools_jar_from_env(self):
        kernel = TLAPlusKernel()

        with tempfile.TemporaryDirectory() as tools_dir:
            jar = os.path.join(tools_dir, 'tla2tools.jar')
            with open(jar, 'w'):
                pass

            with patch.dict(os.environ, {'TLAPLUS_JUPYTER_TLA2TOOLS_JAR': jar}, clear=True), \
                    patch('tlaplus_jupyter.kernel.shutil.which', return_value='/usr/bin/java'):
                self.assertEqual(kernel.java_command(), [
                    '/usr/bin/java',
                    '-XX:+UseParallelGC',
                    '-Dtlc2.TLC.ide=tlaplus_jupyter',
                    '-cp', jar,
                ])

    def test_java_command_reports_missing_tla_tools_jar(self):
        kernel = TLAPlusKernel()

        with tempfile.TemporaryDirectory() as vendor:
            kernel.vendor_path = vendor

            with patch.dict(os.environ, {}, clear=True), \
                    patch('tlaplus_jupyter.kernel.shutil.which', return_value='/usr/bin/java'), \
                    self.assertRaisesRegex(RuntimeError, 'Unable to find tla2tools.jar'):
                kernel.java_command()
