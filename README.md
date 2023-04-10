# Athena: A system to support (semi-)automated assessment of textual exercises

This system implements an approach for (semi-)automated assessment of textual exercises and can be integrated into learning management systems (LMS). A reference integration exists for the LMS [Artemis](https://github.com/ls1intum/Artemis).

Athena implements the approach described in our article *Machine learning based feedback on textual student answers in large courses*:

> **[Machine learning based feedback on textual student answers in large courses](https://www.sciencedirect.com/science/article/pii/S2666920X22000364).**  
> [Jan Philip Bernius](https://github.com/jpbernius), [Stephan Krusche](https://github.com/krusche), and Bernd Bruegge.  
> Computers and Education: Artificial Intelligence, Volume 3. June 2022. 
> DOI: [10.1016/j.caeai.2022.100081](https://doi.org/10.1016/j.caeai.2022.100081)

## Architecture

The Athena system is built using a microservice architecture, as depicted in Figure 1.
Four components comprise the Athena system:

![UML Component Diagram](.github/figures/components-light.png#gh-light-mode-only)
![UML Component Diagram](.github/figures/components-dark.png#gh-dark-mode-only)

<p align="center"><b>Figure 1:</b> Athena Microservice Architectuer depicted using a UML Component diagram.</p>

1.  **Load Balancer:** Provides Service in the form of a HTTP REST API to submit an Athena job. This component will manage the work distribution to other components.
2.  **Segmentation:** Component for segmenting Student Answers based on Topic Modeling.
3.  Language **Embedding:** Component for computing Language Embeddings using ELMo and uploading training material for ELMo.
4.  **Clustering:** Component for clustering of ELMo Vectors using HDBSCAN.

The load balancer orchestrates jobs and calls all components using their HTTP APIs.
After the job is completed, it calls back to LMS to submit the results.

## Basic Usage

### Running with Docker

Using the `docker-compose.yml` file included in the root directory of the repository is the easiest way to start Athena.

The execution of

    docker-compose up -d

will automatically build and start the Load-balancer, Segmentation, the Embedding and the Clustering component (The `-d` parameter will run containers in the background, omit it to directly see outputs).

The first time you start Athena, it will take a while to download all required images and build the components.

For testing and development purposes, a single component can be re-built using e.g.

    docker-compose build segmentation

or be started separately (in foreground mdoe) using e.g.

    docker-compose up segmentation

Stopping Athena can be achieved by stopping the running containers using

    docker-compose down

For further information have a look at the [Compose file reference](https://docs.docker.com/compose/compose-file/) and the [Compose command-line reference](https://docs.docker.com/compose/reference/overview/).

### Running the Services Using make

Prepare all local dependencies and start the services by running

    make -j6 # j6 is optional, but speeds up the process

in the root directory.
This will call `make` in all subdirectories,
which initializes virtual environments,
installs dependencies and downloads required models.
After that the services will be started automatically.

There is one special target in the `Makefile` that will start traefik and the MongoDB database in a docker container
to redirect to the services running on your local machine.

You can always just directly use `make` and it will automatically detect changed dependencies.

### Running the Services Using PyCharm

If you are using PyCharm, you can configure the project as follows:

1.  Open the project in PyCharm

2.  Ensure that you have the [EnvFile plugin](https://plugins.jetbrains.com/plugin/7861-envfile) installed so that the environment file loading can take place from the run configuration.

3.  Run the setup preparations by running `make setup` in a terminal or by using the run configuration `Prepare local setup`

4.  Now, you can add the different microservices as submodules of the PyCharm project. To do so, go to `File -> Open` and open the following directories. When asked, choose to open them using the "Attach" method (in the dialog that also provides options for "This window" / "New window").
    \- `clustering`
    \- `embedding`
    \- `load-balancer`
    \- `segmentation`
    \- `tracking`

5.  Configure the virtual environment Python interpreters for the different modules: For each of the modules in the list above, go to `File -> Settings -> Project: Athena -> Project Interpreter` and select the virtual environment in the `.venv` directory of the respective module.

6.  Now, you can start the different services by running the corresponding run configurations. This has the added advantage that you can debug the services directly from PyCharm by running the configuration in debug mode. You can also start all services by running the `All Services`-configuration.

### Notes on Running the Services Without Docker

Running the services directly has multiple advantages:

*   You can use the Debug-Mode of your IDE to debug the services
*   You can restart the services individually without restarting the whole system
*   The services will restart themselves if you change the code (the uvicorn-reloader is enabled by default)

Using makefiles or PyCharm will use the environment variables from `.local.env`.

You can remove all the setup files by running `make clean`.

## Basic API Overview

By default, a traefik-container will manage API-Endpoints and expose them on port 80 (default HTTP-port).
The following API-routes are available after start:

*   <http://localhost/submit> - For Artemis to submit a job to the load-balancer
*   <http://localhost/queueStatus> - To monitor the queue status of the load balancer
*   <http://localhost/getTask> - For the computation components to query tasks from the load balancer
*   <http://localhost/sendTaskResult> - For the computation components to send back results to the load balancer
*   <http://localhost/upload> - For Artemis to upload course material
*   <http://localhost/tracking> - For Artemis to access tracking functionality
*   <http://localhost/feedback_consistency> - For Artemis to access feedback\_consistency functionality

Traefik provides a dashboard to monitor the status of underlying components.
This dashboard is available on <http://localhost:9081/dashboard> by default.

## Test Instructions

1.  Set up a local instance of Artemis. Configure Athena exactly [like in the setup instructions](https://docs.artemis.cit.tum.de/dev/setup/#athene-service). Make sure that the Artemis `server_name` in the local configuration is set to `http://localhost:8080` so that Athena knows to call back this endpoint. Also, double-check that the `athene` profile is enabled.

2.  There are 2 paths to continue now. In the root directory:
    1.  Run `docker-compose up --build`.
    2.  Run `make setup -j6` and then `make start`.

3.  Go to http://localhost:8080, create a course, then create a text exercise.

4.  Use at least 10 test accounts to participate in the exercise. Otherwise, Athena will not start.

5.  Edit the exercise settings and set the due date to be the next full minute that has not yet passed.

6.  Wait a bit, then log messages should appear in the different microservices in Athena.

7.  To verify that Artemis gets called back by Athena, it might be helpful to set a breakpoint in `AtheneService.java` (in Artemis) in the `processResult` method.

## Configuration

For configuration of the Athena system you can make use of the `.env`-file in the repository. All variables in there are used in the `docker-compose.yml` to bring up the Athena system.

## Contributing

We welcome contributions in any form! Assistance with documentation and tests is always welcome. Please submit a pull request.

## Citing

To reference the automatic assessment approach developed in this system please cite our article in _Computers and Education: Artificial Intelligence_:

> **[Machine learning based feedback on textual student answers in large courses](https://www.sciencedirect.com/science/article/pii/S2666920X22000364).**  
> [Jan Philip Bernius](https://github.com/jpbernius), [Stephan Krusche](https://github.com/krusche), and Bernd Bruegge.  
> Computers and Education: Artificial Intelligence, Volume 3. June 2022. 
> DOI: [10.1016/j.caeai.2022.100081](https://doi.org/10.1016/j.caeai.2022.100081)

```bibtex
@Article{BerniusKB22,
    author = {Bernius, Jan Philip and Krusche, Stephan and Bruegge, Bernd},
    title = {Machine learning based feedback on textual student answers in large courses},
    journal = {Computers and Education: Artificial Intelligence},
    volume = {3},
    publisher = {Elsevier {BV}},
    year = {2022},
    doi = {10.1016/j.caeai.2022.100081},
}
```

## Publications

- **[Automatic Assessment of Textual Exercises](https://mediatum.ub.tum.de/?id=1661270).**  
  [Jan Philip Bernius](https://github.com/jpbernius).  
  Dissertation. Technische Universität München. Munich, Germany, June 2022.  
- **[Machine learning based feedback on textual student answers in large courses](https://www.sciencedirect.com/science/article/pii/S2666920X22000364).**  
  [Jan Philip Bernius](https://github.com/jpbernius), [Stephan Krusche](https://github.com/krusche), and Bernd Bruegge.  
  Computers and Education: Artificial Intelligence, Volume 3. June 2022. 
  DOI: [10.1016/j.caeai.2022.100081](https://doi.org/10.1016/j.caeai.2022.100081)
- **[A Machine Learning Approach for Suggesting Feedback in Textual Exercises in Large Courses](https://www.janphilip.bernius.net/preprint/las21.pdf)**.  
  [Jan Philip Bernius](https://github.com/jpbernius), [Stephan Krusche](https://github.com/krusche), and Bernd Bruegge.  
  8th ACM Conference on Learning @ Scale (L@S '21). Potsdam, Germany, June 2021.  
  DOI: [10.1145/3430895.3460135](https://doi.org/10.1145/3430895.3460135)
- **[Toward Computer-Aided Assessment of Textual Exercises in Very Large Courses](https://dl.acm.org/doi/10.1145/3408877.3439703).**  
  [Jan Philip Bernius](https://github.com/jpbernius).  
  52nd ACM Technical Symposium on Computer Science Education (SIGCSE '21). Toronto, ON, Canada, March 2021.  
  DOI: [10.1145/3408877.3439703](https://doi.org/10.1145/3408877.3439703)
- **[Towards the Automation of Grading Textual Student Submissions to Open-ended Questions](https://www.janphilip.bernius.net/preprint/ecsee20.pdf).**  
  [Jan Philip Bernius](https://github.com/jpbernius), Anna Kovaleva, [Stephan Krusche](https://github.com/krusche), and Bernd Bruegge.  
  4th European Conference of Software Engineering Education (ECSEE '20). Seeon, Germany, May 2020.  
  DOI: [10.1145/3396802.3396805](https://doi.org/10.1145/3396802.3396805)
- **[Segmenting Student Answers to Textual Exercises Based on Topic Modeling](http://ceur-ws.org/Vol-2531/poster03.pdf).**  
  [Jan Philip Bernius](https://github.com/jpbernius), Anna Kovaleva, and Bernd Bruegge.  
  17th Workshop on Software Engineering im Unterricht der Hochschulen (SEUH '20). Innsbruck, Austria, February 2020.
- **[Toward the Automatic Assessment of Text Exercises](http://ceur-ws.org/Vol-2308/isee2019paper04.pdf).**  
  [Jan Philip Bernius](https://github.com/jpbernius), and Bernd Bruegge.  
  2nd Workshop on Innovative Software Engineering Education (ISEE '19). Stuttgart, Germany, February 2019.
