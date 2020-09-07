# Name: Satinder Sikand
# Date September 07, 2020
# File: ZipFileEditor.py
# Purpose: Create a zip file editor, which can be used to test the decompression of
#          one's program for vulnerabilities (i.e. buffer overflow)
# GitHub: https://github.com/Satinder-Sikand/Zip-Editor

import os
from zipfile import ZipFile


# A Mapper class object which will contain the data of the different zip headers
class Mapper(object):
    def __init__(self):
        self.name = ""
        self.data = bytearray(b'')


# Global Variables for each header
localFH = [Mapper()]
centralFH = [Mapper()]
extraSignature = Mapper()
endSignature = Mapper()


# Change the local file offset locations listed in the central file header
def reset_offset():
    # Variable which will keep count of the number of characters
    total = 0
    for num in range(len(centralFH)):
        if num == 0:
            temp = num.to_bytes(4, "little")
            centralFH[num].data[42] = temp[0]
            centralFH[num].data[43] = temp[1]
            centralFH[num].data[44] = temp[2]
            centralFH[num].data[45] = temp[3]
            total += len(localFH[num].data)
        else:
            temp = total.to_bytes(4, "little")
            centralFH[num].data[42] = temp[0]
            centralFH[num].data[43] = temp[1]
            centralFH[num].data[44] = temp[2]
            centralFH[num].data[45] = temp[3]
            total += len(localFH[num].data)


# Change the End of Directory Record as needed
def end_dir_reset():
    # Size of central directory
    lengthCdir = 0
    for num in range(len(centralFH)):
        lengthCdir += len(centralFH[num].data)
    # Change the central directory size recorded in the end of directory record
    temp = bytearray(endSignature.data[0:8])
    temp += len(centralFH).to_bytes(2, "little")
    temp += temp[8:10]
    temp += bytearray(lengthCdir.to_bytes(4, "little"))
    # Size of local directory
    lengthLdir = 0
    for num in range(len(localFH)):
        lengthLdir += len(localFH[num].data)
    temp += bytearray(lengthLdir.to_bytes(4, "little"))
    temp += endSignature.data[20:len(endSignature.data)]
    endSignature.data = temp


# Show the list of current files
def list_files():
    for num in range(len(centralFH)):
        temp = centralFH[num].name
        if temp[-1] == "\n":
            print(temp[0:len(temp)-1], ", ", end="")
        else:
            print(temp, ", ", end="")
    print("")


# Remove a file from the zip file
def remove():
    # Make sure that there is more than one file. Don't want an empty zip
    if len(centralFH) <= 1:
        print("There is only one file in the zip file. You cannot remove any files.")
        return
    name = input("What file do you want to remove (type exit to return to options or list to see current files): ")
    while name != "exit":
        if name == "list":
            list_files()
            name = input("Enter another file name (with the extension), type exit, or type list: ")
        else:
            # Get the index of the file
            index = search(name)
            # If the file is found in the data, remove that file
            if index != -1:
                del localFH[index]
                del centralFH[index]
                # Change the offset data to make them match the current data format
                end_dir_reset()
                reset_offset()
                # If there is only one file left, than the user cannot remove any more files
                if len(centralFH) <= 1:
                    print("There is only one file in the zip file. You cannot remove any more files.")
                    return
                else:
                    name = input("Enter another file name (with the extension), type exit, or type list: ")
            else:
                print("\nSorry, there is no file with this name.")
                name = input("Enter a valid file name (with the extension), type exit, or type list: ")


def create_zip(zipName):
    # Create or rewrite the zip file
    a = open(zipName, "wb")
    for x in localFH:
        # Add in local file header data
        a.write(x.data)
    for x in centralFH:
        # Add in central file header data
        a.write(x.data)
    # If there is extraSignature data then add that as well
    if len(extraSignature.data) > 0:
        print("There is data in extraSignature.")
        a.write(extraSignature.data)
    # Add in end of directory record data
    a.write(endSignature.data)
    a.close()


