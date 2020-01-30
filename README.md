# pic-sure-python-client
Research users may use PIC-SURE API Base Client Library to connect to a PIC-SURE API and list resource instances and their metadata. 

All operations on PIC-SURE rely upon two component libraries: The Connection Library, and a Datasource Adapter Library. The connection library manages network communication and authentication. It also provides basic functionality for PIC-SURE Resource Libraries to perform low level interactions with Resource Implementations. 
## Installation
To use the Python Connector Library, first install a pip package in the current Jupyter kernel:

```python
import sys
pip install --upgrade pip
pip install git+https://github.com/hms-dbmi/pic-sure-python-client.git    
pip install git+https://github.com/hms-dbmi/pic-sure-python-adapter-hpds.git
pip install pandas
pip install matplotlib
```
## Usage
To connect to a PIC-SURE endpoint, first 

```python
import PicSureClient
client = PicSureClient.Client()
client.help()
```
## Supported Python Versions
TBD
## Additional Resources
* [PIC-SURE HPDS Python Client](https://github.com/hms-dbmi/pic-sure-python-adapter-hpds "PIC-SURE HPDS Python Client")
