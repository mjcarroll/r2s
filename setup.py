from setuptools import find_packages
from setuptools import setup

package_name = 'r2s'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=[''],
    zip_safe=True,
    author='Michael Carroll, Jenn Nguyen',
    author_email='mjcarroll@intrinsic.ai, jennuine@intrinsic.ai',
    maintainer='Michael Carroll, Jenn Nguyen',
    maintainer_email='mjcarroll@intrinsic.ai, jennuine@intrinsic.ai',
    url='https://github.com/ros2/r2s',
    download_url='https://github.com/ros2/r2s/releases',
    keywords=[],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    description='Terminal User Interface for ROS 2 command line tools.',
    long_description="""\
Terminal User Interface for ROS 2 command line tools.""",
    license='Apache License, Version 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'r2s = r2s.cli:main'
        ]
    }
)
