from setuptools import find_packages, setup

setup(
    name='crail',
    version='0.0.1',
    description='Crayon rails online helper',
    url='https://github.com/dmaze/crail',
    author='David Maze',
    author_email='dzmaze@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.4',
    ],
    keywords=[],
    packages=find_packages(),
    install_requires=[
        'cssmin',
        'flask',
        'flask-assets',
        # This uses Alembic as its migration engine
        'flask-migrate',
        'flask-script',
        'flask-seasurf',
        'flask-sqlalchemy',
        'PyYAML',
    ],
    package_data={
        'crail.static': [('*/') * depth + '*.' + suffix
                         for depth in range(5)
                         for suffix in ['js', 'css']],
        'crail.templates': ['*.html'],
    },
    entry_points={
        'console_scripts': [
            'crail_manage = crail.manage:main',
        ],
    },
)
