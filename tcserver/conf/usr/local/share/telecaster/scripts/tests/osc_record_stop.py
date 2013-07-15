#!/usr/bin/env python
# -*- coding: utf-8 -*-

import liblo, sys

port = int(sys.argv[-1])

# send all messages to port 1234 on the local machine
try:
    target = liblo.Address(port)
except liblo.AddressError, err:
    print str(err)
    sys.exit()

# send message "/foo/message1" with int, float and string arguments
liblo.send(target, "/record", 0)
