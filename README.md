# Installing NGEC, my steps:

Note for self: if I want to check the dependency trees (dependencies of a specific package version), use:
- `pip install pipgrip`
- `pipgrip sentence-transformers==3.0.0 --tree`

The symbol ❖ in this document signifies a new step.

## Start by following the 'Quick Start' on Github:
> Requirements.txt is outdated. For example, the latest version of NGEC is made for Spacy 3.7, while the file refers to 3.2.3. Do not use that file.


❖ ✅ Creating Conda environment = a closed python environment:
- `conda create -y --name ngec3 python=3.10`
- `conda activate ngec3`


❖ ❌ **WAIT!** The guide says to use `pip install spacy, textacy sentence-transformers`, but there are issues:
- the comma should not be there
- NGEC and mordecai3 were built for Spacy 3.7.x, so we use 3.7.5
- package `sentence-transformers` would install a version of transformers which is incompatible with `spacy-transformers`
- ✅ Solution: `pip install spacy==3.7.5 textacy sentence-transformers==3.0.1`

`pip list` checkpoint:
```
Package               Version
--------------------- ----------
annotated-types       0.7.0
blis                  0.7.11
cachetools            5.5.0
catalogue             2.0.10
certifi               2024.12.14
charset-normalizer    3.4.0
click                 8.1.7
cloudpathlib          0.20.0
confection            0.1.5
cymem                 2.0.10
cytoolz               1.0.1
filelock              3.16.1
floret                0.10.5
fsspec                2024.10.0
huggingface-hub       0.27.0
idna                  3.10
jellyfish             1.1.3
Jinja2                3.1.4
joblib                1.4.2
langcodes             3.5.0
language_data         1.3.0
marisa-trie           1.2.1
markdown-it-py        3.0.0
MarkupSafe            3.0.2
mdurl                 0.1.2
mpmath                1.3.0
murmurhash            1.0.11
networkx              3.4.2
numpy                 1.26.4
packaging             24.2
pillow                11.0.0
pip                   24.2
preshed               3.0.9
pydantic              2.10.3
pydantic_core         2.27.1
Pygments              2.18.0
pyphen                0.17.0
PyYAML                6.0.2
regex                 2024.11.6
requests              2.32.3
rich                  13.9.4
safetensors           0.4.5
scikit-learn          1.6.0
scipy                 1.14.1
sentence-transformers 3.0.1
setuptools            75.1.0
shellingham           1.5.4
smart-open            7.1.0
spacy                 3.7.5
spacy-legacy          3.0.12
spacy-loggers         1.0.5
srsly                 2.5.0
sympy                 1.13.1
textacy               0.13.0
thinc                 8.2.5
threadpoolctl         3.5.0
tokenizers            0.21.0
toolz                 1.0.0
torch                 2.5.1
tqdm                  4.67.1
transformers          4.47.1
typer                 0.15.1
typing_extensions     4.12.2
urllib3               2.2.3
wasabi                1.1.3
weasel                0.4.1
wheel                 0.44.0
wrapt                 1.17.0
```

❖ ✅ Install the Spacy transformer pipeline 'en_core_web_trf'
- This is smart and installs the version which is compatible with the spacy version we are using.
- `python -m spacy download en_core_web_trf`

Output checkpoint:
```
Successfully installed curated-tokenizers-0.0.9 curated-transformers-0.1.1 en-core-web-trf-3.7.3 spacy-curated-transformers-0.2.2
```
❗️ (19/12) WAIT! Some NGEC files also refer to models called `en_core_web_lg` and `en_core_web_sm`. Should we install those too? Idk...
- `python -m spacy download en_core_web_lg`
- `python -m spacy download en_core_web_sm`


❖ ✅ Install Elasticsearch, which will be used for an offline Wikipedia and Geonames server:
- `pip install elasticsearch elasticsearch_dsl unidecode dateparser`


Output checkpoint:
```
Successfully installed dateparser-1.2.0 elastic-transport-8.15.1 elasticsearch-8.17.0 elasticsearch\_dsl-8.17.0 python-dateutil-2.9.0.post0 pytz-2024.2 six-1.17.0 tzlocal-5.2 unidecode-1.3.8
```


❖ ✅ Other packages:
- `pip install jsonlines tqdm datasets rich plac`

