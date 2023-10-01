# Redis Fashion Store VSS Demo
## Jupyter Notebook / RISE Presentation

This repository consists of a Jupyter Notebook that can be shown as a [RISE](https://github.com/damianavila/RISE) presentation (Reveal.js - Jupyter/IPython Slideshow Extension).

The code is written in Python and uses the [redis-py](https://github.com/redis/redis-py) Redis client.  You don't need to be a Python expert to run it and understand the concepts.  Not a Python developer?  Don't worry - these concepts can be applied equally in other programming languages: for example with the [node-redis](https://github.com/redis/node-redis) client for Node.js, [jedis](https://github.com/redis/jedis) for Java or [NRedisStack](https://github.com/redis/NRedisStack) for C#.

## Overview

This presentation is based on the [Redis Product Search Demo](https://github.com/RedisVentures/redis-product-search) by Tyler Hutcherson (`@tylerhutcherson`) and Sam Partee (`@Spartee`) from Redis.

## Setting up your Environment

To run the code locally, you'll need to install and setup a few things:

* Python 3 (if you don't have a recent version of Python, [grab one here](https://www.python.org/downloads/).  We've tested on Python 3.10)
* Poetry (dependency manager for Python - [read the installation instructions here](https://python-poetry.org/docs/#installation))
* Docker Desktop ([read the installation instructions here](https://www.docker.com/products/docker-desktop/)) - we use this to provide you with a Redis Stack instance.
* Git command line tools (the `git` command).  Get these from [the Git website](https://git-scm.com/downloads) if needed.
* RedisInsight - a graphical tool for viewing and managing data in Redis.  [Download a free copy here](https://redis.com/redis-enterprise/redis-insight/) or get it from the Apple App Store if you're on a Macintosh.

We'll assume that you've downloaded/installed the pre-requisites above, and explain how to configure them as needed in the remainder of this README.

## Cloning this Repository

At the terminal, clone the repository to your local machine:

```bash
git clone https://github.com/bsbodden/redis-vss-py.git
```

Then, change directory into the repository folder:

```bash
cd redis-vss-py
```

We assume that your terminal's current directory is this folder for all subsequent commands.

## Installing Python Dependencies

We're using the Poetry tool to manage Python virtual environments and dependencies.  Install the dependencies that this workshop uses with the following command:

```bash
poetry install
```

This installs the dependencies needed for this part of the workshop, and those for the [vector similarity search](./ipynb/README.md) part.  Expect to see output similar to this:

```bash
Creating virtualenv redis-vss-py-_T_fhuK9-py3.10 in /Users/simon/Library/Caches/pypoetry/virtualenvs
Installing dependencies from lock file

Package operations: 134 installs, 0 updates, 0 removals

  • Installing six (1.16.0)
  • Installing attrs (23.1.0)
  • Installing platformdirs (3.8.0)
... similar output...
```

## Creating an Environment File

The code uses a `.env` file to store configuration information.  We've provided an example file that you should be able to use without needing to make any changes.

Copy this into place:

```bash
cp env.example .env
```

Note that `.env` files may contain secrets such as Redis passwords, API keys etc.  Add them to your `.gitignore` file and don't commit them to source control!  We've done that for you in this repository.

## Starting a Redis Stack Instance

We've provided a Docker Compose file for you to run an instance of Redis Stack locally.  This will run on the default Redis port: 6379.  If you have another instance of Redis running on this port, be sure to shut it down first.

Start Redis Stack like this:

```bash
docker-compose up -d
```

You should see output similar to the following:

```bash
...
Starting redis-vss-py ... done
```

## Loading the Data Set

Download the data set contents from https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset
The unzip archive will create a directory like:

```
.
├── images
│   ├── 10000.jpg
│   ├── 10001.jpg
│   ├── 10002.jpg
│   ├── 10003.jpg
│   │   ...
│   ├── 9491.jpg
│   ├── 9497.jpg
│   └── 9892.jpg
└── styles.csv
```

The loader script expects the dataset to be located under the directory pointed to by the environment variable `DATASET_BASE`, set this to the value of the parent directory of styles.csv and the images directory above.

Let's load the Fashion Product Images Dataset into Redis Stack.  This step also builds the search indices that you'll use to query the data from RedisInsight and the Python sample application.

Run the data loader like this:

```bash
poetry run python loader.py
```

This process will take several minutes to vectorize all 44k product descriptions and images.

Now you have data in your Redis Stack instance, go back to RedisInsight, hit the refresh button and you should see 44K+ keys appear.  Click on a key to see the JSON document stored at that key.  The demo keys are prefixed with `fashion:`.

## Launch Jupyter Notebook w/ Rise Presentation

```bash
poetry run jupyter notebook
```

## Reset the presentation

To be able to re-run the presentation a small script resets certain aspects that are perform during the presentation:

* Drops the search index
* Removes the vectorize description and images for the docs with ids defined in the `DEMO_PRODUCTS` environment variable

To run the reset script use:

```bash
poetry run python reset.py
```

## Need Help or Want to Chat?

If you need help with this workshop, or just want to chat with us about the concepts and how you plan to use them in your own projects then we'd love to see you on the [Redis Discord](https://discord.gg/redis).  There's channels for everything from help with different programming languages to promoting your own projects and finding a job.


