# Copyright (c) 2015, Thomas Chiroux - Link Care Services
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of cairotft nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""setuptools installer for cairotft."""

import os
import uuid

from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py

# local imports
try:
    from build_scripts.version import get_git_version
except:
    pass

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.rst')).read()

version = None
try:
    version = get_git_version()
except:
    pass

if version is None or not version:
    try:
        file_name = "cairotft/RELEASE-VERSION"
        version_file = open(file_name, "r")
        try:
            version = version_file.readlines()[0]
            version = version.strip()
        except Exception:
            version = "0.0.0"
        finally:
            version_file.close()
    except IOError:
        version = "0.0.0"


class my_build_py(build_py):
    def run(self):
        # honor the --dry-run flag
        if not self.dry_run:
            target_dirs = []
            target_dirs.append(os.path.join(self.build_lib,
                                            'cairotft'))
            target_dirs.append('cairotft')
            # mkpath is a distutils helper to create directories
            for dir in target_dirs:
                self.mkpath(dir)

            try:
                for dir in target_dirs:
                    fobj = open(os.path.join(dir, 'RELEASE-VERSION'), 'w')
                    fobj.write(version)
                    fobj.close()
            except:
                pass

        # distutils uses old-style classes, so no super()
        build_py.run(self)

dev_reqs_gen = parse_requirements("dev-requirements.txt",
                                  session=uuid.uuid1())
reqs_gen = parse_requirements("requirements.txt",
                              session=uuid.uuid1())

setup(name='cairotft',
      version=version,
      description="UI library for small tft screens using cairocffi",
      long_description=README + '\n\n' + NEWS,
      cmdclass={'build_py': my_build_py},
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.4",
          "Topic :: Multimedia :: Graphics",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces", ],
      keywords='cairo framebuffer tft python',
      author='Thomas Chiroux - Link Care Services',
      author_email='tchiroux (at) linkcareservices.org',
      url='https://github.com/LinkCareServices/cairotft',
      license='BSD 3-Clause',
      packages=find_packages(exclude=['ez_setup']),
      package_data={'': ['*.rst', ], },
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=[str(ir.req) for ir in dev_reqs_gen],
      install_requires=[str(ir.req) for ir in reqs_gen], )
