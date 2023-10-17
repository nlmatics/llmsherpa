from setuptools import setup, find_packages

setup(
    name='llmsherpa',
    version='0.1.0',    
    description='Strategic APIs to Accelerate LLM Use Cases',
    url='https://github.com/nlmatics/llmsherpa',
    author='Ambika Sukla',
    author_email='ambika.sukla@nlmatics.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only'        
    ],
)