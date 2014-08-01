# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with This file.  If not, see <http://www.gnu.org/licenses/>.

import sys

import zlib

import gst

def main(path):
    pipeline = gst.parse_launch('''
        filesrc location="%s" !
        decodebin ! audio/x-raw-int !
        appsink name=sink sync=False''' % path)
    sink = pipeline.get_by_name('sink')

    pipeline.set_state(gst.STATE_PLAYING)
    crc = 0

    while True:
        try:
            buf = sink.emit('pull-buffer')
        except SystemError, e:
            # it's probably a bug that emits triggers a SystemError
            print 'SystemError', e
            break

        # should be coming from a CD
        assert len(buf) % 4 == 0, "buffer is not a multiple of 4 bytes"
        crc = zlib.crc32(buf, crc)

    crc = crc % 2 ** 32
    print "CRC: %08X" % crc


path = 'test.flac'

try:
    path = sys.argv[1]
except IndexError:
    pass

main(path)