# Add a file into the zip file
def add():
    # Get file name and location
    loc = input("\nEnter the path to the file you want to add (include file name and extension): ")
    # No file has been added so far
    change = False
    # Make the current information into a temporary zip file
    create_zip("temporaryZipFileToDelete.zip")
    zipobj = ZipFile("temporaryZipFileToDelete.zip", "a")
    while loc != "exit":
        # Check if the file exists
        if os.path.isfile(loc):
            # Write the file into the zip file
            zipobj.write(loc, os.path.basename(loc))
            change = True
            print("\nThe file was successfully added.")
            loc = input("Please enter another path to the file (include file name and extension) or type exit: ")
        else:
            loc = input("There is no file with such a name. Please enter a valid file path or type exit: ")
    zipobj.close()
    # If a file(s) has been added
    if change:
        # Reset the global variables
        global localFH, centralFH, extraSignature, endSignature
        localFH = [Mapper()]
        centralFH = [Mapper()]
        extraSignature = Mapper()
        endSignature = Mapper()
        # Grab the information from the new temporary zip file
        sep_chunk("temporaryZipFileToDelete.zip", bytearray(b'\x50\x4b\x03\x04'))
        # Add in the file names to the Mapper variables
        file_labels()
    # Remove the temporary file
    os.remove("temporaryZipFileToDelete.zip")


# Rename a file in the zip file
def rename():
    name = input("What file do you want to rename (or type list to see current files): ")
    new_name = ""
    while new_name != "exit":
        if name == "exit":
            break
        elif name == "list":
            list_files()
            name = input("Enter a valid file name (include extension), type exit to return to options, or type list: ")
            continue
        index = search(name)
        if index > -1:
            new_name = input("Rename file to (include extension) or type exit to return to options: ")
            if new_name == "exit":
                break
            if len(new_name) > 65535:
                print("This name is too long. Please select a name that is 65535 characters or less")
                new_name = input("Rename file to (include extension) or type exit to return to options: ")
                continue
            # Add information for local file header
            temp = bytearray(localFH[index].data[0:26])
            temp += len(new_name).to_bytes(2, "little")
            temp += bytearray(localFH[index].data[28:30])
            temp += bytearray(new_name, "UTF8")
            temp += localFH[index].data[(30+len(name)):len(localFH[index].data)]
            localFH[index].data = temp
            localFH[index].name = new_name
            # Add information for central file header
            temp = bytearray(centralFH[index].data[0:28])
            temp += len(new_name).to_bytes(2, "little")
            temp += bytearray(centralFH[index].data[30:46])
            temp += bytearray(new_name, "UTF8")
            temp += centralFH[index].data[(46+len(name)):len(centralFH[index].data)]
            centralFH[index].data = temp
            centralFH[index].name = new_name
            # Change information in the end of directory record
            end_dir_reset()
            print('\nThe file name has been changed successfully.')
            name = input("Rename another file (include extension), type exit to return to options, or type list: ")
        else:
            print("\nSorry, there is no file with such a name. Please enter a valid file name.")
            name = input("Enter a valid file name (include extension), type exit to return to options, or type list: ")
    reset_offset()


# Search function
def search(name):
    for num in range(len(centralFH)):
        if centralFH[num].name == (name+"\n") or centralFH[num].name == name:
            return num
    return -1


# Add the names of the files
def file_labels():
    count = 0
    for x in centralFH:
        byt = x.data[28:30]
        length = int.from_bytes(byt, "little")
        x.name = x.data[46:47+length].decode("UTF8")
        localFH[count].name = x.name
        count += 1


# Used to add the separated data to LFH or CFH section
def add_temp(sig1, sig2, buffer, part, head):
    temp = Mapper()
    temp.data += (bytearray(sig1) + part)
    if head == 1:
        if localFH[0].data == b'':
            localFH[len(localFH)-1] = temp
        else:
            localFH.append(temp)
    elif head == 2:
        if centralFH[0].data == b'':
            centralFH[len(centralFH)-1] = temp
        else:
            centralFH.append(temp)
    buffer = bytearray(sig2) + buffer
    return buffer


# Add all the current data to LFH or CFH section, but leave the last 3 bytes in case they hold the next signature
def break_add_temp(sig, buffer, head):
    temp = Mapper()
    temp.data += (bytearray(sig) + (buffer[0:(len(buffer)-3)]))
    if head == 1:
        if localFH[0].data == b'':
            localFH[len(localFH)-1] = temp
        else:
            localFH.append(temp)
    elif head == 2:
        if centralFH[0].data == b'':
            centralFH[len(centralFH)-1] = temp
        else:
            centralFH.append(temp)
    buffer = buffer[(len(buffer)-3):len(buffer)]
    return buffer


