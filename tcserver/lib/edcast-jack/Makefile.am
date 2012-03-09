## Process this file with automake to produce Makefile.in
 
AUTOMAKE_OPTIONS = foreign dist-zip

SUBDIRS = libedcast 
 
bin_PROGRAMS = edcast_jack

edcast_jack_SOURCES = edcast.cpp 

edcast_jack_LDADD = libedcast/libedcast.a

EXTRA_DIST = conf

LIBS = @LIBS@ @OGG_LIBS@ @VORBIS_LIBS@ @MAD_LIBS@ @LAME_LIBS@ @VORBISENC_LIBS@ @VORBISFILE_LIBS@ @FAAC_LIBS@ @LIBFLAC_LIBS@ @JACK_LIBS@
CFLAGS = -g @CFLAGS@ @OGG_CFLAGS@ @VORBIS_CFLAGS@ @MAD_CFLAGS@ @LAME_CFLAGS@ @FAAC_CFLAGS@ @LIBFLAC_CFLAGS@

