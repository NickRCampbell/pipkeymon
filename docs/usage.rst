Usage
=====

Setup in a local virtual environment:

.. code-block:: powershell

   cd C:\ControlerKeysMapper
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -e .

Run help:

.. code-block:: powershell

   pipkeymon --help
   python -m pipkeymon --help

Run the mapper:

.. code-block:: powershell

   pipkeymon run

Run debug mode:

.. code-block:: powershell

   pipkeymon run --debug
   python -m pipkeymon run --debug
