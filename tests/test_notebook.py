import os
import nbformat

from nbconvert.preprocessors import ExecutePreprocessor
from unittest import TestCase
from unittest.mock import patch

from tlaplus_jupyter.kernel import TLAPlusKernel


class TestNotebook(TestCase):

    @classmethod
    def setUpClass(cls):
        notebook_path = os.path.join(os.path.dirname(__file__), 'testnb.ipynb')
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)

        proc = ExecutePreprocessor(timeout=600)
        proc.allow_errors = True
        proc.preprocess(nb, {'metadata': {'path': '/'}})

        cls.cells = nb.cells

    def test_expr(self):
        cell = self.cells[0]
        self.assertEqual(cell.execution_count, 1)
        res = '{<<1, 1>>, <<1, 2>>, <<1, 3>>, <<2, 2>>, <<2, 3>>, <<3, 3>>}'
        self.assertEqual(cell.outputs[0]['text'], res)

    def test_module(self):
        cell = self.cells[1]
        self.assertEqual(cell.execution_count, 2)
        self.assertEqual(cell.outputs, [])

    def test_tlc_run(self):
        cell = self.cells[2]
        self.assertEqual(cell.execution_count, 3)
        text = "".join([o.text for o in cell.outputs])
        self.assertTrue('97 states generated' in text)

    def test_expr_error(self):
        cell = self.cells[3]
        self.assertEqual(cell.execution_count, 4)
        text = cell.outputs[0].text
        self.assertTrue('Could not parse ' in text)


class TestJavaPathResolution(TestCase):

    @patch('tlaplus_jupyter.kernel.shutil.which', return_value='/usr/bin/java')
    def test_prefers_java_from_path(self, _):
        kernel = TLAPlusKernel()
        self.assertEqual(kernel.java_command()[0], '/usr/bin/java')

    @patch('tlaplus_jupyter.kernel.shutil.which', return_value=None)
    @patch('tlaplus_jupyter.kernel.os.access', side_effect=lambda _, mode: mode == os.X_OK)
    @patch('tlaplus_jupyter.kernel.os.path.isfile', return_value=True)
    def test_uses_java_home_when_path_missing(self, *_):
        with patch.dict(os.environ, {'JAVA_HOME': '/opt/jdk'}):
            kernel = TLAPlusKernel()
            self.assertEqual(kernel.java_command()[0], '/opt/jdk/bin/java')

    @patch('tlaplus_jupyter.kernel.shutil.which', return_value=None)
    @patch('tlaplus_jupyter.kernel.os.access', return_value=False)
    @patch('tlaplus_jupyter.kernel.os.path.isfile', return_value=True)
    def test_raises_when_java_home_is_not_executable(self, *_):
        with patch.dict(os.environ, {'JAVA_HOME': '/opt/jdk'}):
            kernel = TLAPlusKernel()
            with self.assertRaisesRegex(RuntimeError, 'Java executable not found'):
                kernel.java_command()

    @patch('tlaplus_jupyter.kernel.shutil.which', return_value=None)
    @patch('tlaplus_jupyter.kernel.os.path.isfile', return_value=False)
    def test_raises_when_java_missing(self, *_):
        with patch.dict(os.environ, {}, clear=True):
            kernel = TLAPlusKernel()
            with self.assertRaisesRegex(RuntimeError, 'Java executable not found'):
                kernel.java_command()