Output checkpoint:
> Note: It downgraded fsspec because datasets needs version 2024.9.0 or lower, but that's fine
```
  Attempting uninstall: fsspec
    Found existing installation: fsspec 2024.10.0
    Uninstalling fsspec-2024.10.0:
      Successfully uninstalled fsspec-2024.10.0
Successfully installed aiohappyeyeballs-2.4.4 aiohttp-3.11.10 aiosignal-1.3.2 async-timeout-5.0.1 attrs-24.3.0 datasets-3.2.0 dill-0.3.8 frozenlist-1.5.0 fsspec-2024.9.0 jsonlines-4.0.0 multidict-6.1.0 multiprocess-0.70.16 pandas-2.2.3 plac-1.4.3 propcache-0.2.1 pyarrow-18.1.0 tzdata-2024.2 xxhash-3.5.0 yarl-1.18.3
```


❖ ❌ Now install the package mordecai3:
- **WAIT!** Do not use `pip install mordecai3`
- `mordecai3` has some severe inconsistencies in the code, specifically in `setup.py`. Parts of the code were updated but others were not, causing serious issues.
- The code also tries to use a Spacy transformer model incompatible with the Spacy version the package was made for 🤦‍♂️


**My solution:** Cloned the package and fixed the issues
- My version of the package is uploaded on `https://github.com/davepivonka/mordecai3`  - only changed the `setup.py` file
- Updated the packages to match the versions in requirements.txt
- Updated the `en_core_web_trf` to version 3.7.3, supporting Spacy 3.7.x versions
- In `setup.py -> package_data` one of the linked assets was `'assets/mordecai_2023-03-28.pt'` BUT the files contain a newer version `mordecai_2024-06-04.pt` so I updated it

❗️ (19/12) Other files:
- `mordecai_streamlit`: Change the models to the newest one (`mordecai_2024-06-04.pt`)


✅ **Install these before my mordecai3:**
`pip install --force-reinstall elasticsearch==7.17.9 elasticsearch-dsl==7.4.1 pandas==1.5.3 numpy==1.26.4 jsonlines==3.1.0 xmltodict==0.14.2`

`pip install --force-reinstall elasticsearch==7.10.1 elasticsearch-dsl==7.4.1 pandas==1.5.3 numpy==1.26.4 jsonlines==3.1.0 xmltodict==0.14.2`

Output checkpoint:
```
Successfully installed attrs-24.3.0 certifi-2024.12.14 elasticsearch-7.17.9 elasticsearch-dsl-7.4.1 jsonlines-3.1.0 numpy-1.26.4 pandas-1.5.3 python-dateutil-2.9.0.post0 pytz-2024.2 six-1.17.0 urllib3-1.26.20 xmltodict-0.14.2
```

`pip list` checkpoint:
```
Package                    Version
-------------------------- -----------
aiohappyeyeballs           2.4.4
aiohttp                    3.11.10
aiosignal                  1.3.2
annotated-types            0.7.0
async-timeout              5.0.1
attrs                      24.3.0
blis                       0.7.11
cachetools                 5.5.0
catalogue                  2.0.10
certifi                    2024.12.14
charset-normalizer         3.4.0
click                      8.1.7
cloudpathlib               0.20.0
confection                 0.1.5
curated-tokenizers         0.0.9
curated-transformers       0.1.1
cymem                      2.0.10
cytoolz                    1.0.1
datasets                   3.2.0
dateparser                 1.2.0
dill                       0.3.8
elastic-transport          8.15.1
elasticsearch              7.17.9
elasticsearch-dsl          7.4.1
en-core-web-trf            3.7.3
filelock                   3.16.1
floret                     0.10.5
frozenlist                 1.5.0
fsspec                     2024.9.0
huggingface-hub            0.27.0
idna                       3.10
jellyfish                  1.1.3
Jinja2                     3.1.4
joblib                     1.4.2
jsonlines                  3.1.0
langcodes                  3.5.0
language_data              1.3.0
marisa-trie                1.2.1
markdown-it-py             3.0.0
MarkupSafe                 3.0.2
mdurl                      0.1.2
mpmath                     1.3.0
multidict                  6.1.0
multiprocess               0.70.16
murmurhash                 1.0.11
networkx                   3.4.2
numpy                      1.26.4
packaging                  24.2
pandas                     1.5.3
pillow                     11.0.0
pip                        24.2
plac                       1.4.3
preshed                    3.0.9
propcache                  0.2.1
pyarrow                    18.1.0
pydantic                   2.10.3
pydantic_core              2.27.1
Pygments                   2.18.0
pyphen                     0.17.0
python-dateutil            2.9.0.post0
pytz                       2024.2
PyYAML                     6.0.2
regex                      2024.11.6
requests                   2.32.3
rich                       13.9.4
safetensors                0.4.5
scikit-learn               1.6.0
scipy                      1.14.1
sentence-transformers      3.0.1
setuptools                 75.1.0
shellingham                1.5.4
six                        1.17.0
smart-open                 7.1.0
spacy                      3.7.5
spacy-curated-transformers 0.2.2
spacy-legacy               3.0.12
spacy-loggers              1.0.5
srsly                      2.5.0
sympy                      1.13.1
textacy                    0.13.0
thinc                      8.2.5
threadpoolctl              3.5.0
tokenizers                 0.21.0
toolz                      1.0.0
torch                      2.5.1
tqdm                       4.67.1
transformers               4.47.1
typer                      0.15.1
typing_extensions          4.12.2
tzdata                     2024.2
tzlocal                    5.2
Unidecode                  1.3.8
urllib3                    1.26.20
wasabi                     1.1.3
weasel                     0.4.1
wheel                      0.44.0
wrapt                      1.17.0
xmltodict                  0.14.2
xxhash                     3.5.0
yarl                       1.18.3
```