# Separate zip file data into parts
def sep_chunk(filename, separator):
    try:
        with open(filename, mode="rb") as stream:
            buffer = bytearray(b'')
            while True:  # until EOF
                chunk = stream.read(4096)
                if not chunk:
                    break
                buffer += chunk
                while True:
                    try:
                        # Get the number of occurrences for each signature
                        occurLFH = buffer.count(bytearray(b'\x50\x4b\x03\x04'))
                        occurCFH = buffer.count(bytearray(b'\x50\x4b\x01\x02'))
                        occurEES = buffer.count(bytearray(b'\x50\x4b\x06\x06'))
                        occurES = buffer.count(bytearray(b'\x50\x4b\x05\x06'))
                        # If there are no occurrences of any signature found
                        # Add the information to the last part of the current section
                        if occurLFH == 0 and occurCFH == 0 and occurEES == 0 and occurES == 0:
                            if separator == bytearray(b'\x50\x4b\x03\x04'):
                                # Leave the last 3 bytes in case they hold the beginning of the next signature
                                localFH[len(localFH)-1].data += (buffer[0:(len(buffer)-3)])
                                buffer = buffer[(len(buffer)-3):len(buffer)]
                                break
                            elif separator == bytearray(b'\x50\x4b\x01\x02'):
                                # Leave the last 3 bytes in case they hold the beginning of the next signature
                                centralFH[len(centralFH)-1].data += (buffer[0:(len(buffer)-3)])
                                buffer = buffer[(len(buffer)-3):len(buffer)]
                                break
                            else:
                                endSignature.data += buffer
                                break
                        # If there is one occurrence of the LFH
                        elif occurLFH == 1:
                            part, buffer = buffer.split(separator, 1)
                            # Is the occurrence found at the beginning
                            if part == bytearray(b''):
                                # If there is a different signature/CFH signature found, split the data there.
                                # Otherwise add all the data to cfh or lfh
                                if occurCFH > 0:
                                    separator = bytearray(b'\x50\x4b\x01\x02')
                                    part, buffer = buffer.split(separator, 1)
                                    buffer = add_temp(b'\x50\x4b\x03\x04', b'\x50\x4b\x01\x02', buffer, part, 1)
                                else:
                                    buffer = break_add_temp(bytearray(b'\x50\x4b\x03\x04'), buffer, 1)
                                    break
                            else:
                                # No occurrence found at the beginning. Signature found further in.
                                # Split the data and add what is before the signature to the last lfh section
                                localFH[len(localFH)-1].data += part
                                buffer = bytearray(b'\x50\x4b\x03\x04') + buffer
                        # If there is more than one lfh signature found, split the data at the first occurrence
                        elif occurLFH > 1:
                            part, buffer = buffer.split(separator, 1)
                            # Does that data start with the signature
                            if part == bytearray(b''):
                                part, buffer = buffer.split(separator, 1)
                                buffer = add_temp(b'\x50\x4b\x03\x04', b'\x50\x4b\x03\x04', buffer, part, 1)
                            else:
                                localFH[len(localFH)-1].data += part
                                buffer = bytearray(b'\x50\x4b\x03\x04') + buffer
                        # No LFH, but a CFH signature was found
                        elif occurCFH == 1:
                            # Is there still some data left which belongs to LFH
                            if separator == bytearray(b'\x50\x4b\x03\x04'):
                                separator = bytearray(b'\x50\x4b\x01\x02')
                                part, buffer = buffer.split(separator, 1)
                                localFH[len(localFH)-1].data += part
                                buffer = bytearray(b'\x50\x4b\x01\x02') + buffer
                            else:
                                part, buffer = buffer.split(separator, 1)
                                # Does the data start with the CFH signature
                                if part == bytearray(b''):
                                    # Is there also a end signature
                                    if occurES > 0 or occurEES > 0:
                                        tempsig = b''
                                        if occurEES > 0:
                                            separator = bytearray(b'\x50\x4b\x06\x06')
                                            tempsig = b'\x50\x4b\x06\x06'
                                        else:
                                            separator = bytearray(b'\x50\x4b\x05\x06')
                                            tempsig = b'\x50\x4b\x05\x06'
                                        # Separate the data and end signature
                                        part, buffer = buffer.split(separator, 1)
                                        buffer = add_temp(b'\x50\x4b\x01\x02', tempsig, buffer, part, 2)
                                    else:
                                        buffer = break_add_temp(bytearray(b'\x50\x4b\x01\x02'), buffer, 2)
                                        break
                                else:
                                    # If it does not start with the signature
                                    # Split the data and add it to the latest cfh
                                    centralFH[len(centralFH)-1].data += part
                                    buffer = bytearray(b'\x50\x4b\x01\x02') + buffer
                        # If there is more than one CFH signature
                        elif occurCFH > 1:
                            # Is there still some data left which belongs to LFH
                            if separator == bytearray(b'\x50\x4b\x03\x04'):
                                separator = bytearray(b'\x50\x4b\x01\x02')
                                part, buffer = buffer.split(separator, 1)
                                localFH[len(localFH)-1].data += part
                                buffer = bytearray(b'\x50\x4b\x01\x02') + buffer
                            else:
                                part, buffer = buffer.split(separator, 1)
                                # Does the data start with the CFH signature
                                if part == bytearray(b''):
                                    part, buffer = buffer.split(separator, 1)
                                    buffer = add_temp(b'\x50\x4b\x01\x02', b'\x50\x4b\x01\x02', buffer, part, 2)
                                else:
                                    centralFH[len(centralFH)-1].data += part
                                    buffer = bytearray(b'\x50\x4b\x01\x02') + buffer
                        # Is there a EES signature
                        elif occurEES > 0:
                            # Set the separator to the EES signature if it is not already set
                            if separator == bytearray(b'\x50\x4b\x01\x02'):
                                separator = bytearray(b'\x50\x4b\x06\x06')
                                # If the ES signature is not here, read in more data
                                if occurES == 0:
                                    break
                            else:
                                part, buffer = buffer.split(separator, 1)
                                # Does the data start with he EES signature
                                if part == bytearray(b''):
                                    # If the ES signature is not here, read in more data
                                    if occurES == 0:
                                        break
                                    # Separate using the ES signature
                                    separator = bytearray(b'\x50\x4b\x05\x06')
                                    part, buffer = buffer.split(separator, 1)
                                    extraSignature.data += (bytearray(b'\x50\x4b\x06\x06') + part)
                                    buffer = bytearray(b'\x50\x4b\x05\x06') + buffer
                                else:
                                    # There is still some data left from CFH, add it into the last CFH
                                    centralFH[len(centralFH)-1].data += part
                                    buffer = bytearray(b'\x50\x4b\x06\x06') + buffer
                                    if occurES == 0:
                                        break
                        # Is there a ES signature
                        elif occurES > 0:
                            # Set the separator to the ES signature, if it is not already there
                            if separator == bytearray(b'\x50\x4b\x01\x02'):
                                separator = bytearray(b'\x50\x4b\x05\x06')
                            else:
                                part, buffer = buffer.split(separator, 1)
                                # Does the data start with the signature
                                if part == bytearray(b''):
                                    endSignature.data += (bytearray(b'\x50\x4b\x05\x06') + buffer)
                                    buffer = bytearray(b'')
                                else:
                                    # There is still some data left from CFH, separate and add it into the last CFH
                                    centralFH[len(centralFH)-1].data += part
                                    buffer = bytearray(b'\x50\x4b\x05\x06') + buffer
                    except ValueError:
                        break
    except IOError:
        print("Sorry. There is no such file", filename)
        stream.close()
#############################################################


# Main code
filename = input("Location of file: ")
separator = bytearray(b'\x50\x4b\x03\x04')
sep_chunk(filename, separator)
file_labels()

# Actions that can be done
action = input("What do you wish to do (for a list of actions, type -actions): ")
while action != "exit":
    if action == "-actions":
        print("rename\nremove\nadd\nexit")
    elif action == "rename":
        rename()
    elif action == "remove":
        remove()
    elif action == "add":
        add()
    action = input("\nWhat do you wish to do (for a list of actions, type -actions): ")

newFilename = input("\nWhat do you want to name the new zipped file (include .zip extension): ")
if newFilename[len(newFilename)-4:] != ".zip":
    newFilename += ".zip"
create_zip(newFilename)
print("\nWe are done here.")
