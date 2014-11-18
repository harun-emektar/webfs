from webfs import WebDirParser

testDoc = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /ubuntu</title>
 </head>
 <body>
<h1>Index of /ubuntu</h1>
<pre><img src="/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                    <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/icons/back.gif" alt="[DIR]"> <a href="/">Parent Directory</a>                             -   
<img src="/icons/folder.gif" alt="[DIR]"> <a href="dists/">dists/</a>                  18-Jun-2014 12:46    -   
<img src="/icons/folder.gif" alt="[DIR]"> <a href="indices/">indices/</a>                28-Apr-2008 17:47    -   
<img src="/icons/compressed.gif" alt="[   ]"> <a href="ls-lR.gz">ls-lR.gz</a>                28-Apr-2008 16:05  4.5M  
<img src="/icons/folder.gif" alt="[DIR]"> <a href="pool/">pool/</a>                   14-Jan-2008 22:05    -   
<img src="/icons/folder.gif" alt="[DIR]"> <a href="project/">project/</a>                28-Jun-2013 11:52    -   
<hr></pre>
<address>Apache/2.2.22 (Ubuntu) Server at old-releases.ubuntu.com Port 80</address>
</body></html>
"""

def Test_ParsingTest():
    wp = WebDirParser()
    wp.feed(testDoc)
    assert len(wp.entries) == 5
    assert wp.entries.keys().sort() == ['dist', 'indices', 'ls-lR.gz', 'pool', 'project'].sort(),\
        wp.entries.keys()