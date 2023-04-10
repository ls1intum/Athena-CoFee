# Load Balancer

This service balances the load for incoming Artemis-requests to underlying compute nodes.

## Start locally (without Docker)

Locally, the service runs on port 8000. To start it,

*   First, run the following command for some preparations:
    ```bash
    make
    ```
    This will create a virtual environment and install all dependencies.

*   After that, configure the used virtual environment:
    ```bash
    source venv/bin/activate
    ```
    If you use an IDE, you can also configure the virtual environment there.
    In PyCharm, you can even go to `File > Open`, choose the embedding folder
    and then choose the `Attach` option.

*   Then, you can start the load balancer using `python start.py` or using your IDE.

## Start with Docker

Use the `docker-compose.yml` file from the parent directory
to start the embedding service (and all others) with Docker.

## API

The following API-routes will be available after start:

*   <http://localhost:8000/queueStatus> (GET) to get queue statistics
*   <http://localhost:8000/submit> (POST) for Artemis to submit a new Job
*   <http://localhost:8000/getTask> (GET) to get a queued task out of the queue
*   <http://localhost:8000/sendTaskResult> (POST) to send back the result of a task to the load balancer

Input example JSON for POST on http://localhost:8000/submit

```json
{
  "courseId": 2,
  "callbackUrl": "http://testurl",
  "submissions":[
      {
         "id":1,
         "text":"\n\n\n\nhello\n\n\n\n"
      },
      {
         "id":2,
         "text":"\n\ntest\n\nttest\n\ntest"
      },
      {
         "id":3,
         "text":"text"
      },
      {
         "id":4,
         "text":"\n\n\n\n"
      },
      {
         "id":5,
         "text":"Difference:\nInheritance: A class is a subclass of another class. Thats means you can use methods from the upper class, if these methods are public or protected. The supclass then inherits them and you can use these methods in the subclass. In pgdp we had a list called DocumentCollection. Then we implemented a new collection called LinkedDocumentCollection, which worked like a DocumentCollection but with linked documents. Adding, deleting doucments, for example, worked like in DocumentsCollection, therefore it was really convenient to inherit these methods. (1)\n\nDelegation: A class delegates methods to another class, where they has been implemented already. In the \"Proxy Pattern\" exercise, for instance, we used the methods open() and close() from NetworkConnection to implement same methods in ConnectionInterface. (2)\n\nAdvantages/Disadvantages:\nInheritance:\nAdvantage: As I've already mentioned, it's really convenient and intuitive to use. Adding new features, for example, to the subclass is very easy because you may use methods from the upper class or you don't need to implements specific methods because you've implemented them already.\n\nDisadvantage: Changes in parent class can influence the subclass if the subclass uses parant class methods/attributes. That leads to more work to enhance/maintain a program. In case of using methods from the upper class to implements new methods, it forces you to allow these methods in the subclass although they are unwanted there.\n\nDelegation: \nAdvantage: It's also very convenient in case of adding new methods by using methods from other objects. Same example as (2). You can also replace the reference object with other objects, if they the new object has same methods.\n\nDisadvantage: Objects needs to be initialized which leads to inefficiency.\n\n(1) is a perfect example for inheritance, because a LinkedDocumentCollection is a DocumentCollection, but with more features.\nIn contrast if i have a car class that has a method called engine() and inherite a class called plane only to to use the method engine() than it would be better to use delegation. A plane is not a car!"
      },
      {
         "id":6,
         "text":"text"
      },
      {
         "id":7,
         "text":"text"
      },
      {
         "id":8,
         "text":"text"
      },
      {
         "id":9,
         "text":"Inheritance \nI would use inheritance e.g. in a wether application and implement a view with the main key data.\nBut as there are different users e.g. a farmer and a pilot I would write a subclass which for the farmer gives him some extra special information he needs in order to make a decision when to start harvesting.\n\nAdvantages: \neasy to make it more specific, e.g. sell it to different customers with few changes and don't have to rewrite everything. \n\nDisadvantages:\nif I change the superclass, it would effect the subclasses and there would be need for change.\n\n\nDelegation:\nI would use delegation for example a existing calculator which has only a + function but no - function. \nTherefore I would use for my custom subtraction function an already existing operation (+ function). \n\nAdvantages: \nits flexible - you can replace it at runtime. vs inheritance at compile time\nDisadvantages: \nnot highly efficient, because objects are getting encapsulated."
      },
      {
         "id":10,
         "text":"Inheritance means to reuse implemented or specified functionality of the super class in the subclass. An example where inheritance is useful is when you want to implement different types of cars. The class Car would be the superclass, as all cars share common attributes like color, size, number of seats, etc. and common methods like drive() or steer(). All subclasses (e.g. FastCar, SlowCar, etc.) inherit all common attributes and methods, but can overwrite these if the specification is slightly different. For example a fast car can accelerate faster and has a higher maximum speed than a slow car. Also additional attributes or methods can be added. \nDelegation means to catch an operation and delegate it to another object and use the already implemented functionality by invoking a method in another object. This can be useful if you have different access rights in an application. When the client calls a method on the receiver, the receiver can check if the user invoking the method has the right to do so. If yes, the receiver delegates the method call to the delegate, which will execute the request. \n\nAdvantages of inheritance are, that the concept is supported by many programming languages, rather easy to use and you can easily add additional functionality. Possible disadvantages are, that all methods of the super class are inherited, but not all of them should be offered.\nAn advantage of delegation is the high flexibility, as objects can be replaced by run time. On the other hand it is inefficient as more objects have to be created during runtime.\n\nBut obviously it depends on the use case end the specific requirements which concept fits best.\n\nInheritance means that a super class defines a generalized interface or functionality, that all it's sub classes implement/provide. Delegation means that one object calls methods of another object.\n\nInheritance is a core principle of all object oriented programming languages. It offers a great way to generalize or specialize objects. It is easy to understand and use. The extensibility is very high, because it is easy to simply add different subclasses, without changing other objects. However it also very rigid, as all inheritance relationships need to be known at compile time.\n\nDelegation does not have this problem. The delegates can even change during runtime, but this advantage comes at the cost of performance.\n\nExamples:\nWhen designing UI elements, i would use inheritance to create different, specialized elements. For example, a slider and a button share many properties and functionalities (size, position, can be displayed, ?). This can be achieved, by creating the super class UIElement, that implements all these functionalities, and then creating slider and button as subclasses of UIElement. However, the actual function of the elements in the system should not be implemented this way. A button can be used for many different tasks, so it should not contain the corresponding behavior. Instead, when pressed, the button should delegate the task to another object."
      }
   ]
}
```

