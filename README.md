# Zip-Editor
A python-based project, which can be used to create zip files that can be used to test your program's decompression features.

# ZipFileEditor
ZipFileEditor.exe is a runnable .exe file that was generated using pyinstaller. 
The source code for the project is located inside the "source" folder.

# How to use it
If you are using the runnable file, then double-clicking it will open up a terminal window. Here is where you will interact with the program.
When entering the location of the zip file you wish to work with please make sure it is a valid zip file (follows PK header/structure rules) and has already been created. The location entered should be the absolute path, or the path relative to where the ZipFileEditor.exe or ZipFileEditor.py file is (depending on which one you run).

After entering the location of the zip file from which you want to gather information, you directed to an options menu. Type "-actions" for a list of possible actions you can take, and enter them to begin editing the zip file. Four functions will be available to you; "rename", "remove", "add", and "exit". When you are done with your changes, type and enter "exit" which will then prompt you to enter the name of the zip file you wish to place this changed data into. If you wish to rewrite the same file you began with, then enter the location of the file, as well as the original file name and extension. If you wish for a new file to be created, enter the location of the file, the new name, and the extension (if you don't add the .zip extension, the program will do it for you).

That's it! I hope this program comes to use for you, and you can use this program to make your code more secure.

# Rename
This function is useful in testing out how your decompression handles file names that are longer than what you would usually encounter. You can use this to test for buffer overflows by changing a file name to one that is 1000 characters. You can test for path traversals, by changing the name to "../Name", and so on. First, enter in the original name of the file that inside of the zip file you wish to change. To see a list of all the current files, type in "list". You can change the names of multiple files. You can also test how the program reacts to multiple files of the same name being decompressed.

# Remove
This function is used to remove any file that you may have accidentally added, or simply to see how the program you created reacts to certain files being missing from the zip file. Simply enter the name of the file you wish to remove, or you can type and enter "list" to see the names of all the files within the zip file.

# Add
This function is used to add any file you want into the zip file. You can do this to see how your program reacts to unzipping large files within the zip files, or certain files that should not be in your program space being decompressed into it. Simply add in the location of the file you wish to add, as well as its name and extension. The location should either be an absolute path, or a path relative to the ZipFileEditor.exe or ZipFileEditor.py (depending on what you are using).
