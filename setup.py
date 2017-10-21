from setuptools import setup


readme = open('README.rst').read()

setup(name='esper',
      version='0.9.9.1',
      author='Benjamin Moran',
      author_email='benmoran@protonmail.com',
      description="Esper is a lightweight Entity System for Python, with a focus on performance.",
      long_description=readme,
      license='MIT',
      keywords='ecs,entity component system,game',
      url='https://github.com/benmoran56/esper',
      download_url='https://github.com/benmoran56/esper/releases',
      platforms='POSIX, Windows, MacOS X',
      py_modules=['esper'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3 :: Only",
                   "Topic :: Games/Entertainment",
                   "Topic :: Software Development :: Libraries"])