Input example JSON for GET on http://localhost:8000/getTask for a segmentation task

```json
{
    "taskType": "segmentation"
}
```

Input example JSON for POST on http://localhost:8000/sendTaskResult for a segmentation task

```json
{
    "jobId": "1",
    "resultType": "segmentation",
    "textBlocks": [
    {
      "id": 7,
      "startIndex": 0,
      "endIndex": 95
    },
    {
      "id": 7,
      "startIndex": 97,
      "endIndex": 300
    },
    {
      "id": 7,
      "startIndex": 302,
      "endIndex": 443
    },
    {
      "id": 9,
      "startIndex": 0,
      "endIndex": 99
    },
    {
      "id": 9,
      "startIndex": 100,
      "endIndex": 273
    },
    {
      "id": 9,
      "startIndex": 274,
      "endIndex": 368
    }
	.
	.
	.
  ]
}
```

Input example JSON for GET on http://localhost:8000/getTask for a embedding task:

```json
{
    "taskType": "embedding",
    "chunkSize": 100
}
```

Input example JSON for POST on http://localhost:8000/sendTaskResult for a embedding task:

```json
{
    "jobId": "1",
    "taskId": "1",
    "resultType": "embedding",
    "embeddings": [
	    {
	      "id": "b4290ebdf680cdd0ca84d9b79a593a4c9f0ff956",
	      "vector": [ ... ]
	    }
	    .
	    .
	    .
    ]
}
```

Input example JSON for GET on http://localhost:8000/getTask for a clustering task:

```json
{
    "taskType": "clustering"
}
```

Input example JSON for POST on http://localhost:8000/sendTaskResult for a clustering task:

```json
{
    "jobId": "1",
    "resultType": "clustering",
    "clusters": {
	    "0": {
	      "blocks": [
	        { "id": "807971050bb4312b79280e268b28756ae2f71e36" },
	        { "id": "4b769e97ef8a21fd9d68fe152bf54d456380e77e" }
	      ],
	      "probabilities": [ 1.0, 1.0 ],
	      "distanceMatrix": [
	        [ 0.0, 0.20236322290162645 ],
	        [ 0.20236322290162645, 5.551115123125783e-16 ]
	      ]
	    }
	    .
	    .
	    .
    }
}
```
