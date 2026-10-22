import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import organizer


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_preview_then_apply_and_repeat(self):
        (self.root / "photo.JPG").write_bytes(b"image")
        (self.root / "notes.pdf").write_bytes(b"document")
        (self.root / ".hidden").write_text("keep")
        (self.root / "video.part").write_text("keep")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(organizer.main([str(self.root)]), 0)
        self.assertTrue((self.root / "photo.JPG").exists())
        self.assertFalse((self.root / "Images").exists())
        organizer.apply(organizer.plan(self.root))
        self.assertEqual((self.root / "Images/photo.JPG").read_bytes(), b"image")
        self.assertEqual((self.root / "Documents/notes.pdf").read_bytes(), b"document")
        self.assertTrue((self.root / ".hidden").exists())
        self.assertTrue((self.root / "video.part").exists())
        self.assertEqual(organizer.plan(self.root), [])

    def test_collision_preserves_both_files(self):
        (self.root / "Images").mkdir()
        (self.root / "Images/a.png").write_text("old")
        (self.root / "a.png").write_text("new")
        organizer.apply(organizer.plan(self.root))
        self.assertEqual((self.root / "Images/a.png").read_text(), "old")
        self.assertEqual((self.root / "Images/a (1).png").read_text(), "new")

    def test_new_collision_after_preview_does_not_overwrite(self):
        (self.root / "a.txt").write_text("source")
        moves = organizer.plan(self.root)
        (self.root / "Documents").mkdir()
        (self.root / "Documents/a.txt").write_text("existing")
        with self.assertRaises(FileExistsError):
            organizer.apply(moves)
        self.assertEqual((self.root / "a.txt").read_text(), "source")
        self.assertEqual((self.root / "Documents/a.txt").read_text(), "existing")

    def test_symlinks_are_skipped_and_destination_symlink_rejected(self):
        (self.root / "linked.txt").symlink_to("missing")
        self.assertEqual(organizer.plan(self.root), [])
        (self.root / "a.png").write_text("image")
        (self.root / "Images").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            organizer.plan(self.root)


if __name__ == "__main__":
    unittest.main()
