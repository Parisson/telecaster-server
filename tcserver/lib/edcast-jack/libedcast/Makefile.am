AUTOMAKE_OPTIONS = foreign 1.6

lib_LIBRARIES = libedcast.a
#libedcast_la_LDFLAGS = -version-info 3:0:0

include_HEADERS = libedcast.h libedcast_resample.h libedcast_socket.h
libedcast_a_SOURCES = libedcast.cpp \
						resample.c \
						cbuffer.c \
						Socket.cpp

EXTRA_DIST = \
				cbuffer.h \
				enc_if.h \
				libedcast.dsp \
				libedcast.h \
				libedcast_resample.h \
				libedcast_socket.h

LIBS = @LIBS@ @OGG_LIBS@ @VORBIS_LIBS@ @MAD_LIBS@ @LAME_LIBS@ @VORBISENC_LIBS@ @VORBISFILE_LIBS@ @FAAC_LIBS@ @LIBFLAC_LIBS@
CFLAGS = -g @CFLAGS@ @OGG_CFLAGS@ @VORBIS_CFLAGS@ @MAD_CFLAGS@ @LAME_CFLAGS@ @FAAC_CFLAGS@ @LIBFLAC_CFLAGS@
