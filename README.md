# Athene: A library to support (semi-)automated assessment of textual exercises

This library implements an approach for (semi-)automated assessment of textual exercises and can be integrated in learning management systems (LMS). A reference integration exists for the LMS [Artemis](https://github.com/ls1intum/Artemis).

The approach is based on the paper:
> Jan Philip Bernius and Bernd Bruegge. 2019. **Toward the Automatic Assessment of Text Exercises**. In *2nd Workshop on Innovative Software Engineering Education (ISEE)*. Stuttgart, Germany, 19–22. [[pdf]](https://brn.is/isee19)

## Components

- **Segmentation:**  
  API for segmenting Student Answers based on Topic Modeling
- **Clustering:**  
  API for computing Language Embeddings using ELMo and Clustering of ELMo Vectors using HDBSCAN

## Basic Usage

Using the `docker-compose.yml` file included in the root directory of the repository is the easiest way to start Athene. The execution of

```
docker-compose up -d
```

will automatically build and start both the Segmentation and the Clustering component (The `-d` parameter will run containers in the background). By default, the Segmentation component will listen on port 8000, while the Clustering component will listen on port 8001 of your local machine. This means, the following API-routes will be available after start:<br/>
[http://localhost:8000/segment](http://localhost:8000/segment)<br/>
[http://localhost:8001/embed](http://localhost:8000/segment)<br/>
[http://localhost:8001/cluster](http://localhost:8000/segment)<br/>

For testing and development purposes, a single component can be re-built using e.g.

```
docker-compose build segmentation
```

or be started separately (in foreground mdoe) using e.g.

```
docker-compose up segmentation
```

Stopping Athene can be achieved by stopping the running containers using

```
docker-compose down
```

For further information have a look at the [Compose file reference](https://docs.docker.com/compose/compose-file/) and the [Compose command-line reference](https://docs.docker.com/compose/reference/overview/).

## Contributing

We welcome contributions in any form! Assistance with documentation and tests is always welcome. Please submit a pull request.

## Citing

To reference the automatic assessment approach developed in this library please cite our paper in ISEE 2019 proceedings.

```bibtex
@inproceedings{BerniusB19,
  title     = {Toward the Automatic Assessment of Text Exercises},
  author    = {Jan Philip Bernius and Bernd Bruegge},
  booktitle = {2nd Workshop on Innovative Software Engineering Education (ISEE)},
  address   = {Stuttgart, Germany},
  year      = {2019},
  pages     = {19--22},
  url       = {http://ceur-ws.org/Vol-2308/isee2019paper04.pdf}
}
```
