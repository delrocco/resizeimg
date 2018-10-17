#!/usr/bin/python
# -*- coding: utf-8 -*-
#====================================================================
# @author: Joe Del Rocco
# @since: 10/25/2016
# @summary: A module with general useful functionality.
#====================================================================
import os
import shutil
import subprocess
import shlex
import re
import logging
from datetime import datetime
from threading import Timer


'''
Clamp a number to a range.
'''
def clamp(n, minval, maxval):
    return min(max(n, minval), maxval)

'''
Normalize a number between 0-1.
'''
def normalize(n, minval, maxval):
    return float(n-minval)/float(maxval-minval)

'''
Function to return the nth root of a radicand.
'''
def nthRoot(radicand, root):
    return radicand ** (1.0/root)

'''
Function that takes a RECT and ensures that it is forward facing (x,y in top left, width >= 0, height >= 0).
If the rect has been flipped so that either the width or height is negative, this function returns it unflipped.
:param rect: The rect as a list of numbers in order [x1, y1, x2, y2]
'''
def rectForwardFacing(rect):
    newrect = rect
    # rect is flipped horizontally and vertically
    if (rect[2] < rect[0] and rect[3] < rect[1]):
        newrect = [rect[2], rect[3], rect[0], rect[1]]
    # rect is flipped horizontally
    elif (rect[2] < rect[0]):
        newrect = [rect[2], rect[1], rect[0], rect[3]]
    # rect is flipped vertically
    elif (rect[3] < rect[1]):
        newrect = [rect[0], rect[3], rect[2], rect[1]]
    return newrect

'''
Use this for natural (human) sorting. Pass this as a key to a function that takes keys, such as sort.
:param s: The element that will be sorted
:param _nsre: Regular expression to find the digit portion of the element.
:author: https://stackoverflow.com/a/16090640/1002098
'''
RegexDigits = re.compile('([0-9]+)')
def naturalSortKey(s, _nsre=RegexDigits):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

'''
Use this to iterate over a sequence taking into account a step size.
:param seq: The sequence to iterate over.
:param step: The step size.
:author: https://stackoverflow.com/a/434328/1002098
'''
def chunker(seq, step):
    return (seq[pos:pos + step] for pos in range(0, len(seq), step))

'''
Verify that a string is a valid date or datetime
:param datestr: String that is to be verified.
:param datefmtstr: Format datetime string (e.g. "%Y-%m-%d")
'''
def verifyDateTime(datestr, datefmtstr):
    try:
        datetime.strptime(datestr, datefmtstr)
        return True
    except ValueError:
        return False

'''
Get the modification datetime from a file.
:param filepath: Path to file to get modification time from
'''
def fileModDateTime(filepath):
    t = os.path.getmtime(filepath)
    return datetime.fromtimestamp(t)

'''
Helper function that returns a list of all files, directories, or both, immediate or recursive.
:param mode: 0=both, 1=files, 2=dir
:param recursive: Immediate top-level list or recursive list
:param ext: List of file extensions to filter by
'''
def findFiles(dirpath, mode=0, recursive=False, ext=[]):
    stuff = []
    if len(ext) > 0:
        for i in range(0, len(ext)):
            ext[i] = ext[i].strip().lower()
            if ext[i][0] != ".":
                ext[i] = "." + ext[i]
    # immediate top-level list
    if not recursive:
        for entry in os.listdir(dirpath):
            fullpath = os.path.join(dirpath, entry)
            if mode == 1 or mode == 0:
                base, extension = os.path.splitext(fullpath.strip().lower())
                if os.path.isfile(fullpath):
                    if len(ext) > 0:
                        for e in ext:
                            if extension == e:
                                stuff.append(fullpath)
                    else:
                        stuff.append(fullpath)
            if mode == 2 or mode == 0:
                if os.path.isdir(fullpath):
                    stuff.append(fullpath)
    # recursive list
    else:
        for root, dirs, files in os.walk(dirpath):
            if mode == 1 or mode == 0:
                for file in files:
                    fullpath = os.path.join(root, file)
                    base, extension = os.path.splitext(fullpath.strip().lower())
                    if len(ext) > 0:
                        for e in ext:
                            if extension == e:
                                stuff.append(fullpath)
                    else:
                        stuff.append(fullpath)
            if mode == 2 or mode == 0:
                for dir in dirs:
                    fullpath = os.path.join(root, dir)
                    stuff.append(fullpath)
    return stuff

'''
Helper function delete all files and folders given a folder.
'''
def cleanFolder(dirpath):
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
            elif os.path.isdir(filepath):
                shutil.rmtree(filepath)
        except Exception as ex:
            logging.error(ex.message)

'''
Helper function to copy a single file or filetree from one location to another.
'''
def copy(src, dest):
    try:
        if os.path.isfile(src):
            shutil.copy(src, dest)
        else:
            for filename in os.listdir(src):
                srcfile = os.path.join(src, filename)
                destfile = os.path.join(dest, filename)
                if os.path.isfile(srcfile):
                    shutil.copy(srcfile, destfile)
                else:
                    shutil.copytree(srcfile, destfile)
    except Exception as ex:
        logging.error(ex.message)

'''
Helper function to kill a process.
'''
def killProcess(process, timeout):
    timeout["value"] = True
    process.kill()

'''
Helper function to run a shell command with timeout support.
'''
def runCMD(cmd, timeout_sec):
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeout = {"value": False}
    timer = Timer(timeout_sec, killProcess, [process, timeout])
    timer.start()
    stdout, stderr = process.communicate()
    timer.cancel()
    return process.returncode, stdout, stderr, timeout["value"]
