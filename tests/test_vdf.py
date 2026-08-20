from io import StringIO
from scc.lib.vdf import parse_vdf
from scc.foreign.vdf import VDFProfile
import os, pytest

class TestVDF(object):
	""" Tests VDF parser """

	def test_parsing(self):
		sio = StringIO("""
		"data"
		{
			"version" "3"
			"more data" {
				"version" "7"
			}
		}
		""")
		parsed = parse_vdf(sio)
		assert type(parsed["data"]) == dict
		assert parsed["data"]["version"] == "3"
		assert parsed["data"]["more data"]["version"] == "7"

	def test_dict_without_key(self):
		sio = StringIO("""
		"data"
		{
			"version" "3"
			{
				"version" "7"
			}
		}
		""")
		with pytest.raises(ValueError):
			parse_vdf(sio)

	def test_unclosed_bracket(self):
		sio = StringIO("""
		"data"
		{
			"version" "3"
			"more data" {
				"version" "7"
			}
		""")
		with pytest.raises(ValueError):
			parse_vdf(sio)

	def test_too_many_brackets(self):
		sio = StringIO("""
		"data"
		{
			"version" "3"
			"more data" {
				"version" "7"
			}
			}
		}
		""")
		with pytest.raises(ValueError):
			parse_vdf(sio)

	def test_import(self):
		path = "tests/vdfs"
		for f in os.listdir(path):
			filename = os.path.join(path, f)
			print("Testing import of '%s'" % filename)
			VDFProfile().load(filename)
