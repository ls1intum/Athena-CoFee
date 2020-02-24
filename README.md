# Athene: A library to support (semi-)automated assessment of textual exercises

This library implements an approach for (semi-)automated assessment of textual exercises and can be integrated in learning management systems (LMS). A reference integration exists for the LMS [Artemis](https://github.com/ls1intum/Artemis).

The approach is based on the paper:
> Jan Philip Bernius and Bernd Bruegge. 2019. **Toward the Automatic Assessment of Text Exercises**. In *2nd Workshop on Innovative Software Engineering Education (ISEE)*. Stuttgart, Germany, 19–22. [[pdf]](https://brn.is/isee19)

## Components

- **Clustering:**  
  API for computing Language Embeddings using ELMo and Clustering of ELMo Vectors using HDBSCAN
- **Segmentation:**  
  API for segmenting Student Answers based on Topic Modeling

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
