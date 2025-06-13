from setuptools import setup, find_packages

setup(
    name="audio_dashboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.32.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "pydub>=0.25.1",
        "ffmpeg-python>=0.2.0",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "audio-dashboard=app.main:main",
        ],
    },
)
