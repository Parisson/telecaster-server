AC_DEFUN([AM_PATH_MAD],
[
AC_ARG_WITH(mad-prefix,[  --with-mad-prefix=PFX   Prefix where libmad is installed (optional)],
            mad_prefix="$withval", mad_prefix="")
AC_ARG_ENABLE(madtest, [  --disable-madtest       Do not try to compile and run the libmad test program],
   , enable_madtest=yes)

  MAD_LIBS="-lmad"
  MAD_CFLAGS=""
  if test -n "$mad_prefix"; then
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$mad_prefix/lib"
    MAD_CFLAGS="-I$mad_prefix/include"
    MAD_LIBS="-L$mad_prefix/lib $MAD_LIBS"
  fi

  min_mad_version=ifelse([$1], , 0.12.0, $1)
  AC_MSG_CHECKING([for libmad (>= $min_mad_version)])
  if test -n "$enable_madtest"; then
    ac_save_CFLAGS="$CFLAGS"
    ac_save_LIBS="$LIBS"
    CFLAGS="$CFLAGS $MAD_CFLAGS"
    LIBS="$MAD_LIBS $LIBS"
dnl
dnl Now check if the installed madlib is sufficiently new. 
dnl
    AC_TRY_RUN([
#include <mad.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int 
main ()
{
  int major, minor, patch;
  char *tmp_version;

  tmp_version = strdup("$min_mad_version");
  if (sscanf(tmp_version, "%d.%d.%d", &major, &minor, &patch) != 3) {
     printf("%s, bad version string\n", "$min_mad_version");
     exit(1);
   }

   if (    (MAD_VERSION_MAJOR > major) 
       || ((MAD_VERSION_MAJOR == major) && (MAD_VERSION_MINOR > minor)) 
       || ((MAD_VERSION_MAJOR == major) && (MAD_VERSION_MINOR == minor) && (MAD_VERSION_PATCH >= patch)))
     {
       return 0;
     }
   else
     {
       printf("\n*** An old version of libmad (%s) was found.\n", MAD_VERSION);
       printf("*** This program requires at least version %s. The latest version of\n", "$min_mad_version");
       printf("*** libmad is always available from http://mad.sourceforge.net/\n");
     }
   return 1;
}
]
, dnl do nothing if TRY_RUN worked
, dnl define mad_failure if TRY_RUN failed
  mad_failure=yes
,
[
echo $ac_n "cross compiling; cannot test version... $ac_c"
          AC_TRY_LINK([#include <stdio.h>
                       #include <stdlib.h>
                       #include <mad.h>],
                      [ return MAD_VERSION_MAJOR; ],,
                      [ mad_failure=yes ]) 
])

    CFLAGS="$ac_save_CFLAGS"
    LIBS="$ac_save_LIBS"
  fi

  dnl
  dnl See is the program failed
  dnl
  if test "$mad_failure" = "yes"; then
     AC_MSG_RESULT(no)
     CFLAGS="$ac_save_CFLAGS"
     LIBS="$ac_save_LIBS"
     MAD_CFLAGS=""
     MAD_LIBS=""
     ifelse([$2], , :, [$2])
  else
     AC_MSG_RESULT(yes)
     AC_DEFINE(HAVE_MAD_H)
     AC_DEFINE(HAVE_LIBMAD)
	 use_mad="1"
     ifelse([$1], , :, [$1])
  fi

  AC_SUBST(MAD_CFLAGS)
  AC_SUBST(MAD_LIBS)
])

