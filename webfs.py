# Copyright 2014 Harun Emektar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# http://fuse.sourceforge.net/wiki/index.php/FusePython
import fuse

#!/usr/bin/python

import fuse
import HTMLParser
import stat
import errno
import urllib2
import os
from time import time

fuse.fuse_python_api = (0, 2)

class WebDirParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self);
		self.path=""
		self.entries={}
		self._curTag=""
		self._entriesStarted = False
		self._lastFile = None
	def handle_starttag(self, tag, attr):
		self._curTag = tag
	def handle_endtag(self, tag):
		self._curTag = ""
		if tag == "pre":
			self._lastFile = None
	def handle_data(self, data):
		print "handle_data", data
		if self._curTag == "h1":
			self.path=data[len("Index of "):]
		elif self._curTag == "a" and data == "Parent Directory":
			self._entriesStarted = True
		elif self._curTag == "a" and self._entriesStarted:
			isDir = len(data.split("/")) > 1
			self.entries[ data.split("/")[0] ] = WebFSStat(isDir)
			self._lastFile = data.split("/")[0]
		elif self._entriesStarted and self._lastFile and not self.entries[self._lastFile].isDir():
			attr = data.strip().split()
			print attr
			if len(attr) == 3:
				size = attr[-1]
				isize = 0
				if size[-1] in "KMG":
					isize = float(size[0:-1])
					if size[-1] == "K":
						isize *= 1024
					elif size[-1] == "M":
						isize *= 1024 * 1024
					elif size[-1] == "G":
						isize *= 1024 * 1024 * 1024
					isize = int(isize)
				else:
					isize = int(size)
				self.entries[self._lastFile].st_size = isize

class WebFSStat(fuse.Stat):
	def __init__(self, isDir=True):
		if isDir:
			self.st_mode = stat.S_IFDIR | 0555
		else:
			self.st_mode = stat.S_IFREG | 0555
		self.st_ino = 0
		self.st_dev = 0
		self.st_nlink = 2
		self.st_uid = 0
		self.st_gid = 0
		self.st_size = 4096
		self.st_atime = int(time())
		self.st_mtime = self.st_atime
		self.st_ctime = self.st_atime
	def isDir(self):
		return self.st_mode & stat.S_IFDIR
class ResourceNotFound(Exception):
	pass

class WebFS(fuse.Fuse):
	def __init__(self, *args, **kw):
		fuse.Fuse.__init__(self, *args, **kw)
		self._rootURL = "http://old-releases.ubuntu.com/"
		self._rootDirs = ("releases", "ubuntu")
		self._latestDirEntries = {}

	def readdir(self, path, offset):
		print path, offset
		dirents = [ ".", ".."]
		if path == "/":
			dirents += self._rootDirs
		else:
			url = self._rootURL + path
			webDir = urllib2.urlopen(url)
			if webDir.getcode() != 200 and webDir.getcode() != 301:
				return -errno.ENOENT
			parser = WebDirParser()
			for line in webDir:
				parser.feed(line)
			dirents += parser.entries.keys()
			self._latestDirEntries[path] = parser.entries
		retEnt = []
		for r in dirents:
			retEnt += [ fuse.Direntry(r) ]
		return retEnt

	def read(self, path, size, offset):
		print "reading ", path
		request = urllib2.Request(self._rootURL + path, headers={"Range": "bytes=" + str(offset) + "-" + str(offset + size)})
		res = urllib2.urlopen(request)
		content = res.read(size)
		return content
	
	def _isDir(self, path):
		request = urllib2.Request(self._rootURL + path, headers={"Range": "bytes=0-0"})
		info = urllib2.urlopen(request)
		returnCode = info.getcode()
		print "return code for", path, returnCode
		if returnCode != 200 and returnCode != 301 and returnCode != 206:
			raise ResourceNotFound()
		contentType = info.info().getheaders("Content-Type")[0]
		print "content type of ", path, contentType
		retval = contentType.find("html") != -1
		try:
			self._latestDirEntries[os.path.dirname(path)][os.path.basename(path)] = WebFSStat(retval)
		except  KeyError:
			self._latestDirEntries[os.path.dirname(path)] = {os.path.basename(path) : WebFSStat(retval)}
		return retval

	def getattr(self, path):
		st = WebFSStat()
		if path == "/":
			return st
		if len(path.split("/")) == 2 and path.split("/")[1] not in self._rootDirs:
			print path, "doesnt exist"
			return -errno.ENOENT
		isDir = True;
		try:
			dirlist = self._latestDirEntries[os.path.dirname(path)]
			print "entry found",
			isDir = dirlist[os.path.basename(path)].isDir()
			st = dirlist[os.path.basename(path)]
			print "isDir ", str(isDir)
		except KeyError:
			# figure out type
			try:
				isDir = self._isDir(path)
			except ResourceNotFound:
				return -errno.ENOENT
		if not isDir:
			st.st_mode = stat.S_IFREG | 0555
		return st

	def chmod ( self, path, mode ):
		print '*** chmod', path, oct(mode)
		return 0

	def chown ( self, path, uid, gid ):
		print '*** chown', path, uid, gid
		return 0

	def fsync ( self, path, isFsyncFile ):
		print '*** fsync', path, isFsyncFile
		return 0

	def link ( self, targetPath, linkPath ):
		print '*** link', targetPath, linkPath
		return 0

	def mkdir ( self, path, mode ):
		print '*** mkdir', path, oct(mode)
		return 0

	def mknod ( self, path, mode, dev ):
		print '*** mknod', path, oct(mode), dev
		return 0

	def open ( self, path, flags ):
		if path == "/":
			return 0
		if len(path.split("/")) == 2 and path.split("/")[1] not in self._rootDirs:
			print path, "doesnt exist"
			return -errno.ENOENT
		isDir = True;
		try:
			dirlist = self._latestDirEntries[os.path.dirname(path)]
			print "entry found",
			isDir = dirlist[os.path.basename(path)].isDir()
			st = dirlist[os.path.basename(path)]
			print "isDir ", str(isDir)
		except KeyError:
			# figure out type
			try:
				isDir = self._isDir(path)
			except ResourceNotFound:
				return -errno.ENOENT
		if not isDir:
			st.st_mode = stat.S_IFREG | 0555
			request = urllib2.Request(self._rootURL + path, headers={"Range": "bytes=0-0"})
			info = urllib2.urlopen(request)
			rng = info.info().getheaders("Content-Range")[0]
			print "range::", rng
			rng = rng.split("/")[1]
			self._latestDirEntries[os.path.dirname(path)][os.path.basename(path)].st_size=int(rng)
		return 0

	def readlink ( self, path ):
		print '*** readlink', path
		return 0

	def release ( self, path, flags ):
		print '*** release', path, flags
		return 0

	def rename ( self, oldPath, newPath ):
		print '*** rename', oldPath, newPath
		return 0

	def rmdir ( self, path ):
		print '*** rmdir', path
		return 0

	def statfs ( self ):
		print '*** statfs'
		return 0

	def symlink ( self, targetPath, linkPath ):
		print '*** symlink', targetPath, linkPath
		return 0

	def truncate ( self, path, size ):
		print '*** truncate', path, size
		return 0

	def unlink ( self, path ):
		print '*** unlink', path
		return 0

	def utime ( self, path, times ):
		print '*** utime', path, times
		return 0

	def write ( self, path, buf, offset ):
		print '*** write', path, buf, offset
		return 0

def main():
	webFS = WebFS()
	webFS.parse(errex=1)
	webFS.main()

if __name__ == "__main__":
	main()
