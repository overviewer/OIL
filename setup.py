#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext
from distutils.command.clean import clean
from distutils import log

import os.path

class CustomBuildExt(build_ext):
    user_options = build_ext.user_options + [
        ('with-sse', None, "build with SSE CPU backend"),
        ('with-opengl', None, "build with OpenGL GPU backend"),
    ]
    
    def initialize_options(self):
        self.with_sse = False
        self.with_opengl = False
        build_ext.initialize_options(self)
    
    def build_extensions(self):
        c = self.compiler.compiler_type
        if c == "msvc":
            # customize the build options for this compilier
            for e in self.extensions:
                e.extra_link_args.append("/MANIFEST")
        if c == "unix":
            # customize the build options for this compilier
            for e in self.extensions:
                e.extra_compile_args.append("-ffast-math")
                e.extra_compile_args.append("-O2")
                e.extra_compile_args.append("-Wdeclaration-after-statement")
                e.extra_compile_args.append("-Wall")
                e.extra_compile_args.append("-Werror")
        
        for e in self.extensions:
            if self.with_sse:
                e.define_macros.append(("ENABLE_CPU_SSE_BACKEND", None))
            if self.with_opengl:
                e.define_macros.append(("ENABLE_OPENGL_BACKEND", None))
                e.libraries.append("X11")
                e.libraries.append("GL")
                e.libraries.append("GLEW")
        
        # build in place, and in the build/ tree
        self.inplace = False
        build_ext.build_extensions(self)
        self.inplace = True
        build_ext.build_extensions(self)

class CustomClean(clean):
    def run(self):
        # do the normal cleanup
        clean.run(self)

        # try to remove 'OIL.{so,pyd,...}' extension,
        # regardless of the current system's extension name convention
        build_ext = self.get_finalized_command('build_ext')
        fname = build_ext.get_ext_filename('OIL')
        if os.path.exists(fname):
            try:
                log.info("removing '%s'", fname)
                if not self.dry_run:
                    os.remove(fname)
                    
            except OSError:
                log.warn("'%s' could not be cleaned -- permission denied",
                         fname)
        else:
            log.debug("'%s' does not exist -- can't clean it",
                      fname)

#
# STILL TODO: verify libpng is present
#

oil_headers = [
    "oil.h",
    "oil-python.h",
    "oil-dither-private.h",
    "oil-format-private.h",
    "oil-image-private.h",
    "oil-palette-private.h",
    "oil-backend-private.h",
    "oil-backend-cpu.def",
]

oil_sources = [
    "oil-python.c",
    "oil-matrix.c",
    "oil-image.c",
    "oil-format.c",
    "oil-format-png.c",
    "oil-palette.c",
    "oil-dither.c",
    "oil-backend.c",
    "oil-backend-cpu.c",
    "oil-backend-debug.c",
    "oil-backend-cpu-sse.c",
    "oil-backend-opengl.c",
]

setup(name='OIL',
      version='0.0-git',
      cmdclass={'build_ext' : CustomBuildExt, 'clean' : CustomClean},
      ext_modules=[Extension('OIL', oil_sources, depends=oil_headers, libraries=['png'])],
)
