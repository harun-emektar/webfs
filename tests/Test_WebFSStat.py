
from webfs import WebFSStat
import stat

def Test_Basic():
    fields = ('st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid', 'st_gid',
              'st_size', 'st_atime', 'st_mtime', 'st_ctime')
    st = WebFSStat()
    print st.__dict__.keys()
    for field in fields:
        assert field in st.__dict__.keys(), 'field(%s) is not in members' % field
        
def Test_InitParam():
    st = WebFSStat()
    assert st.st_mode == stat.S_IFDIR | 0555
    
    st = WebFSStat(False)
    assert st.st_mode == stat.S_IFREG | 0444
    
def Test_IsDir():
    st = WebFSStat()
    assert st.isDir()
    
    st = WebFSStat(False)
    assert not st.isDir()
    