❖ ✅ **Install my version of mordecai3:**
- Run `pip install git+https://github.com/davepivonka/mordecai3.git`

Output checkpoint:
```
(...)
  Attempting uninstall: tokenizers
    Found existing installation: tokenizers 0.21.0
    Uninstalling tokenizers-0.21.0:
      Successfully uninstalled tokenizers-0.21.0
  Attempting uninstall: transformers
    Found existing installation: transformers 4.47.1
    Uninstalling transformers-4.47.1:
      Successfully uninstalled transformers-4.47.1
Successfully installed mordecai3-3.0.0b0 spacy-alignments-0.9.1 spacy-transformers-1.3.5 tokenizers-0.15.2 transformers-4.36.2
```


❖ **Offline Wikipedia and Geonames index:**
> Note: We can easily update the index and update it, the code is publicly available. But let's use the pre-built 2023 version for now:
 
❖ ✅ Now, download the pre-built offline Geonames and Wikipedia index from `https://andrewhalterman.com/files/geonames_wiki_index_2023-03-02.tar.gz` 
or run `wget https://andrewhalterman.com/files/geonames_wiki_index_2023-03-02.tar.gz` 

❖ ✅ Uncompress the file somewhere. 
- Either manually, or run `tar -xvzf geonames_wiki_index_2023-03-02.tar.gz`

❖ ✅ Download and install Docker (`https://www.docker.com/`)

❖ ✅ Run docker - don't need to do anything, just open the app
20241219133919
❖ ✅ You may need to set write permissions for Docker to run:
- `chmod -R 777 ./geonames_index/` where you replace `./geonames_index/` with the location of the "geonames_index" folder (might not even need to change it)
- My code: `chmod -R 777 '/Users/davidpivonka/Documents/Peacekeeping Dividends/geonames_index'`

❖ ✅ Now, start an Elasticsearch instance in Docker with the uncompressed index as a volume.
- Update the code to match your `geonames_index` folder location
- NGEC authors say that it was tested for 7.10.1, but hopefully this works
- `sudo docker run -d -p 127.0.0.1:9200:9200 -e "discovery.type=single-node" -v '/Users/davidpivonka/Documents/Peacekeeping Dividends/geonames_index':/usr/share/elasticsearch/data elasticsearch:7.17.9`
- Without my specific location (might work without change if you used the commands `wget` and `tar` to get the geonames index folder): `sudo docker run -d -p 127.0.0.1:9200:9200 -e "discovery.type=single-node" -v ./geonames_index/:/usr/share/elasticsearch/data elasticsearch:7.17.9`



❖ ✅ **Install NGEC**
- Download the NGEC repository from Github: `https://github.com/ahalterman/NGEC`


❖ ✅ Now, install it using:
- `pip install -e .` where the `.` is replaced with the location of the NGEC folder. In my case:
- `pip install -e '/Users/davidpivonka/Documents/Peacekeeping Dividends/Github Repo/NGEC'`

Output checkpoint:
```
  Preparing metadata (setup.py) ... done
Installing collected packages: ngec
  DEPRECATION: Legacy editable install of ngec==0.0.0 from file:///Users/davidpivonka/Documents/Peacekeeping%20Dividends/Github%20Repo/NGEC (setup.py develop) is deprecated. pip 25.0 will enforce this behaviour change. A possible replacement is to add a pyproject.toml or enable --use-pep517, and use setuptools >= 64. If the resulting installation is not behaving as expected, try using --config-settings editable_mode=compat. Please consult the setuptools documentation for more information. Discussion can be found at https://github.com/pypa/pip/issues/11457
  Running setup.py develop for ngec
Successfully installed ngec

```


**Successfully installed ngec!** Yes!! 🎉
