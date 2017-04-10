from setuptools import setup
from setuptools.command.install import install
from distutils import log # needed for outputting information messages
import os

class OverrideInstall(install):
    def run(self):
        uid, gid = 0, 0
        mode = 0o777
        install.run(self) # calling install.run(self) insures that everything that happened previously still happens, so the installation does not break!
        # here we start with doing our overriding and private magic ..
        for filepath in self.get_outputs():
            if 'previous.p' in filepath:
                log.info("Overriding setuptools mode of scripts ...")
                log.info("Changing ownership of %s to uid:%s gid %s" %
                         (filepath, uid, gid))
                os.chown(filepath, uid, gid)
                log.info("Changing permissions of %s to %s" %
                         (filepath, mode))
                os.chmod(filepath, mode)

setup(name='hue_plus',
      version='1.0.6',
      description='A utility to control the NZXT Hue+ in Linux',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux',
      ],
      url='http://github.com/kusti8/hue-plus',
      author='Gustav Hansen',
      author_email='kusti8@gmail.com',
      license='GPL3',
      packages=['hue_plus'],
      package_data = {'package': ["things/*"]},
      entry_points={
        'console_scripts': [
            'hue = hue_plus.hue:main'
        ],
        'gui_scripts': [
            'hue_ui = hue_plus.hue_ui:main'
        ]
      },
      install_requires=[
          'pyserial',
          'webcolors',
      ],
      extras_require={
        'GUI': ["PyQt5"],
        'Audio': ["pyaudio"],
      },
      include_package_data=True,
      zip_safe=False,
      cmdclass={'install': OverrideInstall})
