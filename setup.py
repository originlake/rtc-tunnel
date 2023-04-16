from setuptools import setup, find_packages, Extension

setup(
    name="rtc_tunnel",
    python_requires='>=3.7.0',
    version = '0.1.0',
    packages=find_packages(include = ['rtc_tunnel', 'rtc_tunnel.*', 'rtc_tunnel.bin.*']),
    description="WebRTC tunnel via peerjs server",
    url="https://github.com/originlake/rtc-tunnel",
    install_requires=[
        "aiortc>=1.5.0",
        "websockets"
    ],
    entry_points={
        'console_scripts': [
            'rtc_server = rtc_tunnel.bin:server',
            'rtc_client = rtc_tunnel.bin:client'
        ]
    }
)
