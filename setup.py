from setuptools import setup
from setuptools.command.install import install
from distutils import log # needed for outputting information messages
import os

setup(name='hue_plus',
      version='1.4.5',
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
          'pyqt5',
          'pyaudio',
          'appdirs'
      ],
      keywords = 'nzxt hue hue-plus hue_plus hue+',
      include_package_data=True,
      zip_safe=False)
