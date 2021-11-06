import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EPViz",
    version="0.0.1",
    description="An open source EEG Visualization software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jcraley/epviz",
    project_urls={
        "Bug Tracker": "https://github.com/jcraley/epviz/issues",
        "Documentation": "https://engineering.jhu.edu/nsa/links/epviz/",
    },
    package_data={'visualization.ui_files': ['gui_stylesheet.css',]},
    packages=["visualization", "visualization.signal_loading", "visualization.edf_saving", "visualization.filtering", "visualization.image_saving", "visualization.models", "visualization.predictions", "visualization.preprocessing", "visualization.signal_stats", "visualization.spectrogram_window",],
    entry_points={
        'console_scripts': ['epviz=visualization.plot:main', ]
    },
)
