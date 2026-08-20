import xml.etree.cElementTree as ET
import os


def _get_files():
    """Generate a list of all Glade files in glade/ and subdirectories."""
    rv = []

    def recursive(path):
        for f in os.listdir(path):
            filename = os.path.join(path, f)
            if os.path.isdir(filename):
                recursive(filename)
            elif filename.endswith(".glade"):
                rv.append(filename)

    recursive("glade/")
    return rv


def _check_ids(el, filename, parent_id):
    """Recursively check widget IDs, allowing intentional anonymous menu content."""
    for child in el:
        if child.tag == "object":
            # GtkMenuButton supports an inline child widget that does not need
            # an ID. This is used by the daemon status button in app.glade.
            anonymous_menu_child = parent_id == "btDaemon"
            if anonymous_menu_child and "id" not in child.attrib:
                continue

            msg = "Widget has no ID in %s; class %s; Parent id: %s" % (
                filename,
                child.attrib["class"],
                parent_id,
            )
            assert "id" in child.attrib and child.attrib["id"], msg
            for subel in child:
                if subel.tag == "child":
                    _check_ids(subel, filename, child.attrib["id"])


class TestGlade(object):
    """Tests Glade files for known GUI-loading problems."""

    def test_every_widget_has_id(self):
        """Check widget IDs while allowing intentional anonymous GTK children."""
        for filename in _get_files():
            root = ET.parse(filename).getroot()
            _check_ids(root, filename, "<root element>")
