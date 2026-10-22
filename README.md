# Mac Files Organizer

A small command-line organizer for macOS, also usable on Linux. Requires Python
3.10 or newer and has no external dependencies.

From this repository, preview a folder:

```sh
python3 organizer.py ~/Downloads
```

Review the proposed destinations, then move the files:

```sh
python3 organizer.py ~/Downloads --apply
```

Files go into Images, Documents, Audio, Videos, Archives, Installers, Code, or
Other. Existing filenames receive a numbered suffix instead of being overwritten.
Only immediate files are organized. Hidden files, symbolic links, subfolders,
and common incomplete downloads are skipped. Destination symlinks are rejected.
macOS may ask Terminal for permission to access Downloads or Documents.

Try a sample folder before organizing important files. Moves copy file contents
and standard metadata before deleting the source; macOS resource forks, Finder
tags, ACLs, and other extended metadata are not guaranteed to be preserved.
If a later move fails, earlier successful moves remain in their new locations.
Avoid changing the folder while the organizer runs.

Run tests:

```sh
python3 -m unittest discover -s tests -v
```

The project uses Python's standard library. There is no server or background
process to start. macOS-specific permissions and metadata behavior require
validation on a Mac.
