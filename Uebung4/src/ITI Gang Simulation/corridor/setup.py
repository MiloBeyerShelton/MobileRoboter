import os
from glob import glob
from setuptools import setup

package_name = 'corridor'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'),
         glob('worlds/*.world')),
        (os.path.join('share', package_name, 'models', 'itiGang'),
         glob('models/itiGang/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Tanja Kaiser',
    maintainer_email='Tanja.Kasier@uni-luebeck.de',
    description='TODO: Package description',
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'TestNode = corridor.TestNode:main',
            'add_bot_node = corridor.add_bot_node:main'
        ],
    },
)
