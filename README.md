# Article Citation Model

## Summary

This model is based on the "Virus on Network" example model from python mesa framework.

JavaScript library used in this model to render the network: [d3.js](https://d3js.org/).

## Installation

To use this model, one needs to have python mesa installed.
To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

## Files

* ``run.py``: Launches a model visualization server.
* ``model.py``: Contains the agent class, and the overall model class.
* ``server.py``: Defines classes for visualizing the model (network layout) in the browser via Mesa's modular server, and instantiates a visualization server.

## Further Reading

https://mesa.readthedocs.io/en/stable/
