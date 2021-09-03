from setuptools import setup


with open('esper.py') as f:
    info = {}
    for line in f.readlines():
        if line.startswith('version'):
            exec(line, info)
            break

README = open('README.rst').read()

setup(name='esper',
      version=info['version'],
      author='Benjamin Moran',
      author_email='benmoran@protonmail.com',
      description="esper is a lightweight Entity System (ECS) for Python, with a focus on performance.",
      long_description=README,
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
