# Configure paths for libvorbis
# Jack Moffitt <jack@icecast.org> 10-21-2000
# updated by Karl Heyes 31-Mar-2003
# Shamelessly stolen from Owen Taylor and Manish Singh

dnl XIPH_PATH_VORBIS([ACTION-IF-FOUND [, ACTION-IF-NOT-FOUND]])
dnl Test for libvorbis, and define VORBIS_CFLAGS VORBIS_LIBS
dnl VORBIS_VORBISENC_LIBS VORBIS_VORBISFILE_LIBS VORBIS_LDFLAGS
dnl

AC_DEFUN([XIPH_PATH_VORBIS],
[dnl
AC_REQUIRE([XIPH_PATH_OGG])

dnl Get the cflags and libraries for vorbis
dnl
AC_ARG_VAR([VORBIS_PREFIX],[path to vorbis installation])
AC_ARG_WITH(vorbis,
    AC_HELP_STRING([--with-vorbis=PREFIX],
        [Prefix where libvorbis is installed (optional)]),
    vorbis_prefix="$withval",
    vorbis_prefix="$VORBIS_PREFIX"
    )
if test "x$vorbis_prefix" = "x" -o "x$vorbis_prefix" = "xyes"; then
    if test "x$prefix" = "xNONE"; then
        vorbis_prefix="/usr/local"
    else
        vorbis_prefix="$prefix"
    fi
fi

VORBIS_CFLAGS="$OGG_CFLAGS"
VORBIS_LDFLAGS="$OGG_LDFLAGS"

VORBIS_LIBS="-lvorbis"
VORBISFILE_LIBS="-lvorbisfile"
VORBISENC_LIBS="-lvorbisenc"

xt_save_LIBS="$LIBS"
xt_save_LDFLAGS="$LDFLAGS"
xt_save_CPPFLAGS="$CPPFLAGS"
CPPFLAGS="$CPPFLAGS $VORBIS_CFLAGS"
LDFLAGS="$LDFLAGS $VORBIS_LDFLAGS"
LIBS="$LIBS $VORBIS_LIBS"
xt_lib_vorbis="not found"
AC_MSG_CHECKING([for libvorbis])
AC_TRY_LINK_FUNC(ogg_stream_init, [xt_lib_vorbis=ok],
        [LIBS="$LIBS $OGG_LIBS -lm"
        AC_TRY_LINK_FUNC(vorbis_info_init,
            [xt_lib_vorbis=ok
            VORBIS_LIBS="$VORBIS_LIBS $OGG_LIBS -lm"],
            )
        ])

AC_MSG_RESULT([$xt_lib_vorbis])
if test "x$xt_lib_vorbis" = "xok"; then
#
# Now check if the installed Vorbis is sufficiently new.
#
AC_CHECK_TYPES([struct ovectl_ratemanage_arg],,
        [xt_lib_vorbis="old version found"], [
#include <vorbis/codec.h>
#include <vorbis/vorbisenc.h>
        ])
fi
CPPFLAGS="$xt_save_CPPFLAGS"
LIBS="$xt_save_LIBS"
LDFLAGS="$xt_save_LDFLAGS"

if test "x$xt_lib_vorbis" = "xok"; then
	AC_DEFINE([HAVE_VORBIS], [1], [Define if you have libvorbis installed])
    use_vorbis="1"
    ifelse([$1], ,[:], [$1])
else
    VORBIS_CFLAGS=""
    VORBIS_LDFLAGS=""
    VORBIS_LIBS=""
    VORBISFILE_LIBS=""
    VORBISENC_LIBS=""
    ifelse([$2], ,, [$2])
fi
AC_SUBST(VORBIS_CFLAGS)
AC_SUBST(VORBIS_LDFLAGS)
AC_SUBST(VORBIS_LIBS)
AC_SUBST(VORBISFILE_LIBS)
AC_SUBST(VORBISENC_LIBS)
])
