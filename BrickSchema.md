Introduction
============

## What is Brick?

Brick is an open-source effort to standardize semantic descriptions of the **physical, logical and virtual assets** in buildings and **the relationships between them**.
Brick consists of an **extensible dictionary** of terms and concepts in and around buildings, a set of **relationships** for linking and composing concepts together, and a **flexible data model** permitting seamless integration of Brick with existing tools and databases.
Through the use of powerful Semantic Web technology, Brick can describe the broad set of idiosyncratic and custom features, assets and subsystems found across the building stock in a consistent matter.

Adopting Brick as the canonical description of a building enables the following:

- Brick lowers the cost of deploying analytics, energy efficiency measures and intelligent controls across buildings
- Brick presents an integrated, cross-vendor representation of the multitude of subsystems in modern buildings: HVAC, lighting, fire, security and so on
- Brick simplifies the development of smart analytics and control applications
- Brick reduces the reliance upon the non-standard, unstructured labels endemic to building management systems

Brick is free and open-sourced under the BSD 3-Clause license. The source code for Brick, this website, and related tools developed by the Brick team are available on **[GitHub](https://github.com/BrickSchema)**.

![Brick Model Example](/img/brick-model-example.png)

## How Does Brick Compare to X?

[**Project Haystack**](https://project-haystack.org/) is a popular tagging system for describing building assets using semi-structured sets of tags.
Because there are no formal rules for how tags can be used, Haystack-based descriptions of buildings tend to consist of ad-hoc collections of tags, resulting in highly custom and inconsistent modeling practices across sites.
Brick includes a tagging system similar to Haystack that augments tags with formal semantic rules that promote consistency and interpretability.

[**Industry Foundation Classes**](https://technical.buildingsmart.org/) and [**Building Information Models**](https://www.nationalbimstandard.org/) emerged from the need for a common exchange model for the 3D architectural drawings needed for a building's construction. BIM models capture structural information, but lack descriptions of how the constituent equipment and points function together.

[**Building Topology Ontology (BOT)** ](https://w3c-lbd-cg.github.io/bot/) is a complementary effort for semantic building metadata from the [Linked Building Data W3C Community Group](https://www.w3.org/community/lbd/) that focuses on capturing topological concepts in buildings such as sites, floors, zones and rooms. Because BOT is built using the Semantic Web, it can be used in tandem with Brick.

[**Smart Appliances REFerence Ontology (SAREF)**](https://sites.google.com/site/smartappliancesproject/ontologies/reference-ontology) is an ontology capturing high level aspects of smart and connected appliances. While SAREF does not capture the the full spectrum of equipment and sensors that exist in buildings, SAREF models can be easily integrated into Brick.


Modeling Support         | **Brick** | **Project Haystack** | **IFC** | **BOT** | **SAREF**
-------------------------|-----------|----------------------|---------|---------|----------
HVAC Systems             |  **yes**      |       **yes**    |**yes**  |   no    |   no
Lighting Systems         |  **yes**      |       partial    |**yes**  |   no    |   no
Electrical Systems       |  **yes**      |       **yes**    |**yes**  |   no    |   no
Spatial Information      |  **yes**      |       no         |**yes**  |**yes**  |   no
Sensor Systems           |  **yes**      |       **yes**    |generic  |   no    |   **yes**
Control Relationships    |  **yes**      |       no         |generic  |   no    |   no
Operational Relationships|  **yes**      |       no         |generic  |   no    |   no
Formal Definitions       |  **yes**      |       no         |**yes**  |**yes**  |   **yes**
<br></br>

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Design Principles
======================

Brick is an ontology-based metadata schema that captures the entities and relationships necessary for effective representations of buildings and their subsystems.
Brick describes buildings in a machine readable format to enable programmatic exploration of different operational, structural and functional facets of a building.

## Design Principles

Brick adheres to the following design principles:

* **Completeness**: A schema should represent all the information (such as a sensor’s location, type, etc.) required by building applications.
* **Expressivity**: A schema should capture the diverse family of entities and relationships between them that are present in a building's BMS and expressed in canonical energy-, operations- and management-oriented applications and scenarios.
* **Usability**: A schema should be not too complex for users to easily understand and use.
* **Consistency**: A schema should be able to enforce consistency in modeling processes across different users.
* **Extensibility**: A schema should be easily extensible to cover new concepts in a consistent way.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Core Concepts
==============

These are the essential concepts of Brick.

## Entity

An entity is an abstraction of any physical, logical or virtual item; the actual "things" in a building.

Physical entities are anything that has a physical presence in the world.
Examples are mechanical equipment such as air handling units, variable air volume boxes, luminaires and lighting systems, networked devices like electric meters, thermostats and electrical vehicle chargers, and spatial elements like rooms and floors.

Virtual entities are anything whose representation is based in software.
Examples are sensing and status points which allow software to read the current state of the world (such as the value of a temperature sensor, the speed of a fan, or the energy consumption of a space heater), and actuation points which allow software to write values (such as temperature setpoints or the brightness of a lighting fixture).

Logical entities are those entities or collections of entities that are defined by a set of rules.
Examples are HVAC zones and Lighting zones.
Concepts such as class names and tags (defined below) also fall into this category.
</details>

## Tag

A **tag** is an atomic fact or attribute of an entity.
Examples of tags are `sensor`, `setpoint`, `air`, `water`, `discharge`, `leaving` and `vav`.
Brick borrows the concept of tags from Project Haystack in order to preserve the flexibility and ease of use for annotation; however, Brick does not rely on tags alone to determine the type of an entity.

## Class

A **class** is a named category with intensional meaning (a definition) used for grouping entities.
Classes are organized into a hierarchy, and entities are instances of one or more classes (that is, the type of an entity is given by one or more classes).
Classes also have a set of associated tags, which provide helpful annotations for discovery.

## Relationship

A **relationship** defines the nature of a link between two related entities.
Examples of relationships are *encapsulation* (one entity is contained within another), *sequence* (one entity takes effect before another in some process) and *instantiation* (one entity's type is given by another entity).

For a more detailed look at relationships in Brick and how/when to use them, read the [Relationship documentation](/brick/relationships).

## Graph

A **graph** is an abstract organizational data structure representing a set of entities (nodes) and relationships (edges). Brick is represented by a directed, labeled graph.

```{image} ../img/node-edge-graph.png
:width: 400px
:align: center
```

This figure is an illustration of a generic directed graph. In the context of Brick, nodes in a graph are entities and the edges of the graph are relationships. The source and destination nodes of an edge indicate the subject and object entities of the relationship given by the name of the edge.

We recommend reading the [Wikipedia page on the abstract graph data structure](https://en.wikipedia.org/wiki/Graph_(abstract_data_type)).

In Brick, the graph is represented using the RDF data model. The [RDF primer page](https://www.w3.org/TR/rdf11-concepts/) is an excellent introduction to how a graph is represented using RDF.


## Brick Model 

A **Brick model** is a digital representation of a building that adheres to the Brick schema. Entities in a Brick model are classified according to the classes defined by Brick, and are connected using the relationships defined by Brick. Several annotated reference models are available in the [Modeling Common Subsystems](/modeling/collections) section.

![Brick Model Example](../img/brick-model-example.png)


The blue nodes represent entities that are instances of Brick classes.These are the "things" inside our example building. They range from equipment (`AHU1A`, `VAV2-4`), points (`VAV2-4.DPRPOS`), locations (`Room 410`) and logical collections (`VAV2-3Zone`). The colored boxes connected to the instances with dashed lines represent Brick classes; the dashed line represents the "is an instance of" relationship (`rdf:type`). The rest of the class structure has been elided for simplicity. Lastly, the solid directed edges represent Brick relationships between entities.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Relationships
=============

## Definitions

An **Entity** is a digital representation of any physical, logical or virtual item; the actual "things" in and around a building.  Brick defines how entities can be classified and related to one another. There are several flavors of entities:

- **Physical Entities**: anything that has a physical presence in the world. Examples are:
    - mechanical equipment such as air handling units, variable air volume boxes, luminaires and lighting systems
    - networked devices like electric meters, thermostats, electric vehicle chargers
    - spatial elements like buildings, floors and rooms
- **Virtual Entities**: anything whose representation is based in software. Examples are:
    - sensing and status points which allow software to read the current state of the world (such as the value of a temperature sensor, the speed of a fan or the energy consumption of a space heater)
    - actuation points which allow software to write values (such as temperature setpoints or brightness of a lighting fixture)
    - computed points such as average temperatures, electric meter aggregates
- **Logical Entities**: entities or collections of entities defined by a set of rules. Examples are HVAC zones and Lighting zones. Concepts which help to define Brick also fall into this category such as class names and tags

**Relationships** express how entities, classes, tags and other "things" interact and are associated with each other. More formally, a relationship defines the nature of a link between two related entities. The purpose of this document is to provide greater clarity on:

- the broad categories of relationships
- names and definitions of the specific relationships defined by the Brick ontology
- guidelines, idioms and examples for how to apply these relationships in practice

## Philosophy of Brick Relationships

There are many possible perspectives on how a building may be described. The relationships defined by Brick outline several of these:

**Composition**: informally, what "things" can be assembled to make other "things", or what "things" make up other "things". There are several flavors of this. Physical composition describes what equipment can be composed of other equipment (e.g. a VAV may be made up of a damper, fan, reheat coil and so on), and how locations can be composed of other locations (e.g. a building is made up of floors and spaces). Logical composition describes how concepts can be broken down: an HVAC zone consists of a set of rooms, for example.

**Topology**: the way in which "things" are connected or arranged. This includes how equipment are connected and in what order they affect or modulate some media as it flows through the building, such as air or water. The topological perspective of a building also describes what spaces or rooms or zones are connected and which are next to each other.

**Telemetry**: the data *sources* associated or attached to various "things", be they logical, physical or virtual. In BMS-parlance, these are called "Points", and consist of the *digital* representations of the sensors, setpoints, commands, alarms and parameters that constitute the data produced by, for and on behalf of a building.

Brick provides a way to describe a building and its subsystems along each of these perspectives.

## Defining Brick Relationships

We list each of the Brick relationships related to each of the modeling perspectives described above. Each relationship has a *subject* (the "thing" owning the relationship, or the "thing" that the relationship is about) and an *object* (the "thing" that is the value of the relationship).

### Composition

`brick:hasPart`: the *subject* has some component or part identified by *object*; used to describe both physical and logical composition. This relationship is not typically used to desscribe the physical location of the *object* except in the case where the location of the *object* is fundamental to the identity of the *subject*. For example, a chair being located in a room is not fundamental to the definition of a room because a room can exist independent of whether or not a chair is located in it -- here, we would use the `brick:hasLocation` relationship (see below). However, a damper being "located" in a VAV is fundamental to the definition of a VAV because a VAV must be able to modulate the volume of air. In this case, we would use the `brick:hasPart` relationship.

### Topology

`brick:feeds`: the *subject* is arranged upstream of *object*, implying that some media flows from *subject* into *object*.

`brick:hasLocation`: the *subject* has a location given by *object*; this is the spatial notion of "location" and is not related to composition. See the definition of `brick:hasPart` above for a discussion of the difference


### Telemetry

`brick:hasPoint`: the *subject* has a source of telemetry identified by *object*. Generally this means that some aspect of *subject* is measured, controlled, configured or monitored, and the generated telemetry is identified by *object*. The type and definition of *object* dictates what aspect of *subject* is being represented by data.

`brick:hosts`: the *subject* (an ICT Equipment instance) hosts or exposes the *object* (a Point). Use this to describe which network device or controller physically exposes a given data point.

### Control

```{note}
`brick:controls`, `brick:isControlledBy`, `brick:hosts`, and `brick:isHostedBy` are new in Brick v1.5.
```

`brick:controls`: the *subject* (a Controller) controls the *object* (Equipment).

`brick:isControlledBy`: inverse of `brick:controls`; the *subject* (Equipment) is controlled by the *object* (a Controller).

## How and When to Use Brick Relationships

When your *subject* is a...

- **Location**:
  - `hasPart` describes the components of that location
    - Floor `hasPart` Room
    - HVAC Zone `hasPart` Room
- **Point**:
  - `isPointOf` describes what the data is relevant to
    - Sensor `isPointOf` Room
- **Equipment**:
  - `hasPoint` describes telemetry associated with the equipment:
    - VAV `hasPoint` Temperature Sensor
    - Damper `hasPoint` Damper Position Command
  - `hasLocation` describes where the equipment is physically located
    - Thermostat `hasLocation` Room
  - `hasPart` describes the components of the equipment
    - VAV `hasPart` Damper
    - VAV `hasPart` Heating Coil
    - AHU `hasPart` Supply Fan
  - `feeds` describes downstream equipment and locations
    - AHU `feeds` VAV
    - VAV `feeds` HVAC Zone
  - `isControlledBy` describes the controller responsible for the equipment
    - VAV `isControlledBy` VAV_Controller
- **ICT Equipment**:
  - `hosts` describes points exposed by the device
    - BACnet_Device `hosts` Temperature_Sensor
- **Controller**:
  - `controls` describes what equipment the controller manages
    - VAV_Controller `controls` VAV

### Quick Note on "Inverse" Relationships

Brick allows many relationships to be defined in two different directions through the use of an "inverse" relationship. This lends some flexibility to the modeler, and the vast majority of Brick-related software, databases and tooling will support the use of either direction.

| Relationship | Inverse |
|--------------|---------|
| `hasPoint`   | `isPointOf` |
| `hasPart`    | `isPartOf` |
| `hasLocation`| `isLocationOf` |
| `feeds`      | `isFedBy` |
| `controls`   | `isControlledBy` |
| `hosts`      | `isHostedBy` |

In all cases where we have `subject relationship object`, an equvalent statement is `object inverse-relationship subject`.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Modeling Data Sources
=====================

Brick models describe data sources and their context --- what they are, where they are, what they mean, and how they relate to the building processes and structures that contain them. Because Brick models are only a means of *describing* data sources, we also need a way of representing the data itself. This document describes how to effectively describe timeseries data --- stored in an external database --- using the Brick ontology.

Specifically, this document covers:
- common design patterns for describing timeseries data with Brick
- using and verifying units of measure for timeseries data

This document assumes familiarity with the [Relationships documentation](/brick/relationships).

For information on how to link timeseries data in Brick to a database, see the [timeseries storage documentation](/metadata/timeseries-storage).

Here is the high-level description of the Brick data model for telemetry. Boxes represent entities; edges represent relationships. Bolded items are defined by the Brick ontology and do not need to be defined in a Brick model for a particular building.

```{image} ../img/brick-point-unit.png
:width: 600px
:align: center
```

## Categorizing Data Sources

Instances of the Brick `Point` class represent sources or sinks of telemetry. There are several major classes of telemetry in Brick:
- `Sensor`: represents the value of a device or instrument designed to detect and measure a variable
- `Setpoint`:  represents the value at which the desired property is set
- `Alarm`: represents signals that alert an operator to an off-normal condition which requires some form of corrective action
- `Command`: represents settings/actions that directly determines the behavior of equipment and/or affects relevant operational points.
- `Parameter`: represents configuration settings used to guide the operation of equipment and control systems; for example they may provide bounds on valid setpoint values
- `Status`: represents the current operating mode, state, position, or condition of an item. Statuses are observations and should be considered 'read-only'

Each of these classes is the root of a class hierarchy of more specific point types. See the [Brick documentation](https://brickschema.org/ontology/1.2/classes/Point) for details. To observe documentation for any Brick class, simply navigate to the Brick class URL in your browser. For example, the Brick class `brick:Air_Temperature_Sensor` is short for [`https://brickschema.org/schema/Brick#Air_Temperature_Sensor`](https://brickschema.org/schema/Brick#Air_Temperature_Sensor); navigating to that link will open a web page with the documentation describing that class.

## Point Instances

A single data source --- a particular sensor channel, setpoint, and so on --- is realized in a Brick model as an instance of a `Point` class. An instance is represented by a URI, typically in a namespace specific to the deployment site, which is related to a Brick `Point` class by means of the `rdf:type` relationship.

The snippet below defines a zone air temperature sensor named `mybldg:t1` in two equivalent ways.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   rdf:type   brick:Air_Temperature_Sensor .
# 'a' is a common and universally recognized shorthand for 'rdf:type'
mybldg:t1   a   brick:Air_Temperature_Sensor .
```

An instance is commonly related to locations and/or equipment by means of the `brick:isPointOf` relationship, though these annotations are optional:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   a   brick:Air_Temperature_Sensor .

mybldg:tstat1 a   brick:Thermostat ;
    brick:hasPoint mybldg:t1 .

# instead of the `brick:hasPoint` line above, we could have written
mybldg:t1 brick:isPointOf mybldg:tstat1 .
```

`Point`s cannot have locations (they are not physical entities), but they can be related to locations through the `brick:isPointOf` relationship.
We can associate the `Point` with an equipment, and then place the equipment in a location. For example, the following snippet associates a temperature sensor with a thermostat, and then places the thermostat in a room:


```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   a   brick:Air_Temperature_Sensor .
mybldg:tstat1 a   brick:Thermostat ;
    brick:hasPoint mybldg:t1 .

mybldg:room1 a   brick:Room ;
    brick:isLocationOf mybldg:tstat1 . # the thermostat, not the sensor!

```

An instance can have many other properties attached to it, including units of measure as we will see in the next section.

## Units of Measure

```{note}
A list of available units can be found [here](http://www.qudt.org/doc/DOC_VOCAB-UNITS.html)
```

An important piece of metadata to capture is the units of measure for a particular data stream. Brick builds on the [QUDT ontology](http://qudt.org/), which provides formal, semantic definitions of many common units. We have done some work to try and simplify the data model for the common cases, but there are some situations for which the necessary complexity comes through. We will point out those "sharp corners" in the documentation where they arise.

Units of measures are instances of the `qudt:Unit` class, and are represented by URIs such as [`unit:DEG_F`](http://qudt.org/vocab/unit/DEG_F) and [`unit:PPM`](http://qudt.org/vocab/unit/PPM). Units are associated with Brick `Point`s with the `brick:hasUnit` relationship:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   a   brick:Air_Temperature_Sensor ;
    brick:hasUnit   unit:DEG_F .
```

*A list of available units can be found [here](http://www.qudt.org/doc/DOC_VOCAB-UNITS.html)*. Given a Brick `Point` instance, it is possible to query for valid potential units. The `?unit` values returned by this query can be associated with a `Point` instance using the `brick:hasUnit` relationship as seen above.

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#> .
PREFIX qudt: <http://qudt.org/schema/qudt/> .

SELECT ?unit  WHERE {
    mybldg:t1   brick:measures/qudt:applicableUnit ?unit .
}
```

---

Some QUDT units have symbols associated with them; these can be retrieved through altering the above query:

```sparql
SELECT ?unit ?symbol WHERE {
    mybldg:t1   brick:measures/qudt:applicableUnit ?unit .
    OPTIONAL {
        ?unit   qudt:symbol ?symbol
    }
}
```

```{note}
Most QUDT units have *labels*, which are human readable strings denoting the units. These may be a helpful alternative to `qudt:symbol` for rendering what units are associated with a point. These can be retrieved using the following query:

```sparql
SELECT ?unit ?label WHERE {
    mybldg:t1   brick:measures/qudt:applicableUnit ?unit .
    ?unit rdfs:label ?label
}
```
---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Aliases and Equivalent Classes
==============================


```{note}
This feature was introduced in Brick v1.4.
```

Over its history, Brick has accumulated several duplicate class names. For example: `brick:AHU`, `brick:Air_Handler_Unit` and `brick:Air_Handling_Unit` can all be found in the Brick 1.4 release.
Brick retains all of these classes for backwards-compatibility; however, in Brick 1.4 it became necessary to denote a *preferred* class among a set of interchangeable classes.
At the same time, downstream tools and consumers should remain agnostic to whichever class was chosen by a modeler.
Brick handles both of these features through two mechanisms: *equivalent classes* and *aliases*.

## Aliases

Aliases identify the *preferred* class among a set of interchangeable (equivalent) classes.
Non-preferred classes will have a `brick:aliasOf` property which indicates the preferred class.

See below a snippet of Brick 1.4 containing definitions of `AHU`, `Air_Handler_Unit` and `Air_Handling_Unit`. Only `brick:Air_Handling_Unit` is missing the `brick:aliasOf` property, so it is the preferred class. The other classes have a `brick:aliasOf` property pointing to this preferred class.

```ttl
brick:AHU a owl:Class, sh:NodeShape ;
    rdfs:label "AHU" ;
    owl:equivalentClass brick:Air_Handling_Unit ;
    brick:aliasOf brick:Air_Handling_Unit .

brick:Air_Handler_Unit a owl:Class, sh:NodeShape ;
    rdfs:label "Air Handler Unit" ;
    owl:equivalentClass brick:Air_Handling_Unit ;
    brick:aliasOf brick:Air_Handling_Unit .

brick:Air_Handling_Unit a owl:Class, sh:NodeShape ;
    rdfs:label "Air Handling Unit" ;
    rdfs:subClassOf brick:HVAC_Equipment ;
    owl:equivalentClass brick:AHU,
        brick:Air_Handler_Unit ;
    brick:hasAssociatedTag tag:AHU,
        tag:Air,
        tag:Equipment,
        tag:Handler,
        tag:Handling,
        tag:Unit .
```

### Listing all Preferred Classes

This SPARQL query lists all preferred classes in Brick:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?preferred WHERE {
    ?preferred a owl:Class ;
               rdfs:subClassOf* brick:Entity .
    FILTER NOT EXISTS { ?preferred brick:aliasOf ?alias }
}
```

Here is how to run this query on the latest Brick release:

```{code-cell}
from rdflib import Graph
brick = Graph()
brick.parse("https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl", format="ttl")
res = brick.query("""
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?preferred WHERE {
    ?preferred a owl:Class ;
               rdfs:subClassOf* brick:Entity .
    FILTER NOT EXISTS { ?preferred brick:aliasOf ?alias }
}
LIMIT 10
""")
for row in res.bindings:
    print(row)
```

### Getting the Preferred Class for an Entity

This SPARQL query gets the preferred class for a specific Brick class:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?preferred WHERE {
    { ?class brick:aliasOf ?preferred }
    UNION
    {
        BIND ( ?class AS ?preferred )
        FILTER NOT EXISTS { ?class brick:aliasOf ?other }
    }
}
```

Here is how to run this query on the latest Brick release. Adjust the `initBindings` paramete to change which class you are querying the alias for.

```{code-cell}
from rdflib import Graph, BRICK
brick = Graph()
brick.parse("https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl", format="ttl")

query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?preferred WHERE {
    { ?class brick:aliasOf ?preferred }
    UNION
    {
        BIND ( ?class AS ?preferred )
        FILTER NOT EXISTS { ?class brick:aliasOf ?other }
    }
}"""

# try this query for an alias
res = brick.query(query, initBindings={"class": BRICK.AHU})
for row in res.bindings:
    print(row)

# try this query for a preferred calss
res = brick.query(query, initBindings={"class": BRICK.Air_Handling_Unit})
for row in res.bindings:
    print(row)
```

## Equivalent Classes

Groups of duplicate classes (e.g., `AHU`, `Air_Handler_Unit` and `Air_Handling_Unit`) will also be marked as *equivalent* classes using the `owl:equivalentClass` property.
There are two SHACL rules in Brick (`bsh:OWLEquivalentClassRule1` and `bsh:OWLEquivalentClassRule2`) which handle the semantics of equivalent classes: when SHACL inference is run on a Brick model, these rules will add *all* the equivalent classes to each entity.

For example, consider a simple Brick model with a single AHU instance:

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix : <urn:bldg#> .

:myAHU a brick:AHU .
```

After SHACL inference, the model will contain:

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix : <urn:bldg#> .

:myAHU a brick:AHU, brick:Air_Handler_Unit, brick:Air_Handling_Unit .
```

This means that *after running SHACL inference*, one can use the preferred Brick classes to find an entity.
It is not necessary to know which (equivalent) class was used.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Creating a Brick Model
======================

A Brick model must be created, derived or otherwise produced in order to enable data-driven applications and deliver value.
There are several ways of creating a Brick model for a building.
The most appropriate choice of method or tool depends on a number of factors:
- whether there is existing metadata or an existing digital representation of the building
- the format or standard that defines any digital representation
- how standardized, regular or predictable that digital representation is

The rest of this section describes common ways of creating a Brick model, organized by what form of source information is available.


## From Scratch

A Brick model can be created from scratch by explicitly listing the contents of the graph.
This is often helpful when creating [small examples](https://github.com/BrickSchema/Brick/tree/master/examples), when no existing structured information is available, or when the building is best described programatically.

There is no prescribed methodology for creating a Brick model from scratch.
A common pattern is to use data structures to represent collections of similar information (e.g. all rooms in a building, all VAVs and their points, etc) and then to traverse those data structures, creating triples in a graph along the way.

### Software

- [brickschema](https://brickschema.readthedocs.io/) (Python): Python package over RDFlib that provides Brick-specific features and APIs for working with Brick models
- [RDFlib](https://rdflib.readthedocs.io/en/stable/) (Python): Python package for working with RDF graphs

### Example

The following example uses the [brickschema](https://brickschema.readthedocs.io/) package to create a simple Brick model:


```python
import brickschema
from brickschema.namespaces import A, BRICK, UNIT
from rdflib import Namespace, Literal

# create a namespace for the building
BLDG = Namespace("urn:my-building-name#")

# create a graph object to store the Brick model
g = brickschema.Graph()
g.bind("bldg", BLDG)

# create a datastructure for floors + rooms
rooms_and_floors = {
    "Floor1": ["Room1", "Room2", "Room3"],
    "Floor2": ["Room4"],
}

for floor, room_list in rooms_and_floors.items():
    # Use the strings in the datastructure to refer to entities in the Brick model.
    # By putting "BLDG[floor]" into the graph, we implicitly create the entity.
    g.add((BLDG[floor], A, BRICK.Floor))
    for room in room_list:
        g.add((BLDG[room], A, BRICK.Room))
        g.add((BLDG[room], BRICK.isPartOf, BLDG[floor]))

# save the file to disk
g.serialize("my-building.ttl", format="ttl")
```

Also see the Brick [examples folder](https://github.com/BrickSchema/Brick/tree/master/examples) which contains a few examples of creating sample models from scratch.

## From Structured Tabular Sources

Structured tabular sources like CSV files, schedules and COBie sheets are often good sources of metadata.
The Brick ecosystem contains several tools that help describe how this structured data can be transformed into a Brick model.
Most of these tools operate by
- use a mapping between the terms/types in the source data and their corresponding Brick classes to create entities
- use the relationships between columns in the source to define the relationships between those entities

Generally, this means that each *row* of the input data results in the creation of a subgraph containing some entities, their types, and the relationships between them.

### Software
- [brickify](https://brickschema.readthedocs.io/en/latest/brickify/index.html): a robust tool for describing transformations to Brick from structured sources like tables (spreadsheets, CSV files)
- [brick-builder](https://github.com/gtfierro/brick-builder): like `brickify` but simpler and with fewer features. Uses templates to describe how CSV rows should be turned into a Brick model.
- [rule-based-model-builder](https://github.com/gtfierro/rule-based-model-builder): experimental framework for expressing complex transformations of structured data to a Brick model; includes COBie translation.

### Example

#### Brickify

Assume a spreadsheet with the following data

VAV name | temperature sensor | temperature setpoint | has_reheat
---------|--------------------|----------------------|-----------
A | A_ts | A_sp | false
B | B_ts | B_sp | true

The following `brickify` config file expresses how to create VAV objects in Brick from that spreadsheet, with their corresponding sensors. It optionally creates the VAV with Reheat type when prompted. Notice that the types of the entities in the rows are determined by the column name and that this is baked into the config file.

```yaml
---
namespace_prefixes:
  brick: "https://brickschema.org/schema/Brick#"
  bldg: "http://mybuildings.com/mybuilding#"
  rdf: "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
operations:
  -
    data: |-
      bldg:{VAV name} rdf:type brick:VAV ;
                      brick:hasPoint bldg:{temperature sensor} ;
                      brick:hasPoint bldg:{temperature setpoint} .
      bldg:{temperature sensor} rdf:type brick:Temperature_Sensor .
      bldg:{temperature setpoint} rdf:type brick:Temperature_Setpoint .
  -
    conditions:
      - |
        '{has_reheat}'
    data: |-
      bldg:{VAV name} rdf:type brick:RVAV .
```

This creates the following Brick model

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <http://mybuildings.com/mybuilding#> .

bldg:A rdf:type brick:VAV ;
                brick:hasPoint bldg:A_ts ;
                brick:hasPoint bldg:A_sp .
bldg:A_ts rdf:type brick:Temperature_Sensor .
bldg:A_sp rdf:type brick:Temperature_Setpoint .

bldg:B rdf:type brick:VAV, brick:RVAV ;
                brick:hasPoint bldg:B_ts ;
                brick:hasPoint bldg:B_sp .
bldg:B_ts rdf:type brick:Temperature_Sensor .
bldg:B_sp rdf:type brick:Temperature_Setpoint .
```


### Tutorials
- [Creating a Brick model with Brick Builder and OpenRefine](https://www.youtube.com/watch?v=LKcXMvrxXzE)

## From Haystack Models

Translation from Project Haystack <4.0 models is available in [brickify](https://brickschema.readthedocs.io/en/latest/brickify/index.html#haystack-handler). Translation for Haystack 4.0 models is in development.

### Software
- [brickify](https://brickschema.readthedocs.io/en/latest/brickify/index.html): a robust tool for describing transformations to Brick from structured sources like tables (spreadsheets, CSV files)

## From IFC Models

Currently, only support for COBie spreadsheets has been developed; see the software below.

Support for translation from IFC models directly is in development.

### Software
- [rule-based-model-builder (COBie)](https://github.com/gtfierro/rule-based-model-builder/tree/main/examples/cobie): implementation of a COBie translator using the `rule-based-model-builder` package

## From BMS Point Labels

One of the most common forms of existing building metadata are BMS point labels. Unfortunately, these often lack consistent structure, or follow ad-hoc naming conventions which are rarely documented.
The primary challenge when dealing with these sources is figuring out what each entitity is.
Each point label explicitly corresponds to a Brick Point instance, but the label itself may also contain additional information describing related equipment, other assets or even some of the building topology.

The reconcilation API server linked below will attempt to infer the type of a point from common abbreviations in its label. This is a helpful tool for implementating translation software for different point naming schemes.

### Software
- [Brick Reconciliation API Server](https://github.com/BrickSchema/reconciliation-api): an implementation of the W3C reconciliation api for use with OpenRefine
- [OpenRefine](https://openrefine.org/): locally-hosted web-based tool for manipulating mess ydata
- [point-label-sharing](https://github.com/gtfierro/point-label-sharing): a Python package for extracting point labels from a BACnet network

### Tutorials
- [Creating a Brick model with Brick Builder and OpenRefine](https://www.youtube.com/watch?v=LKcXMvrxXzE)

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Inference and Reasoning
=======================

**Inference** is the process by which implied information is discovered and made explicit in a model. Informally, you can think of this process as automatically adding additional metadata to your Brick model.

The Brick ontology definition includes a set of formal axioms that outline what information can be implied by the statements in a particular Brick model. These axioms are interpreted by a piece of software called a **reasoner**, which derives all implied information and adds it to the Brick model. The process of performing inference is sometimes referred to as **reasoning**.

```{note}
Brick uses the OWL 2 RL profile, described [in this W3C document](https://www.w3.org/TR/owl2-profiles/). [This section](https://www.w3.org/TR/owl2-profiles/#Reasoning_in_OWL_2_RL_and_RDF_Graphs_using_Rules) of the W3C documentation provides first-order definitions of the OWL 2 RL axioms, which may be helpful in understanding the specific reasoning mechanisms at hand. Reading and understanding these documents are *not* necessary to effective use of Brick.
```

## Brick Inference Results

Applying inference to a Brick model can automatically add a great deal of information that would otherwise need to be manually added. This includes, but is not limited to:

- **Superclasses:** for Brick entities that are instances of Brick classes, reasoning will also attach the superclasses to the instance
- **Inverse relationships**: reasoning will automatically add the "inverse" Brick relationships where needed (e.g. `brick:feeds` is the reverse of `brick:isFedBy`)
- **Tags**: reasoning will add tags to Brick entities which are instances of Brick classes

While using a reasoner is not strictly necessary for effective use of Brick, it does fill in a substantial amount of information that makes Brick easier to use and a more consistent experience.

### Example: Superclasses

Before reasoning:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   a   brick:Zone_Air_Temperature_Sensor .
```

After reasoning:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix tag: <https://brickschema.org/schema/BrickTag#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

# The reasoner adds all parent classes of brick:Zone_Air_Temperature_Sensor as types
# of the mybldg:t1 entity.
# For clarity, we are eliding the tags that would also be associated with mybldg:t1
mybldg:t1   a   brick:Zone_Air_Temperature_Sensor,
                brick:Air_Temperature_Sensor,
                brick:Temperature_Sensor,
                brick:Sensor,
                brick:Point .
```

### Example: Tags

Before reasoning:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   a   brick:Zone_Air_Temperature_Sensor .
```

After reasoning:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix tag: <https://brickschema.org/schema/BrickTag#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

# The reasoner adds the tags associated with brick:Zone_Air_Temperature_Sensor and all
# of its superclasses to the mybldg:t1 entity.
# For clarity, we are eliding the superclasses that would also be added
mybldg:t1   a   brick:Zone_Air_Temperature_Sensor,
            brick:hasTag    tag:Zone, tag:Air, tag:Temperature,
                            tag:Sensor, tag:Point .
```

### Example: Inverse Relationships

Before reasoning:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   a   brick:Zone_Air_Temperature_Sensor .
mybldg:vav1 a   brick:VAV ;
    brick:hasPoint mybldg:t1 .
```

After reasoning:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

# the inverse relationship (brick:isPointOf) is added by the reasoner.
# Note that for clarity we are eliding the tags and superclasses that would
# be associated with mybldg:t1 and mybldg:vav1
mybldg:t1   a   brick:Zone_Air_Temperature_Sensor ;
    brick:isPointOf mybldg:vav1 .
mybldg:vav1 a   brick:VAV ;
    brick:hasPoint mybldg:t1 .
```

## Performing Inference

Coming soon!

Resources:
- [`brickschema` package support](https://brickschema.readthedocs.io/en/latest/quickstart.html)

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Validation
==========

Documentation coming soon!

Helpful resources:
- [`brickschema` package support](https://brickschema.readthedocs.io/en/latest/validate.html)

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Ontology Versioning
===================

Brick models (digital representations of buildings) are often developed against a specific version of the Brick ontology.
As the Brick ontology evolves, it is important to keep track of which version of the Brick ontology is required for a particular model.

This is accomplished through use of of (a) *ontology declarations*, and (b) *ontology imports*.

All Brick models should explicitly declare the graph which contains the statements modeling the building.
An ontology declaration is a triple of the form:

```ttl
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<graph name> rdf:type owl:Ontology .
```

`<graph name>` is an RDF IRI, and is *usually* the same as the namespace that is used to define the entities in the building:

```ttl
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <urn:my_building#> .

<urn:my_building> a owl:Ontology .
```

Since v1.2, all versions of the Brick ontology have the same namespace: `https://brickschema.org/schema/Brick#`.
This makes it easier to upgrade the Brick ontology used with a particular model without having to change all of the classes, relationships, etc used by that model to use a different namespace.
Instead, we use *ontology imports* to track the dependency on a particular version of Brick.

Ontology imports are properties of the `owl:Ontology` entity which point to other graphs via the `owl:imports` relationship.

```ttl
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bldg: <urn:my_building#> .

<urn:my_building> a owl:Ontology ;
    owl:imports <https://brickschema.org/schema/1.2/Brick#> .
```

The IRI of the *imported* graph has the version of the Brick ontology embedded in it.
This *versioned* IRI points to the version of the Brick ontology indicated in the IRI; for example, `https://brickschema.org/schema/1.2/Brick` is `v1.2` of Brick, `https://brickschema.org/schema/1.3/Brick` is `v1.3` of Brick, and so on.
To update Brick, it is only necessary to change the object of the `owl:imports` statement.
This is possible because the IRI that *imports* Brick will always resolve to a file that uses the *version-agnostic* Brick namespace `https://brickschema.org/schema/Brick#`.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---


Brick Distributions
===================

```{admonition} Note
All distributions are available on the [Brick GitHub Releases page](https://github.com/BrickSchema/Brick/releases).
```

The following distributions are available for the Brick schema on the [Releases](https://github.com/BrickSchema/Brick/releases) page:
- `Brick+imports.ttl` (recommended for end-applications): contains the Brick and RealEstateCore ontologies, as well as all imports; no other dependencies are required
- `Brick.ttl` (recommended for platforms): contains the Brick and RealEstateCore ontologies; all other dependencies must be imported or otherwise included
- `Brick-only.ttl`: contains *only* the Brick ontology; all other dependencies, including RealEstateCore, must be imported or otherwise included
- `Brick+extensions.ttl`: contains the Brick and RealEstateCore ontologies, as well as all extensions currently in the Brick repository. All other dependencies must be imported or otherwise included.

With supplementary files:
- `imports.zip`: contains all imports for the Brick and RealEstateCore ontologies as individual Turtle (`.ttl`) files
- `extensions.zip`: contains all extensions currently in the Brick repository as individual Turtle (`.ttl`) files

The `Brick+imports.ttl` file is convenient for end-applications, as it contains all necessary imports.
This means that applications can just import this file and have access to the entire Brick schema.
This simplifies validation and inference on Brick models because the end-application does not have to resolve or find dependencies.

The `Brick.ttl` file is recommended for software platforms, as it contains only the Brick and RealEstateCore ontologies, allowing for more control over dependencies. 
By keeping the imports separate, software platforms can deduplicate imports and update or manage these dependencies independently of the core Brick schema.

The `Brick-only.ttl` file is useful for applications that only need the Brick ontology and do not require RealEstateCore or other extensions. This is unlikely to be useful for most applications, as RealEstateCore is deeply integrated with Brick and is required for many common use cases.

The `Brick+extensions.ttl` file is useful for applications that require all extensions in the Brick repository. This is unlikely to be useful for most applications, as extensions are typically used on a case-by-case basis.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Using Tags
==========

A **tag** is an atomic term that is used to annotate an entity in a Brick model.
The set of tags associated with a Brick entity can be queried by users and applications; Brick also supports the automatic association of tags with entities based on which Brick class they are an instance of.

In contrast to other metadata efforts such as Project Haystack, Brick does not use tags to define what an entity is.
Tags constitute a ["folksonomic"](https://en.wikipedia.org/wiki/Folksonomy) approach to capturing knowledge.
Because tags are usually just words (e.g. `hot`, `water`, `sensor`, `evaporative`), there is no explicit mechanism to state how a certain word is *intended*.
As a result, while tags are great for to informally annotate properties whose meaning is already known to the user, they are not an effective mechanism for communicating semantic information in a consistent and interpretable manner {cite}`fierro2019beyond`.

```{note}
You may want to review the section on [Inference](../lifecycle/inference) to understand how an external software reasoner supports use of a Brick model.
```

## Querying Tags

Tags are instances of the `brick:Tag` class, and are defined as part of the Brick distribution in the `https://brickschema.org/schema/BrickTag#` namespace (commonly abbreviated as `tag:`).
The full set of Brick tags can be retrieved with the following SPARQL query:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tag: <https://brickschema.org/schema/BrickTag#>

SELECT ?tag ?label WHERE {
    ?tag    a          brick:Tag .
    ?tag    rdfs:label ?label
}
```

### Tags and Brick Classes

Most, if not all, Brick classes have a set of associated tags, which will be "inherited" by any Brick entity which is an instance of that class.
Tags are related to a Brick class via the `brick:hasAssociatedTag` relationship.
For example, to fetch the tags associated with the `brick:Zone_Air_Temperature_Sensor` class, execute the following query:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tag: <https://brickschema.org/schema/BrickTag#>

SELECT ?tag WHERE {
    brick:Zone_Air_Temperature_Sensor brick:hasAssociatedTag ?tag
}
```

### Tags and Brick Entities

After **inference** is applied to a Brick model, Brick entities will inherit tags from their Brick classes.
These inferred tags are related to the Brick entity via the `brick:hasTag` relationship.
The set of tags associated with a Brick entity will be the __union__ of the tags associated with each of the classes it instantiates.

For example, consider an instance of `brick:Zone_Air_Temperature_Sensor` in a Brick model (before inference is applied):

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

mybldg:t1   a   brick:Zone_Air_Temperature_Sensor .
```

After inference, the model will consist of the following:

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix tag: <https://brickschema.org/schema/BrickTag#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix mybldg: <mybuilding#> .

# all parent classes of brick:Zone_Air_Temperature_Sensor are added to the model
mybldg:t1   a   brick:Zone_Air_Temperature_Sensor,
                brick:Air_Temperature_Sensor,
                brick:Temperature_Sensor,
                brick:Sensor,
                brick:Point ;
# here is the union of all tags associated with the above Brick classes
            brick:hasTag    tag:Zone, tag:Air, tag:Temperature,
                            tag:Sensor, tag:Point .
```

To retrieve the set of tags associated with a specific entity, use the following query (remembering to apply inference first):

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#> .
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
PREFIX tag: <https://brickschema.org/schema/BrickTag#> .

SELECT ?tag WHERE {
    mybldg:t1   brick:hasTag ?tag
}
```

### Finding Stuff with Tags

The primary use case of tags is as a form of "keyword search".
Memorizing the whole Brick schema is neither tractable nor expected; tags can be used by user interfaces, automated tools or users themselves to help guide or direct a search for relevant classes or entities in a Brick model.

To find all classes with a given tag (helpful for figuring out which class to use for a new entity), use a variation of the following query (this example finds all classes with the `air` and `temperature` tags):

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#> .
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
PREFIX tag: <https://brickschema.org/schema/BrickTag#> .

SELECT ?class WHERE {
    ?class  brick:hasAssociatedTag tag:Air, tag:Temperature .
}
```

To find all *instances* with a given tag, remember to apply inference, and then execute a query like:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#> .
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
PREFIX tag: <https://brickschema.org/schema/BrickTag#> .

SELECT ?entity WHERE {
    ?entity  brick:hasTag tag:Air, tag:Temperature .
}
```

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Entity Properties
=================

```{note}
This feature is new in Brick v1.2
```

Entity Properties are attributes or characteristics of Brick entities. The values of Entity Properties should change rarely, if ever; if a value is changing regularly, then it is likely better modeled as a Brick Point. Entity properties are useful for modeling static charcteristics such as:
- floor area, room volume
- phase count, phases, and flow of electric meters
- which operational stage a point is associated with
- how the values of a given Point are aggregated
- and many others!


An Entity Property has two parts:
- the *Entity Property* itself, which is a named relationship between a Brick entity and a property value
- the property value, which is its own entity with a set of properties capturing current value, associated units and others

Entity Properties, and their associated classes and relationships, are defined in the `brick` namespace.

The use of Entity Properties generally adheres to the following pattern:

```{image} ../img/entity-property.png
:width: 600px
:align: center
```

## Simple Example

To illustrate the use of entity properties, consider the following models

### Area of a Room

```turtle
:room1  a   brick:Room ;
    brick:area  [
        brick:value  "100"^^xsd:decimal ;
        brick:hasUnit   unit:FT2 ;
    ] ;
.
```

```{note}
The `[]` square brackets above are a [blank node](https://www.w3.org/2007/02/turtle/primer/) notation. Everything in the `[]` is the predicate and object for an *implied* entity that is also the object of the `brick:area` relationship. You can consider the above equivalent to the following:


```turtle
:room1  a   brick:Room ;
        brick:area  :a .
        
:a brick:value  "100"^^xsd:decimal ;
    brick:hasUnit   unit:FT2 .
```

The model here is relatively straight forward. The area is a (usually anonymous) Brick entity with a numerical value (indicated by `brick:value`) and a unit (indicated by `brick:hasUnit`). The area entity is associated with a Brick room through the `brick:area` property.

### Peak Hourly Power Meter

This is the model of a power sensor which tracks the peak hourly real power.

```turtle
:hourly_peak_real_power_meter   a   brick:Power_Sensor ;
    brick:hasUnit   unit:KiloW ;
    brick:aggregate [
        brick:aggregationFunction    "max" ;
        brick:aggregationInterval    "RPT1H" ;
    ] ;
    brick:powerComplexity [
        brick:value  "real" ;
    ]
.
```

This is a little more complex than the earlier example. There are two entity properties associated with the `Power_Sensor` entity. The first is `brick:powerComplexity` which tells us that the sensor measures real power. The second is `brick:aggregate`. The two properties of the `brick:aggregate` value tell us that the sensor's values are aggregated on a 1 hour window; this is indicated by the `brick:aggregationInterval` property. The `brick:aggregationFunction` indicates that the values within that 1 hour interval are aggregated to the maximum of the values in that window.

```{note}
`brick:aggregationInterval` uses the [ISO 8601 Duration specification](https://en.wikipedia.org/wiki/ISO_8601#Durations) to indicate the length of an interval. It also incorporates an `R` prefix to indicate a [repeating duration](https://en.wikipedia.org/wiki/ISO_8601#Repeating_intervals).

Some common other intervals are:
- every 1 hour: `RPT1H`
- every 2 hours: `RPT2H`
- every 15 minutes: `RPT15M`
- every month: `RP1M`
- every 30 days: `RP30D`
```
---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Timeseries Storage
==================

```{note}
This feature is new in Brick v1.2
```

It is possible to embed within a Brick model the metadata indicating where timeseries data is stored and how particular Points are identified --- this enables the automatic retrieval of timeseries data. This metadata is associated with Brick Point instances, which represent sources of data, through the `ref:hasExternalReference` property.
These all use the [`ref-schema`](https://github.com/gtfierro/ref-schema) schema for external references; this schema is packaged with the Brick ontology.

The `ref:hasExternalReference` property relates a Brick Point instance to a `ref:TimeseriesReference` object. This object has exactly one `ref:hasTimeseriesId` property, whose value is a string denoting the identifier or primary key of the instance's data in some database. The database itself is realized as an object and is related to the `ref:TimeseriesReference` through the `ref:storedAt` property.

At this point in time, Brick does not mandate what the properties are on the database instance. As best practices arise, this will be codified in a future release of Brick.

## Simple Example

```turtle
:sensor1    a   brick:Temperature_Sensor ;
    brick:hasUnit unit:DEG_F ;
    ref:hasExternalReference [
        a ref:TimeseriesReference
        ref:hasTimeseriesId   "8f541ba4-c437-43ba-ba1d-5c946583fe54" ;
        ref:storedAt  :database ;
    ] ;
.

:sensor2    a   brick:Temperature_Sensor ;
    brick:hasUnit unit:DEG_F ;
    ref:hasExternalReference [
        a ref:TimeseriesReference ;
        ref:hasTimeseriesId   "38b5fa0e-407e-4a23-8800-6ec4f6d60785" ;
        ref:storedAt  :database ;
    ] ;
.

# the properties on the database instance are non-normative
:database   a   ref:Database ;
    rdfs:label  "Postgres Timeseries Storage" ;
    :connstring "postgres://1.2.3.4/data" ;
.
```
---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

External Representation
=======================

```{note}
This feature is new in Brick v1.3
```

Instances of `Point` in Brick are representations of I/O points and data sources and sinks.
Brick supports relating `Point`s to their representations in external systems, e.g. BACnet networks and timeseries databases.
This allows software to use a Brick model to configure its access to those other systems.
These references are encoded using the [`ref-schema`](https://github.com/gtfierro/ref-schema) schema; a copy of the schema is packaged with the Brick ontology.

The generic relationship `ref:hasExternalReference` can be used to find these other references.
A Brick `Point` can have any number of external references.

Brick currently supports the following external representations:
- `ref:TimeseriesReference`: links a Brick `Point` to its data in a timeseries database
- `ref:BACnetReference`: links a Brick `Point` to its corresponding BACnet object

Examples follow below.


## BACnet

The BACnet reference object is linked to a Brick `Point` with the `ref:hasExternalReference` relationship pointing to a `ref:BACnetReference` object.
There are two possible forms of the BACnet reference object:

Option 1 supports the following fields:
- `bacnet:object-identifier`: the BACnet object ID: `"object-type,object-instance-number"^^bacnet:objectIdentifier`, e.g. `"device,999"^^bacnet:objectIdentifier`
- `bacnet:object-name`: the `name` field: the `description` field for the BACnet object
- `bacnet:object-type`: the BACnet type of the object, e.g. `analog-input`
- `bacnet:description`: the `description` field for the BACnet object
- `bacnet:read-property`: which property to read for the value; defaults to `present-value`

Option 2 supports the BACnet URI scheme:
- `brick:BACnetURI`: defined in clause Q.8 of the BACnet spec: `bacnet:// <device> / <object> [ / <property> [ / <index> ]]`


```turtle
@prefix bldg: <urn:example/> .
@prefix ref: <https://brickschema.org/schema/Brick/ref#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix bacnet: <http://data.ashrae.org/bacnet/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

bldg:sample-device
    a bacnet:BACnetDevice ;
    bacnet:device-instance 123 ;
    bacnet:hasPort [
        a bacnet:Port ;
        bacnet:network-type bacnet:NetworkType.ipv4 ;
        bacnet:ip-address "C0A80164"^^xsd:hexBinary ;        # 192.168.1.100
        bacnet:ip-default-gateway "C0A80101"^^xsd:hexBinary  # router 192.168.1.1
    ] .

# Option 1: explicit fields
bldg:ts1 a brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit unit:DEG_C ;
    ref:hasExternalReference [
        a ref:BACnetReference ;
        bacnet:object-identifier "analog-value,5"^^bacnet:objectIdentifier ;
        bacnet:object-name "BLDG-Z410-ZATS" ;
        bacnet:objectOf bldg:sample-device ;
    ] .

# Option 2: BACnet URI
bldg:ts2 a brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit unit:DEG_C ;
    ref:hasExternalReference [
        a ref:BACnetReference ;
		brick:BACnetURI "bacnet://123/analog-input,3/present-value" ;
        bacnet:objectOf bldg:sample-device ;
    ] .
```

## Timeseries

See the [metadata/timeseries-storage](/metadata/timeseries-storage) section.

## Discovering External Representations

The `ref:hasExternalReference` relationships can be used to find external representations.
Those external references should be annotated with what kind of external reference they are.

Consider the following example:

```turtle
# example.ttl
bldg:ts1 a brick:Zone_Air_Temperature_Sensor ;
    brick:hasUnit unit:DEG_C ;
    ref:hasExternalReference [
        a ref:BACnetReference ;
        bacnet:object-identifier "analog-value,5"^^bacnet:objectIdentifier ;
        bacnet:object-name "BLDG-Z410-ZATS" ;
        bacnet:objectOf bldg:sample-device ;
    ] ;
    ref:hasExternalReference [
        a ref:TimeseriesReference ;
        ref:hasTimeseriesId "756e1623-914f-4415-9000-b1b10ce8f5c9" ;
        ref:storedAt "postgres://1.2.3.4:5432/mydata" ;
    ] .
```

In Python, using the `brickschema` package, external representations can be found and typed as follows:

```python
import brickschema

g = brickschema.Graph()
g.load_file("Brick.ttl")
g.load_file("example.ttl")

g.expand("shacl")

query = """SELECT ?point ?rep ?type WHERE {
    ?point ref:hasExternalReference ?rep .
    ?rep   a ?type .
}
```
---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Software Interfaces for Brick

This section answers the question of how Brick can be used to create data-driven applications.
Rather than relying on a standard API to define interactions with the building instance, Brick provides a set of *references* that describe the interface between Brick and some other API, software library or other digital representation.
This affords a great deal of flexibility in how software can choose to interact with the building and its data.


Recall that the intent of a Brick model is to describe the data sources in a building and their context.
The data sources themselves are represented by instances of the Brick `Point` class, and the context of these data sources is provided by instances of locations, equipment, systems and other building entities.
These instances are associated with data sources through [Brick relationships](/brick/relationships).

This means that a Brick model can be used to find data sources and other entities.
This is usually done through SPARQL queries against the Brick model graph.
The information returned by these queries can be used to configure a piece of software.
For example, a SPARQL query can return:
- the configuration information required to access live or historical data through a time series database
- the parameters for accessing an I/O point on a BMS network
- the parameters for retrieving the geometry of an entity from an IFC model

See the [External Representations](/metadata/external-representations) section for details and examples of how these references are represented in Brick.

## Tutorials

- [Discovering and Retrieving Timeseries Data with Brick and TimescaleDB](https://www.youtube.com/watch?v=kZYNXoiM8gk): tutorial video showing how the Brick timeseries reference can be used to retrieve data from a TimescaleDB database --- the techniques are not TimescaleDB-specific.
- [Brick Data Retrieval Demo](https://github.com/gtfierro/brick-data-retrieval-demo): supporting repository for the above video, providing a Jupyter notebook implementing the data retrieval method in Python. The technique is not TimescaleDB-specific and only one function in the codebase is TimescaleDB-specific. The rest should be easily reusable.

## Brick Platforms

There are two main open-source platforms for interacting with Brick that *do* define APIs:
- [Mortar](https://github.com/gtfierro/mortar): a self-hostable platform for retrieving bulk timeseries data using Brick queries for context. The [Mortar platform website](https://mortardata.org/intro.html) has publicly available data and a [library](https://github.com/SoftwareDefinedBuildings/mortar-analytics) of public implementations of common data analytics
- [Brick Example Server](https://github.com/BrickSchema/brick-example-server): a self-hostable platform demonstrating how a Brick model can be abstracted by an HTTP API

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Database Backends for Brick

In this section, we provide an incomplete list of available commercial and open-source databases which support Brick features.

## Feature List

- **RDF model storage**: does the database support the storage of RDF models (this should be *yes* for all of the below databases)
- **SPARQL support**: does the database support the execution of SPARQL queries? The relevant standards are:
    - [SPARQL 1.1 Query](https://www.w3.org/TR/sparql11-query/) (including property paths)
    - [SPARQL 1.1 Update](https://www.w3.org/TR/sparql11-update/) (the ability to write to the database using SPARQL)
- **Reasoning/Inference**: does the database support [reasoning and inference](../lifecycle/inference) on stored RDF models? Relevant features are:
    - what inference is supported: OWL-DL, OWL-RL, RDFS, OWL-Full, SHACL-AF
    - manual or automatic: is reasoning performed as a manual or batch processing task
- **SHACL support**: does the database support the validation of RDF models using SHACL shapes?
- **Multiple Graphs**: does the database support the storage of multiple graphs, and can those graphs be updated/queried independently?
- **Scaling and Performance**: what are the scaling and performance properties of the database? This includes horizontal scaling capabilities, query performance and storage requirements

## Database List

```{admonition} Info
:class: tip
If there is a missing database or our documentation is incomplete, please [file an issue](https://github.com/BrickSchema/docs/issues/new)
```

### RDFlib + Related Libraries

RDFlib and its related libraries are open-source, production-quality Python libraries for working with RDF data.

Links:
- [RDFlib GitHub](https://github.com/RDFLib/rdflib)
- [pySHACL GitHub](https://github.com/RDFLib/pySHACL)
- [OWL-RL GitHub](https://github.com/RDFLib/OWL-RL)

Features:
- **RDF model storage**: RDFlib supports the storage of RDF models in several [possible backends](https://rdflib.readthedocs.io/en/stable/persistence.html), including an in-memory store by default
- **SPARQL support**: RDFlib contains a complete implementation of SPARQL 1.1 (Query and Update).
- **Reasoning/Inference**: The OWL-RL library supports inference for the RDFS and OWL-RL ontology languages
- **SHACL support**: pySHACL provides a complete implementation of SHACL and SHACL Advanced Features
- **Multiple Graphs**: RDFlib is Python library, so multiple graphs can always be managed as separate Python objects. RDFlib supports named graphs (all graph objects can have a Named Graph URI); most RDFlib backends allow graph objects to be linked to a Named Graph URI
- **Scaling and Performance**: scaling of storage can be provided by the different storage backends supported by RDFlib; additional backends can be added easily. RDFlib's implementation of SPARQL and OWL-RL are not heavily optimized so performance can suffer on larger graphs.

### HodDB

HodDB is an open-source, high-performance, research-quality query processor

Links:
- [HodDB GitHub](https://github.com/gtfierro/hoddb)
- [HodDB paper (BuildSys 2017)](http://people.eecs.berkeley.edu/~gtfierro/papers/hoddb.pdf)
- [Extended HodDB paper (TOSN 2018)](http://people.eecs.berkeley.edu/~gtfierro/papers/hoddb_tosn.pdf)

Features:
- **RDF model storage**: HodDB supports the storage of RDF models on a local filesystem, using BadgerDB
- **SPARQL support**: HodDB supports a subset of SPARQL 1.1, including property path queries and UNION (specifically *not* inserts). See the HodDB papers for a more precise list. HodDB also does not support the SPARQL API protocol, and instead requries use of a specific GRPC-based API
- **Reasoning/Inference**: HodDB supports some basic inference --- namely handling OWL inverse and transitive properties.
- **SHACL support**: HodDB does not support SHACL
- **Multiple Graphs**: HodDB supports the storage of multiple graphs which can be queried separately
- **Scaling and Performance**: Due to the restricted query and update model, HodDB provides excellent SPARQL query performance on graphs up to a few hundred thousand nodes. HodDB currently does not support distributed storage

### Allegrograph

Allegrograph is a proprietary, commercial graph database supporting RDF and related technologies. Allegrograph also provides a free version with limited features

Links:
- https://franz.com/agraph/allegrograph/

Features:
- **RDF model storage**: The paid version of Allegograph supports horizontally scalable storage of RDF models; the base version stores RDF models on a single node
- **SPARQL support**: Allegrograph supports full SPARQL 1.1
- **Reasoning/Inference**: Allegrograph supports both [OWL-RL](https://franz.com/agraph/support/documentation/current/materializer.html) and [RDFS](https://franz.com/agraph/support/documentation/current/reasoner-tutorial.html) languages
- **SHACL support**: Allegrograph supports [SHACL validation](https://franz.com/agraph/support/documentation/current/shacl.html) but does not seem to support SHACL advanced features such as inference
- **Multiple Graphs**: unknown
- **Scaling and Performance**: Allegrograph demonstrates good performance on graphs typical of Brick

### Oxigraph

### Apache Jena

### Blazegraph

### TopBraid

Collections, Systems and Loops
==============================

A *collection* is a group of related entities, typically organized around a fixed use or function.


A collection is modeled as an entity which contains other entities; the relationship between a collection and its contents is `rec:includes`. Collections allow a modeler to associate entities together to make them easier to find later. Systems and Loops are special kinds of Collections.

Brick defines multiple kinds of collections and allows modelers to create their own.

Examples of Brick collections include:
- **Portfolio**: a group of `brick:Site`
- **Loop**: a group of `brick:Equipment` and `brick:Point`
- **System**: a group of `brick:Equipment`, `brick:Point` and `brick:Loop`
- **Photovoltaic Array**: a group of `brick:PV_Panel`

Several kinds of systems are also defined, including `brick:Lighting_System`, `brick:HVAC_System`, `brick:Chilled_Water_System` and `brick:Energy_Generation_System`.
Typically, collections can only contain equipment and points. The main exception is a `Portfolio` which can only contain `brick:Site`.

There are few rules on what kinds of equipment and points can be included in each of the collection types, so the composition of a collection is quite flexible.

```{note}
At this time, collections must be created manually by the modeler, though it is not out of the question to consider a post-processing tool that assigns entities to different collections based on their types and other relationships. For example, this post-processor may add all chilled water coils to a chilled water system, and all hot water coils to a hot water system.
```

## Example: HVAC System

Below is simple example of an HVAC system with AHUs and VAVs, demonsrating use of `brick:HVAC_System` and `brick:Air_Loop` collections.
An HVAC System is a group of equipment, points and loops that implement or handle heating, ventilation and/or air-conditioning in the building.
An Air Loop is a group of equipment and points that are all connected and pass air between them; this does not model arbitrary air flow in a building but rather the system's intended transit of air through the system.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix : <urn:bldg#> .

:hvac_system    a   brick:HVAC_System .
:air_loop_1 a   brick:Air_Loop .
:air_loop_2 a   brick:Air_Loop .

:ahu1   a   brick:AHU ;
    brick:feeds     :vav1, :vav2 ;
    brick:isPartOf :hvac_system, :air_loop_1, :air_loop_2 .
:vav1   a   brick:VAV ;
    brick:hasPart :dmp1 ;
    brick:hasPoint  :sats1 ;
    brick:feeds     :zone1 ;
    brick:isPartOf :hvac_system, :air_loop_1 .
:vav2   a   brick:VAV ;
    brick:hasPart :dmp2 ;
    brick:hasPoint  :sats2 ;
    brick:feeds     :zone2 ;
    brick:isPartOf :hvac_system, :air_loop_2 .
    
:zone1  a   brick:HVAC_Zone .
:zone2  a   brick:HVAC_Zone .
:dmp1 a brick:Damper ;
    brick:hasPoint  :pos1 .
:dmp2 a brick:Damper ;
    brick:hasPoint  :pos2 .
:pos1   a brick:Position_Command .
:pos2   a brick:Position_Command .
:sats1   a brick:Supply_Air_Temperature_Sensor .
:sats2   a brick:Supply_Air_Temperature_Sensor .
```

After applying [inference](lifecycle/inference), several new conclusions can be drawn:
- the members of `:air_loop_1` are `:vav1`, `:ahu1` (indicated explicitly) but also `:dmp1`, `:pos1` and `:sats1`
- likewise, the members of  `:air_loop_2` are `:vav2`, `:ahu2` (indicated explicitly) but also `:dmp2`, `:pos2` and `:sats2`
- the mebmers of `:hvac_system` are the members of the loops above as well as the loops themselves
- *at this time* the zones themselves are not part of the loop **this may change in the future depending on community feedback**

This permits useful discovery queries such as the following: *"What are the contents of the air loop feeding Zone 1?*"

```sparql
SELECT ?content WHERE {
    ?content    brick:isPartOf ?loop .
    ?equip    brick:isPartOf ?loop .
    ?loop   a   brick:Air_Loop .
    ?equip    brick:feeds :zone1 .
}
```

## Custom Collections

```{note}
As of Brick v1.5, custom collections use `rec:Collection` and `rec:includes`. The `brick:Collection` class is deprecated.
```

It is possible for a modeler to create their own ad-hoc collections, depending on how they want to organize entities in the model. The generic `rec:Collection` class is available for this purpose.
These can be created by instantiating a new entity that is of type `rec:Collection`; it is recommended to use `rdfs:label` to name the collection.

Using the example of the HVAC system above, one can create a collection containing just the dampers.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix : <urn:bldg#> .

:my_collection  a   rec:Collection ;
    rdfs:label "All of the dampers" ;
    rec:includes   :dmp1, :dmp2 .
```

```{note}
`brick:Collection` was deprecated in Brick v1.5.0 in favor of `rec:Collection` to remove redundancy between the two ontologies.
```

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---


Connections
===========

```{note}
This feature is new in Brick v1.4 and relies on the [ASHRAE 223P standard](https://open223.info)
```

Brick itself does not include connections (e.g., pipes, ducts, and wires) but as of Brick 1.4, it is possible to model connections using the related ASHRAE 223 ontology.
This mechanism allows more detailed descriptions of the topology of building equipment and subsystems, and permits the association of Brick `Point`s with the connections themselves, as well as where those connections attach to equipment and other entities.


## 223P Connections Overview

```{note}
Text borrowed from the [223p documentation](https://docs.open223.info/explanation/223_overview.html#topology)
```

ASHRAE 223 can be used to describe the topology of the equipment and spaces in a building, but not the geometric details.
Topology refers to the way entities are connected and how some media (e.g. water, air, or electricity) is conveyed between them.
There are several different classes used to describe which entities participate in connections and how they connect: [Connectables](https://explore.open223.info/s223/Connectable.html), which include the entities that are capable of connecting to each other; [ConnectionPoints](https://explore.open223.info/s223/ConnectionPoint.html), which model where Connectables can be connected; and [Connections](https://explore.open223.info/s223/Connection.html), which describe physical things through which the medium is conveyed, like pipes or ducts.
These [Mediums](https://explore.open223.info/s223/Substance-Medium.html) (e.g. gas, electricity, water) are defined as an [EnumerationKind](https://explore.open223.info/s223/EnumerationKind.html) in the standard.
There are also multiple relations used to describe the details of these connections, and how the multiple entities involved in a connection relate to each other.
The figure below summarizes these relations.

```{image} /img/connection-relationships.png
:align: center
:width: 700px
```

Though there are many relations to describe different perspectives of a connection, only [`s223:cnx`](https://explore.open223.info/s223/cnx.html) needs to be manually added to the model, and the rest can be automatically added to the model through the process of model inference.

Note that the `s223:connectedTo` relationship is equivalent to `brick:feeds` because it shows a directional "flow" relationship from one entity to another.

Here is what to remember about modeling connections with 223P.
Equipment can have `ConnectionPoint`s associated with them, using the `s223:hasConnectionPoint` relationship.
`ConnectionPoint`s have a direction (`InletConnectionPoint`, `OutletConnectionPoint`) but can also be bidirectional (`BidirectionalConnectionPoint`).
`ConnectionPoint`s also have a medium associated with them, which is the medium that flows through the connection point.

```{warning}
The current 223P pre-release has changed the name of Medium instances to use "Fluid" where appropriate.
Our examples below are temporarily out of date and will be updated soon.
For example, `s223:Medium-Air` should be `s223:Fluid-Air`.
```

Any `ConnectionPoint` should be associated with an equipment *and* an instance of `Connection`; there are substance-specific versions here, like `s223:Pipe` (water), `s223:Duct` (air), and `s223:Wire` (electricity).
The `s223:cnx` relationship is used to connect two `ConnectionPoint`s, and the direction of the connection is inferred from the direction of the `ConnectionPoint`s.

## Connections on Brick Entities

Brick `Equipment` are now subclasses of `s223:Equipment` in the Brick ontology.
This means that they can have `ConnectionPoint`s and `Connection`s associated with them.


### Common Connection Constructs

Here is a model of a Duct between a brick AHU and a brick VAV

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix s223: <http://data.ashrae.org/standard223#> .

# Define the AHU and VAV
:ahu  a  brick:AHU ;
    rdfs:label "AHU" .
:vav  a  brick:VAV ;
    rdfs:label "VAV" .

# air flow sensor
:air_flow_sensor  a  brick:Air_Flow_Sensor ;
    rdfs:label "Air Flow Sensor" .

# Define the duct
:duct  a  s223:Duct ;
    rdfs:label "duct" ;
    s223:hasMedium s223:Medium-Air ;
    brick:hasPoint  :air_flow_sensor ; # put a sensor in the duct!
    s223:connectsFrom  :ahu ;
    s223:connectsTo  :vav .
```

Here, we need to use `connectsFrom`/`connectsTo` to specify the direction of the connection.

We can also augment this model with connection points which are the physical locations where connections can be made.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <urn:duct_example/> .

<urn:duct_example> a owl:Ontology ;
    owl:imports <https://brickschema.org/schema/1.5/Brick>,
                <https://brickschema.org/extension/s223extension> .

:saf1  a  brick:Supply_Air_Flow_Sensor ;
    rdfs:label "Supply Air Flow Sensor" .

# define the AHU with a air supply connection point
:ahu  a  brick:AHU ;
    rdfs:label "AHU" ;
    s223:hasConnectionPoint  :ahu_air_supply .

:ahu_air_supply  a  s223:OutletConnectionPoint ;
    rdfs:label "AHU air supply" ;
    s223:hasRole s223:Role-Supply ;
    brick:hasPoint :saf1 ; # put the supply air flow sensor at the outlet of the AHU
    s223:hasMedium s223:Medium-Air .

# define the VAV with a air inlet connection point
:vav  a  brick:VAV ;
    rdfs:label "VAV" ;
    s223:hasConnectionPoint  :vav_air_inlet .
:vav_air_inlet  a  s223:InletConnectionPoint ;
    rdfs:label "VAV air inlet" ;
    s223:hasMedium s223:Medium-Air .

# now that we have connection points, we can define the duct using s223:cnx,
# which will infer the rest of the relationship and the correct direction
# of the connection
:duct  a  s223:Duct ;
    rdfs:label "duct" ;
    s223:hasMedium s223:Medium-Air ;
    s223:cnx  :ahu_air_supply, :vav_air_inlet .
```

### Example: Reheat VAV with Hot Water Coil

Here is an example of a reheat VAV with a hot water coil.
Notice that we can attach water as well as air connection points to the VAV, and then use pipes to connect the coil inlet/outlet to the boiler.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix : <urn:rvav_example/> .


<urn:rvav_example> a owl:Ontology ;
    owl:imports <https://brickschema.org/schema/1.5/Brick>,
                <https://brickschema.org/extension/s223extension> .

# define the VAV with air and water connection points
:vav  a  brick:VAV ;
    rdfs:label "VAV" ;
    brick:hasPart :coil, :damper ;
    s223:hasConnectionPoint  :vav_air_inlet, :vav_air_outlet, :vav_water_inlet, :vav_water_outlet .

:vav_air_inlet  a  s223:InletConnectionPoint ;
    rdfs:label "VAV air inlet" ;
    s223:hasMedium s223:Medium-Air .

:vav_air_outlet  a  s223:OutletConnectionPoint ;
    rdfs:label "VAV air outlet" ;
    s223:hasMedium s223:Medium-Air .

:vav_water_inlet  a  s223:InletConnectionPoint ;
    rdfs:label "VAV water inlet" ;
    s223:hasMedium s223:Medium-Water .

:vav_water_outlet  a  s223:OutletConnectionPoint ;
    rdfs:label "VAV water outlet" ;
    s223:hasMedium s223:Medium-Water .


# define the coil with water connection points
:coil  a  brick:Hot_Water_Coil ;
    rdfs:label "Heating Coil" ;
    s223:hasConnectionPoint  :coil_water_inlet, :coil_water_outlet .

:coil_water_inlet  a  s223:InletConnectionPoint ;
    rdfs:label "Coil water inlet" ;
    s223:mapsTo  :vav_water_inlet ;
    s223:hasMedium s223:Medium-Water .

:coil_water_outlet  a  s223:OutletConnectionPoint ;
    rdfs:label "Coil water outlet" ;
    s223:mapsTo  :vav_water_outlet ;
    s223:hasMedium s223:Medium-Water .

# define the damper
:damper  a  brick:Damper ;
    rdfs:label "Damper" .

# define the boiler
:boiler  a  brick:Boiler ;
    rdfs:label "Boiler" ;
    s223:hasConnectionPoint  :boiler_water_supply, :boiler_water_return .

:boiler_water_supply  a  s223:OutletConnectionPoint ;
    rdfs:label "Boiler water supply" ;
    s223:hasMedium s223:Medium-Water .

:boiler_water_return  a  s223:InletConnectionPoint ;
    rdfs:label "Boiler water return" ;
    s223:hasMedium s223:Medium-Water .

# define the pipes
:pipe1  a  s223:Pipe ;
    rdfs:label "Pipe 1" ;
    s223:hasMedium s223:Medium-Water ;
    s223:cnx  :boiler_water_supply, :coil_water_inlet .

:pipe2  a  s223:Pipe ;
    rdfs:label "Pipe 2" ;
    s223:hasMedium s223:Medium-Water ;
    s223:cnx  :coil_water_outlet, :boiler_water_return .
```

The [`mapsTo`](https://explore.open223.info/s223/mapsTo.html) relation is used to indicate that the connection point on the coil is the same as the connection point on the VAV.
This is a form of encapsulation, which can simplify reuse of the model components.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Controllers
===========

```{note}
`brick:Controller`, `brick:controls`/`brick:isControlledBy`, and `brick:hosts`/`brick:isHostedBy` are new in Brick v1.5.
```

A **Controller** is a piece of ICT equipment that supervises and commands one or more physical equipment instances and exposes the points used to do so.
Brick provides two relationship pairs for modeling controllers:

- `brick:controls` / `brick:isControlledBy` — links a Controller to the Equipment it supervises.
- `brick:hosts` / `brick:isHostedBy` — links a Controller (or any ICT Equipment) to the Points it exposes on the network.

These relationships are distinct from `brick:hasPoint`, which expresses that a point *describes* a piece of equipment, regardless of which device exposes it.

## Relationships

`brick:controls`: the *subject* (a `brick:Controller`) commands the *object* (a `brick:Equipment` instance).

`brick:hosts`: the *subject* (a `brick:ICT_Equipment` or `brick:Controller`) exposes the *object* (a `brick:Point`) on the network. This is the physical/logical hosting relationship — the device through which the point is accessed.

A point may be hosted by a controller (`brick:hosts`) and also described as belonging to an equipment (`brick:hasPoint` / `brick:isPointOf`). These two relationships are independent.

## Example: VAV Controller

```turtle
@prefix bldg: <http://example.com/controller#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

bldg:Controller_1 a brick:Controller ;
    rdfs:label "Main Building Controller" ;
    brick:controls bldg:VAV1 ;
    brick:hosts bldg:VAV1_Temperature_Sensor,
                bldg:VAV1_Occupancy_Sensor .

bldg:VAV1 a brick:Variable_Air_Volume_Box ;
    rdfs:label "VAV1" ;
    brick:hasPoint bldg:VAV1_Temperature_Sensor,
                   bldg:VAV1_Occupancy_Sensor ;
    brick:feeds bldg:Zone1 .

bldg:VAV1_Temperature_Sensor a brick:Temperature_Sensor .
bldg:VAV1_Occupancy_Sensor a brick:Occupancy_Sensor .

bldg:Zone1 a rec:HVACZone ;
    rdfs:label "Zone 1" .
```

Here `brick:controls` captures the supervisory relationship and `brick:hosts` captures which device exposes the points on the network.
`brick:hasPoint` remains on the VAV to express that those points describe the VAV — not the controller.

## Combining Controllers with Point Collections

`brick:hosts` and `brick:Point_Collection` serve different purposes and can be used together.
Use `brick:hosts` for the physical/network hosting relationship; use a `brick:Point_Collection` to group points for display, export, or application logic.

```turtle
@prefix bldg: <urn:example/vav#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix unit: <http://qudt.org/vocab/unit/> .

bldg:VAV_1 a brick:Variable_Air_Volume_Box ;
    brick:hasPoint bldg:VAV_1_SAF_Sensor .

bldg:Ctrl_1 a brick:Controller ;
    brick:controls bldg:VAV_1 ;
    brick:hosts bldg:VAV_1_SAF_Sensor .

bldg:VAV_1PointCollection a brick:Point_Collection ;
    rdfs:label "VAV 1 Point Collection" ;
    rec:includes bldg:VAV_1_SAF_Sensor .

bldg:VAV_1_SAF_Sensor a brick:Supply_Air_Flow_Sensor ;
    brick:hasUnit unit:FT3-PER-MIN ;
    brick:isPointOf bldg:VAV_1 .
```

The controller hosts the sensor; the Point Collection organizes it for tools. See [Point Collections](point-collections) for more on organizing points into bundles.

## Query Patterns

Find all equipment controlled by a given controller:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?equipment WHERE {
    ?controller a/rdfs:subClassOf* brick:Controller ;
                brick:controls ?equipment .
}
```

Find which controller hosts a given point:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?controller WHERE {
    ?controller brick:hosts :my_point .
}
```

Find all points hosted by controllers in the model, and the equipment those points describe:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?controller ?point ?equipment WHERE {
    ?controller a/rdfs:subClassOf* brick:Controller ;
                brick:hosts ?point .
    ?point brick:isPointOf ?equipment .
}
```

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Meters
======

```{note}
This feature is new in Brick v1.3
```

Brick provides a basic but flexible model for describing meters, submeter hierarchies, and their relationships to the building.
Meters are equipment (they are subclasses of the Brick `Equipment` class) that measure the consumption or production of energy, steam, gas or other "substances" in the building.
The data produced by meters can be found in instances of the Brick `Point` class that are associated with the Meter.
These include power, energy, water and gas consumption sensors and the like.

## Meter Data

Meters can host several points which correspond to the data produced by the meter. These point instances are related to the meter via the `brick:isPointOf` relationship. See [[metadata/entity-properties]] for some examples of how those points can be described.
(The meter can also be related to the point via the `brick:hasPoint` relationship).

```ttl
bldg:building_energy_sensor a brick:Energy_Sensor ;
    brick:hasUnit unit:KiloW-HR ;
    brick:isPointOf bldg:main-meter ;
    brick:timeseries [ brick:hasTimeseriesId "a7523b08-7bc7-4a9d-8e88-8c0cd8084be0" ] .

bldg:building_peak_demand a brick:Peak_Power_Demand_Sensor ;
    brick:aggregate [ brick:aggregationFunction "max" ;
            brick:aggregationInterval "RP1D" ] ;
    brick:hasUnit unit:KiloW ;
    brick:isPointOf bldg:main-meter ;
    brick:timeseries [ brick:hasTimeseriesId "bcf9a85d-696c-446a-a2ac-97207ecfbc56" ] .

bldg:building_power_sensor a brick:Electric_Power_Sensor ;
    brick:hasUnit unit:KiloW ;
    brick:isPointOf bldg:main-meter ;
    brick:timeseries [ brick:hasTimeseriesId "fd64fbc8-0742-4e1e-8f88-e2cd8a3d78af" ] .

bldg:mybldg a brick:Building ;
    brick:isMeteredBy bldg:main-meter .
bldg:main-meter a brick:Building_Electrical_Meter .
```

## Meters and Submeters

Meters are instances of the `brick:Meter` class or any of its subclasses.
Submeter hierarchies are defined through the `brick:hasSubMeter` and `brick:isSubMeterOf` relationships.
In fact, meters can *only* be related to each other via these relationships.

```ttl
:building_meter a brick:Building_Meter ;
    brick:hasSubMeter :floor-meter-1, :floor-meter-2 .
:floor-meter-1 a brick:Meter .
:floor-meter-2 a brick:Meter .
```

```{warning}
Brick does not describe the nature of the submeter relationship -- only that it exists. If this is a problem, [let us know!](https://github.com/BrickSchema/Brick/issues)
```

To ask for the immediate submeters of a particular meter, one can query the model as follows:

```sparql
SELECT * WHERE {
    :building_meter brick:hasSubMeter ?submeter .
}
```

or more generally, for all immediate parent/child submeter relationships:

```sparql
SELECT ?meter ?submeter WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Meter .
    ?meter brick:hasSubmeter ?submeter .
}
```

One can also ask for all meters that *aren't* submeters of any other meter. Assuming the Brick model is correct, this will avoid double counting:

```sparql
SELECT DISTINCT * WHERE {
    ?meter rdf:type/rdfs:subClassOf* brick:Meter .
    FILTER NOT EXISTS { ?meter brick:isSubMeterOf ?parent }
}
```

### Virtual Meters

It is useful to be able to model "virtual" meters which do not have a physical presence in the building.
Brick supports modeling "virtual" meters using the `brick:isVirtualMeter` Entity Property.
This property can only be "true" for instances of `brick:Meter` or subclasses thereof.

```ttl
:my_virtual_meter a brick:Electrical_Meter ;
    brick:isVirtualMeter [ brick:value true ] .
```

By default, virtual meters look exactly like physical meters so no queries need to be changed if you don't care about the distinction between them.
It is also possible to query *only* virtual meters:

```sparql
SELECT ?meter WHERE {
   ?meter rdf:type/rdfs:subClassOf* brick:Meter ;
          brick:isVirtualMeter/brick:value true .
}
```

or to query only meter which are *not* virtual meters

```sparql
SELECT ?meter WHERE {
   ?meter rdf:type/rdfs:subClassOf* brick:Meter .
   FILTER NOT EXISTS { ?meter brick:isVirtualMeter/brick:value true ] }
}
```


## Associating Meters

Meters can be associated with the entities that they are metering through the `brick:meters` / `brick:isMeteredBy` relationships. These entities can be instances of `brick:Equipment`, `brick:Location` *or* `rec:Collection`.

Metering `brick:Equipment`: useful when the Meter is measuring the consumption/production of a single Equipment instance.

```ttl
:chiller-1 a brick:Chiller ;
    brick:isMeteredBy :chiller-meter .
:chiller-meter rdf:type/rdfs:subClassOf* brick:Electric_Meter .
```

Metering `brick:Location`s: useful when the Meter is measuring the consumption/production of many entities within a single location, e.g. a building or floor or room.

```ttl
:floor-1 a brick:Floor ;
    brick:isLocationOf :camera-1, :camera-2 ;
    brick:isMeteredBy :floor-meter .
:floor-meter rdf:type/rdfs:subClassOf* brick:Electric_Meter .
:camera-1 a brick:Camera .
:camera-2 a brick:Camera .
```

Metering `rec:Collection`s: useful when the Meter is measuring the consumption/production of many entities that are not necessarily grouped by location. Recall that a `rec:Collection` is a named group of entities. This could represent the equipment in a particular air loop, in a particular chilled water system, all of the devices owned by a particular individual, or any other organization.

```ttl
# pv generation systems and pv_arrays are both collections
:pv_generation_system a brick:PV_Generation_System ;
    brick:hasPart :array1 ;
    brick:isMeteredBy :pv_meter .
:array1 a brick:PV_Array .
:panel11 a brick:PV_Panel ;
    brick:isPartOf :array1 ;
    brick:panelArea [ brick:hasUnit unit:M2 ;
            brick:value "5"^^xsd:double ] .
:panel12 a brick:PV_Panel ;
    brick:isPartOf :array1 .
:pv_meter   rdf:type/rdfs:subClassOf*   brick:Electrical_Meter .
```

### Querying these patterns

Brick makes it possible to identify all meters associated with any entity in the Brick model:

```sparql
SELECT ?meter WHERE {
    ?entity brick:isPartOf*/brick:isMeteredBy ?meter .
    ?meter rdf:type/rdfs:subClassOf* brick:Meter .
}
```

Automation and Point Collections
================================

Automation and Point Collections are named groups for organizing building automation entities. They make it possible to describe application-level bundles such as frost detection, ventilation control, room control applications, startup sequences, alarm packages, and operator-facing point groups.

These collections are organizational. They help tools find related entities, but they do not replace the Brick relationships that describe physical composition, point ownership, topology, or control behavior.

```{important}
Do not infer functional semantics from collection membership alone. If a sensor, command, alarm, and piece of equipment are in the same collection, that only says they belong to the same modeled bundle. Use explicit Brick relationships to describe what is measured, commanded, controlled, hosted, or physically part of something else.
```

## At-a-Glance

- Create a `brick:Point_Collection` for point-only groups.
- Create a `brick:Automation_Collection` for mixed automation bundles.
- Put member entities into the collection with `rec:includes`.
- Attach every point to what it describes with `brick:hasPoint` or `brick:isPointOf`.
- Attach every hosted point to its controller or ICT equipment with `brick:hostsPoint` or `brick:isHostedBy`.
- Use `brick:hasPart` only for equipment composition, not collection membership.
- Add `rdfs:label` so tools can present the collection clearly.

## The Two Collection Types

Use `brick:Automation_Collection` for a logical automation bundle. An Automation Collection can include equipment, points, point collections, and other automation collections. It is the right choice when a grouping represents a control application, sequence, alarm package, or other automation function that spans more than just points.

Use `brick:Point_Collection` for a point-only bundle. A Point Collection can include points and nested Point Collections. It is the right choice for operator displays, trend packages, export packages, and other groupings whose members are only points.

Both types use `rec:includes` for membership:

```turtle
@prefix bldg: <urn:example/> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

bldg:VentilationControl a brick:Automation_Collection ;
    rdfs:label "Ventilation control" ;
    rec:includes bldg:AirHandler,
        bldg:VentilationPoints .

bldg:VentilationPoints a brick:Point_Collection ;
    rdfs:label "Ventilation points" ;
    rec:includes bldg:DamperPosition,
        bldg:CO2Setpoint .
```

## Relationship Roles

Use collection membership for organization, and use the normal Brick relationships for the model semantics:

- Use `rec:includes` to put an entity into an Automation Collection or Point Collection.
- Use `brick:hasPart` for physical or structural composition, such as an AHU having a fan or coil.
- Use `brick:hasPoint` / `brick:isPointOf` to attach a point to the equipment, location, or zone it describes.
- Use `brick:hostsPoint` / `brick:isHostedBy` to describe the ICT equipment, controller, gateway, or device that hosts or exposes a point.
- Use `brick:controls` / `brick:isControlledBy` for control relationships between controllers and the equipment they supervise.

Equipment, spaces, and zones can include automation collections with `rec:includes`. This is useful when an asset or zone has a logical application bundle, but the bundle is not a physical part of that asset or zone.

## Choosing the Right Pattern

Use a Point Collection when all of these are true:

- the grouping only contains points or nested point groups
- the grouping is mainly for display, export, trending, configuration, or navigation
- membership should not imply control logic, equipment structure, or a sequence of operation

Use an Automation Collection when any of these are true:

- the grouping includes equipment or other non-point entities
- the grouping represents an automation application, control package, alarm package, or sequence
- the grouping needs nested Point Collections for subsets of points
- the grouping should be associated with an equipment instance, space, or zone as a named application

Define a custom subclass when the grouping has stable meaning in a project or organization. For example, `mpo:FrostDetectionCollection` can be declared as a subclass of `brick:Automation_Collection`.

## Example: Frost Detection

This example models an AHU with a frost detection package. The AHU uses `brick:hasPart` for physical components and `rec:includes` for the logical automation bundle. The points are still attached to the entities they describe with `brick:isPointOf` / `brick:hasPoint`.

```turtle
@prefix bldg: <urn:example/collection#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix mpo: <http://my-private-ontology.com/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

mpo:FrostDetectionCollection a owl:Class ;
    rdfs:subClassOf brick:Automation_Collection ;
    rdfs:label "Frost Detection Collection" ;
    rdfs:comment "An automation collection that includes components for frost detection in an AHU." .

bldg:Ahu a brick:AHU ;
    brick:hasPart bldg:Hcl, bldg:Fan ;
    rec:includes bldg:FrostDetection .

bldg:Hcl a brick:Heating_Coil .

bldg:Fan a brick:Discharge_Fan .

bldg:FrostDetection a mpo:FrostDetectionCollection ;
    rdfs:label "AHU frost detection" ;
    rec:includes bldg:FrostDetectionSensor,
        bldg:FrostDetectionMonitoring,
        bldg:FrostPoints .

bldg:FrostDetectionSensor a brick:Sensor_Equipment ;
    brick:hasPoint bldg:FrostDetected .

bldg:FrostDetectionMonitoring a brick:Enable_Command ;
    brick:isPointOf bldg:Ahu .

bldg:FrostPoints a brick:Point_Collection ;
    rdfs:label "Frost detection points" ;
    rec:includes bldg:FrostDetected,
        bldg:MixedAirTemp .

bldg:FrostDetected a brick:Frost_Sensor ;
    brick:isPointOf bldg:FrostDetectionSensor .

bldg:MixedAirTemp a brick:Mixed_Air_Temperature_Sensor ;
    brick:isPointOf bldg:Ahu .
```

The Automation Collection groups the whole frost detection application. The nested Point Collection groups only the telemetry associated with that application.

## Example: Room Application

Automation Collections can represent applications within a zone or space. In this example, a zone includes an HVAC application. The HVAC application includes equipment and point-only collections for specific application areas.

```turtle
@prefix bldg: <urn:example/room#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

bldg:Zone a rec:Zone ;
    rec:includes bldg:Hvac .

bldg:Room a rec:Room ;
    rec:hasPart bldg:Zone .

bldg:Hvac a brick:Automation_Collection ;
    rdfs:label "HVAC" ;
    rec:includes bldg:RadiantCeiling,
        bldg:RoomTemperatureSetpointDetermination,
        bldg:AirVolumeFlowTracking,
        bldg:VentilationControl .

bldg:RadiantCeiling a brick:Radiant_Panel ;
    rdfs:label "Radiant ceiling" ;
    brick:feeds bldg:Room .

bldg:RoomTemperatureSetpointDetermination a brick:Point_Collection ;
    rdfs:label "Room temperature setpoint determination" ;
    rec:includes bldg:RoomTemperatureSetpoint,
        bldg:RoomTemperatureSetpointShift .

bldg:RoomTemperatureSetpoint a brick:Target_Zone_Air_Temperature_Setpoint ;
    rdfs:label "Room temperature setpoint" ;
    brick:isPointOf bldg:Zone .

bldg:RoomTemperatureSetpointShift a brick:Temperature_Adjust_Sensor ;
    rdfs:label "Room temperature setpoint shift" ;
    brick:isPointOf bldg:Zone .

bldg:AirVolumeFlowTracking a brick:Point_Collection ;
    rdfs:label "Air volume flow tracking" ;
    rec:includes bldg:RoomSupplyAirVolumeFlow,
        bldg:RoomExtractAirVolumeFlowSetpoint .

bldg:RoomSupplyAirVolumeFlow a brick:Supply_Air_Flow_Sensor ;
    rdfs:label "Room supply air volume flow" ;
    brick:isPointOf bldg:Zone .

bldg:RoomExtractAirVolumeFlowSetpoint a brick:Exhaust_Air_Flow_Setpoint ;
    rdfs:label "Present setpoint for room extract air volume flow" ;
    brick:isPointOf bldg:Zone .

bldg:VentilationControl a brick:Point_Collection ;
    rdfs:label "Ventilation control" ;
    rec:includes bldg:PresentVentilationSetpoint,
        bldg:RoomAirQualitySetpointComfort,
        bldg:RoomAirQualitySetpointPreComfort .

bldg:PresentVentilationSetpoint a brick:Damper_Position_Setpoint ;
    rdfs:label "Present ventilation setpoint" ;
    brick:isPointOf bldg:Zone .

bldg:RoomAirQualitySetpointComfort a brick:CO2_Setpoint ;
    rdfs:label "Setpoint room air quality for comfort" ;
    brick:isPointOf bldg:Zone .

bldg:RoomAirQualitySetpointPreComfort a brick:CO2_Setpoint ;
    rdfs:label "Setpoint room air quality for pre-comfort" ;
    brick:isPointOf bldg:Zone .
```

The top-level HVAC collection identifies the room automation application. Its point-only subcollections make it easy for tools to retrieve the points for each part of the application.

## Controllers and Point Collections

Collections do not replace point hosting. A controller should still use `brick:hosts` for the points it exposes, while Point Collections can organize those points for display or configuration. See [Controllers](controllers) for a full treatment of `brick:controls` and `brick:hosts`.


## Query Patterns

The following queries assume standard RDFS subclass reasoning is either available in the graph or handled by the `a/rdfs:subClassOf*` property paths shown below.

Retrieve all members of an Automation Collection, including nested automation and point collections:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rec: <https://w3id.org/rec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?member WHERE {
    ?collection a/rdfs:subClassOf* brick:Automation_Collection ;
                rec:includes+ ?member .
}
```

Retrieve all points in a Point Collection, including points in nested Point Collections:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rec: <https://w3id.org/rec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?point WHERE {
    ?collection a/rdfs:subClassOf* brick:Point_Collection ;
                rec:includes+ ?point .
    ?point a/rdfs:subClassOf* brick:Point .
}
```

Find all automation bundles associated with an AHU and the entities they include:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rec: <https://w3id.org/rec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?collection ?member WHERE {
    ?ahu a/rdfs:subClassOf* brick:AHU ;
         rec:includes ?collection .
    ?collection a/rdfs:subClassOf* brick:Automation_Collection ;
                rec:includes+ ?member .
}
```

Find automation bundles associated with a zone and the points included in those bundles:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rec: <https://w3id.org/rec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?collection ?point WHERE {
    ?zone a rec:Zone ;
          rec:includes ?collection .
    ?collection a/rdfs:subClassOf* brick:Automation_Collection ;
                rec:includes+ ?point .
    ?point a/rdfs:subClassOf* brick:Point .
}
```

Retrieve both physical parts and logical automation bundles from an AHU:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rec: <https://w3id.org/rec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?related WHERE {
    ?ahu a/rdfs:subClassOf* brick:AHU .
    {
        ?ahu brick:hasPart+ ?related .
    } UNION {
        ?ahu rec:includes+ ?related .
    }
}
```

Find the equipment or zone that each point in a collection describes:

```sparql
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rec: <https://w3id.org/rec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?point ?entity WHERE {
    ?collection rec:includes+ ?point .
    ?point a/rdfs:subClassOf* brick:Point ;
           brick:isPointOf ?entity .
}
```

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Terminal Units
==============

```{note}
This page uses Brick and RealEstateCore concepts together, which is a new feature in Brick v1.4
```

This page provides a brief annotated reference model for how to approach modeling terminal units in Brick, along with their points and their relationship to zones and spaces.

```ttl
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix bldg: <urn:my_building/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ref: <https://brickschema.org/schema/brick/ref#> .
@prefix bacnet: <http://data.ashrae.org/bacnet/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

bldg:VAV1 a brick:Variable_Air_Volume_Box_With_Reheat ;
    rdfs:label "VAV 1" ;
    brick:hasPoint bldg:sat1, bldg:saf1, bldg:sp1 ;
    brick:feeds bldg:zone1 .

bldg:sat1 a brick:Supply_Air_Temperature_Sensor ;
    brick:hasUnit unit:DEG_F ;
    ref:hasExternalReference [
        bacnet:object-identifier "analog-value,5"^^bacnet:objectIdentifier ;
        bacnet:object-name "BLDG-Z410-SAT" ;
        bacnet:objectOf bldg:sample-device ;
    ] .

bldg:sp1 a brick:Supply_Air_Temeprature_Setpoint ;
    brick:hasUnit unit:DEG_F ;
    ref:hasExternalReference [
        bacnet:object-identifier "analog-value,7"^^bacnet:objectIdentifier ;
        bacnet:object-name "BLDG-Z410-SAF" ;
        bacnet:objectOf bldg:sample-device ;
    ] .

bldg:saf1 a brick:Supply_Air_Flow_Sensor ;
    brick:hasUnit unit:FT3-PER-MIN ;
    ref:hasExternalReference [
        bacnet:object-identifier "analog-value,6"^^bacnet:objectIdentifier ;
        bacnet:object-name "BLDG-Z410-SAF" ;
        bacnet:objectOf bldg:sample-device ;
    ] .

bldg:zone1 a rec:HVACZone ;
    rec:hasPart bldg:room1 .

bldg:room1 a rec:Office ;
    rdfs:label "Personal Office" ;
    rec:isLocationOf bldg:sensor_box_1 .

bldg:sensor_box_1 a brick:Sensor_Equipment ;
    brick:hasPoint bldg:rmat1 .

bldg:rmat1 a brick:Room_Air_Temperature_Sensor ;
    brick:hasUnit unit:DEG_F ;
    ref:hasExternalReference [
        bacnet:object-identifier "analog-value,8"^^bacnet:objectIdentifier ;
        bacnet:object-name "BLDG-Z410-ROOM" ;
        bacnet:objectOf bldg:sample-device ;
    ] .

# BACnet network stuff
bldg:sample-device
    a bacnet:BACnetDevice ;
    bacnet:device-instance 123 ;
    bacnet:hasPort [
        a bacnet:Port ;
        bacnet:network-type bacnet:NetworkType.ipv4 ;
        bacnet:ip-address "C0A80164"^^xsd:hexBinary ;        # 192.168.1.100
        bacnet:ip-default-gateway "C0A80101"^^xsd:hexBinary  # router 192.168.1.1
    ] .
```

The `bldg:VAV1` entity models the RVAV unit itself, along with its associated data streams (`bldg:sat1`, `bldg:saf1`, and `bldg:sp1`) and which zone it is connected to (`bldg:zone1`).
Each of the data streams is a representation of the BMS point; the `ref:hasExternalReference` relationship connects each Point to the corresponding BACnet object.

The `bldg:zone1` entity is a representation of the HVAC zone; it contains a single room which is a personal office.
This office contains a piece of `Sensor_Equipment`, which is a physical sensing apparatus.
It also has a Sensor entity associated with it, which represents the data source containing temperature data from the sensing apparatus.


---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Extending Brick
===============

This page documents best practices for extending Brick. Extending Brick may include adding new classes, new relationships, new entity properties, new documentation or ontology rules.

Whenever possible, it is recommended to submit extensions to Brick as a pull request on the [GitHub repository](https://github.com/BrickSchema/Brick) so that they can be made available to the broader community. The [CONTRIBUTING.md](https://github.com/BrickSchema/Brick/blob/master/CONTRIBUTING.md) document in the root of the repository contains detailed instructions and guidelines for how to achieve this.

However, in some cases, it may make sense to develop a proprietary or internal extension to Brick which defines classes/relationships that (a) refer to company-specific products or features, (b) refer to internal classes not exposed to customers or users, or (c) are being developed and will be released at a later date.

## Proprietary Extensions

Proprietary extensions should be distributed as an independent RDF file (using a `.ttl`, `.n3` or `.xml` extension) containing the *definitions* of the new classes/relationships in the extension, and their relationship to existing Brick definitions. Relating proprietary extensions to existing Brick definitions is crucial for the correct interpretation/discovery of those classes for any consumers of the extension. This allows, for example, a proprietary definition of a special kind of equipment to be understood as a more specific type of an existing Brick equipment class.

### Namespace

Proprietary extension classes and relationships should be placed in their own namespace. A namespace is a URI prefix which groups the names of the classes, relationships and definitions in a graph; it does not need to be resolvable, but it is generally best practice if an HTTP GET on the namespace URI returns the definition of the extension [^brick]. Once published, a namespace should change rarely, if ever. For a hypothetical "Example Corporation" developing its extensions to Brick, possible namespaces might be: `https://example.com/schema/BrickExtension#`, `https://example.com/brick/extension/` and so on. It is helpful, but not strictly necessary, for the namespace to end in a `#` or `/`.

### Adding Classes and Relationships

The names of the classes and relationships in the extension are suffixed to the namespace chosen above, resulting in a URI which uniquely identifies that class or relationship. For example, to add a ice-making machine class in the "Example Corporation" extension, the class name `IceMachine` may be chosen. Prefixing this with the namespace results in the URI `https://example.com/schema/BrickExtension#IceMachine`.

New classes should have several properties attached to them (see the example below):
- `a owl:Class`: classes should be annotated as instances of OWL classes
- `skos:definition "definition goes here"`: classes should have textual definitions of what they are and how they are intended to be used
- `rdfs:subClassOf <Brick class>`: classes should be related to *existing Brick classes* through the `rdfs:subClassOf` relationship. A extension's class can subclass multiple Brick classes, and those classes can be as generic or specific as required. Some classes, such as `IceMachine`, may have no obvious parent classes in Brick other than `brick:Equipment`. Other classes, such as a specific kind of VFD, may have `brick:VFD` as a parent class instead.

New relationships or properties have similar requirements:
- `a owl:ObjectProperty`: if the relationship has other entities/URIs as values, `ObjectProperty` should be used. If the relationship will have scalar values such as integers, floats or strings, then `owl:DatatypeProperty` is more appropriate
- `skos:definition "definition goes here"`: relationships should have textual definitions of what they are and how they are intended to be used
- `rdfs:domain <class>`: where appropriate, relationships should be annotated with the types of entities that will have the relationship
- `rdfs:range <class>`: where appropriate, relationships should be annotated with the types of entities that will be the object of the relationship (or the datatype of the relationship)
- `rdfs:subPropertyOf <Brick relationship>`: if the extension's relationship is a specialization of an existing Brick relationship, then the extension should indicate which relationship is being specialized.

### Example

Below develops a simple extension defining:
- an `IceMachine` equipment which produces ice,
- a `SnowConeMaker` equipment which *recieves* ice from an `IceMachine` and makes snow cones, and
- a `feedsIce` relationship to indicate which snow cones receive ice from which ice machines. This is a subproperty of the `brick:feeds` relationship

Notice that the `ext` prefix is used in the Turtle file below; the choice of prefix is arbitrary and can be anything convenient. It is recommended to choose a prefix that clearly identifies the extension.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix ext: <https://example.com/schema/BrickExtension#> .

ext:IceMachine  a   owl:Class ;
    rdfs:subClassOf brick:Equipment ;
    skos:definition "A machine made by Example Corp. that produces ice" .

ext:SnowConeMaker   a   owl:Class ;
    rdfs:subClassOf brick:Equipment ;
    skos:definition "A machine made by Example Corp. that uses ice to make snow cones" .

ext:feedsIce    a   owl:ObjectProperty ;
    rdfs:subPropertyOf  brick:feeds ;
    skos:definition "The subject feeds ice to the object" ;
    rdfs:domain ext:IceMachine ;
    rdfs:range  ext:SnowConeMaker .
```


## Creating Extensions

There are two supported ways to create and maintain Brick extensions.

### Direct/Manual Maintenance

One way of extending Brick is to manually maintain an RDF graph file, e.g. serialized in a Turtle (`.ttl`) file.
This can be done by editing the file directly, or using an external ontology
tool like Protege. This is the most flexible option, though maintaining RDF
ontologies "by hand" can be tricky to manage.

The [occupancy extension](https://github.com/gtfierro/brick-occupancy-extension) is one example of how this can be done.

### Python-based Extensions

The other way to extend Brick is to create a Python extension file and compile it with Brick.
The [demo_extension](https://github.com/BrickSchema/Brick/tree/master/demo_extension) folder in the Brick repository contains an example of this.

To compile Brick with this extension, provide the Python import path to the extension's `.py` file when invoking `generate_brick.py`:

```bash
$ python generate_brick.py demo_extension.new_sensors
```

The advantage of this method is that you can use the same Python constructs to implement Brick features like [Entity Properties](../metadata/entity-properties).

<details>
<summary>Example demo extension file</summary>

```python
import rdflib
from datetime import datetime
from bricksrc.namespaces import BRICK, SKOS, SH, XSD, RDFS, DCTERMS, RDF, SDO, OWL

# define the namespace to hold all of our terms, classes, properties, etc
DEMO = rdflib.Namespace("urn:demo_extension#")

# this is the ontology metadata dictionary. It MUST be named 'ontology_definition'
ontology_definition = {
    # required 'namespace' key for ontology declaration
    "namespace": DEMO,
    # optional list of creators (individuals)
    DCTERMS.creator: [
        {
            RDF.type: SDO.Person,
            SDO.email: rdflib.Literal("gtfierro@mines.edu"),
            SDO.name: rdflib.Literal("Gabe Fierro"),
        },
    ],
    # first date of release of extension/ontology
    DCTERMS.issued: rdflib.Literal("2023-07-13"),
    # keep this to ensure the 'modified' date matches when this was last ran
    DCTERMS.modified: rdflib.Literal(datetime.now().strftime("%Y-%m-%d")),
    # a version number for the ontology
    OWL.versionInfo: rdflib.Literal("0.0.1"),
    # a human-readable label for the extension/ontology
    RDFS.label: rdflib.Literal("Demo Extension"),
    # metadata on the publisher of the extension/ontology
    DCTERMS.publisher: {
        # see schema.org for other types, e.g. Consortium or Person
        RDF.type: SDO.Organization,
        SDO.legalName: rdflib.Literal("Not a real org"),
        SDO.sameAs: rdflib.Literal("http://my fake organization website.org"),
    },
    # key-value pairs of prefix to URI of ontology being imported. This will
    # add owl:imports statements to the generated extension
    "imports": {
        "shacl": "http://www.w3.org/ns/shacl#",
    },
    # namespace declarations for any SHACL rules
    "decls": {
        "rdf": RDF,
        "rdfs": RDFS,
        "brick": BRICK,
        "owl": OWL,
        "sh": SH,
        "demo": DEMO,
    }
}

# optional
# the *first* level of this dictionary should have Brick (or otherwise existing)
# classes as keys, and class definition dictionaries as values. Anything further
# nested can follow the normal class dictionary construction.
# This dictionary MUST be named 'classes'
classes = {
    BRICK.Equipment: {
        DEMO["Sensor_Platform"]: {},
        DEMO["PurpleAir_Weather_Station"]: {
            "parents": [BRICK.Weather_Station],
        },
    },
}


# optional
# this dictionary MUST be named 'entity_properties'
entity_properties = {
    DEMO.manufacturer: {
        SKOS.definition: rdflib.Literal("the manufacturer"),
        SH.datatype: XSD.string,
        RDFS.label: rdflib.Literal("manufacturer"),
        "property_of": BRICK.Equipment,
    },
    DEMO.version: {
        SKOS.definition: rdflib.Literal("a MAJOR.MINOR.PATCH version number"),
        SH.node: DEMO.VersionShape,
        RDFS.label: rdflib.Literal("version"),
        "property_of": BRICK.Equipment,
    },
}

# optional
# this dictionary MUST be named 'property_value_shapes'
property_value_shapes = {
    DEMO.VersionShape: {
        "properties": {
            DEMO.versionMajor: {
                SKOS.definition: rdflib.Literal("Major version"),
                "datatype": XSD.integer,
            },
            DEMO.versionMinor: {
                SKOS.definition: rdflib.Literal("Minor version"),
                "datatype": XSD.integer,
            },
            DEMO.versionPatch: {
                SKOS.definition: rdflib.Literal("Patch version"),
                "datatype": XSD.integer,
            },
        },
    },
}
```
</details>

## Using Extensions


Extensions may be distributed in a downloadable file containing the contents of the extension. This extension can be loaded into a graph in the same manner that the Brick ontology definitions can.


Consider the following code snippet which loads the above extension (serialized into a `example_extension.ttl` file) into a graph using the [brickschema](https://brickschema.readthedocs.io/en/latest/index.html) Python package:

```python
import brickschema

g = brickschema.Graph()
g.load_file("Brick.ttl")
g.load_file("example_extension.ttl")
g.load_file("my_building_graph.ttl")
```


In the Brick model file, `my_building_graph.ttl`, the extension classes and relationships can be used with Brick classes and relationships.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix ext: <https://example.com/schema/BrickExtension#> .
@prefix bldg: <urn:snow_cone_factory#> .

bldg:factory    a   rec:Building ;
    brick:buildingPrimaryFunction [ brick:value "Manufacturing/Industrial Plant" ] .

bldg:ice_machine_1  a   ext:IceMachine ;
    brick:hasLocation   bldg:factory ;
    ext:feedsIce    bldg:snow_cone_maker_1 .

bldg:snow_cone_maker_1  a   ext:SnowConeMaker ;
    brick:hasLocation   bldg:factory .
```


## Integrating Extensions into Brick

It may come to pass that a proprietary extension is developed and used internally, but then an equivalent classes/relationships are developed in Brick, or the extension is offered for inclusion in a future release of Brick. In these cases, it is likely that there will be "old" models using the extension's version of the class and "new" models using the Brick version of the same class. These two definitions can be reconciled in a few different ways.

1. `<brick class> owl:equivalentClass <proprietary class>`: this statement can be added to the proprietary extension file to mark the two classes as being *equivalent*. After applying a [reasoner](lifecycle/inference), both classes will be assigned to all instances of either class.
2. `<brick class> rdfs:subClassOf <proprietary class>`: this statement can be added to the proprietary extension file to mark the Brick class as being more specific. This means that instances of the Brick class are *implied* to be instances of the proprietary class, but not vice-versa
2. `<proprietary class> rdfs:subClassOf <brick class>`: this statement can be added to the proprietary extension file to mark the proprietary class as being more specific. This means that instances of the proprietary class are *implied* to be instances of the Brick class, but not vice-versa

[^brick]: Visiting the Brick namespace in the browser will download the latest release of Brick! Try it: [https://brickschema.org/schema/Brick](https://brickschema.org/schema/Brick)

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---


Using Brick and RealEstateCore Together
===============

```{note}
Brick-REC integration was introduced in Brick v1.4 and expanded in v1.5.
```

This document summarizes the changes to Brick that allow it to be used in conjunction with RealEstateCore  (REC).


## Locations

All Brick `Location` classes have been deprecated as of 1.4 and replaced with equivalents in RealEstateCore.
These deprecations appear like this in the Turtle file:

```turtle
brick:Building
  owl:deprecated "true"^^xsd:boolean ;
    brick:deprecatedInVersion "1.4.0" ;
    brick:deprecationMitigationMessage "Brick location classes are being phased out in favor of RealEstateCore classes. For a replacement, consider rec:Building" ;
    brick:isReplacedBy rec:Building ;
.
```

The `brick:isReplacedBy` property indicates the REC class that should be used in place of the deprecated Brick class.
Using a Brick class in a Brick model will raise warnings, not errors, during SHACL validation.
SHACL rules included in Brick will also add the new REC class to the model, so that the model is still valid.

## Relationships

Brick relationships have been mapped to REC relationships where possible.

See this table:

| Brick Relationship | REC Relationship |
|--------------------|------------------|
| `brick:hasLocation` | `rec:locatedIn` |
| `brick:isLocationOf` | `rec:isLocationOf` |
| `brick:feeds` | `rec:feeds` |
| `brick:isFedBy` | `rec:isFedBy` |
| `brick:hasPoint` | `rec:hasPoint` |
| `brick:isPointOf` | `rec:isPointOf` |
| `brick:hasPart` | `rec:hasPart` |
| `brick:isPartOf` | `rec:isPartOf` |
| `brick:hasPart` (collection membership) | `rec:includes` |

## Collections

```{note}
This section describes changes introduced in Brick v1.5.
```

As of Brick v1.5.0, `brick:Collection` has been deprecated in favor of `rec:Collection` to remove redundancy between the two ontologies. Custom collections should now be typed as `rec:Collection` and use `rec:includes` to express membership:

```turtle
@prefix rec: <https://w3id.org/rec#> .
@prefix : <urn:bldg#> .

:my_collection a rec:Collection ;
    rdfs:label "All of the dampers" ;
    rec:includes :dmp1, :dmp2 .
```

All built-in Brick collection classes (e.g. `brick:HVAC_System`, `brick:Air_Loop`, `brick:PV_Array`) are now subclasses of `rec:Collection` rather than the deprecated `brick:Collection`.

---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

Writing Custom SHACL Shapes
===========================

This document describes how to write custom SHACL shapes for use with Brick models.

```{note}
Please file an issue if you would like additional examples or guidance on this topic
```

## Introduction

SHACL is a W3C standard for defining constraints on RDF data.
Brick uses both the base [SHACL](https://www.w3.org/TR/shacl/) vocabulary as well as the [SHACL-AF](https://www.w3.org/TR/shacl-af/) advanced features vocabulary.
These languages can also be used to define custom constraints on Brick models, for example to ensure that all instances of a certain class have a certain property, or to ensure that all instances of a certain class have a certain relationship to another class.

To learn SHACL, we recommend reading the definitions of [SHACL](https://www.w3.org/TR/shacl/) and [SHACL-AF](https://www.w3.org/TR/shacl-af/).
The [RDF Validation book](http://book.validatingrdf.com) is another good resource.

## Examples

### Example: Point list for a RVAV

A simple and common pattern is to define a custom SHACL shape which checks all instances of a class have the correct/required points (e.g., sensor points, setpoints).
Below is an example of a custom SHACL shape for a VAV with reheat which checks that all instances of the `brick:RVAV` class have a heating coil with a valve position command, and a damper with a position command.
It also checks that all instances of the `brick:RVAV` class have a supply air temperature sensor and setpoint.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix : <urn:vav_extension/> .

:RVAV_Point_List a sh:NodeShape ;
    # sh:targetClass is the class that this shape applies to
    sh:targetClass brick:RVAV ;
    # sh:property is a list of constraints that must be satisfied

    # RVAV must have a Heating coil which has a valve position command
    sh:property [
        sh:path brick:hasPart ;
        sh:qualifiedValueShape [
            sh:class brick:Heating_Coil ;
            sh:property [
                sh:path brick:hasPoint ;
                sh:qualifiedValueShape [
                    sh:class brick:Valve_Position_Command ;
                    sh:qualifiedMinCount 1 ;
                ] ;
            ] ;
        ] ;
    ] ;
    # RVAV must have a Damper which has a position command
    sh:property [
        sh:path brick:hasPart ;
        sh:qualifiedValueShape [
            sh:class brick:Damper ;
            sh:property [
                sh:path brick:hasPoint ;
                sh:qualifiedValueShape [
                    sh:class brick:Position_Command ;
                    sh:qualifiedMinCount 1 ;
                ] ;
            ] ;
        ] ;
    ] ;
    # RVAV must have a Supply Air Temperature Sensor
    sh:property [
        sh:path brick:hasPoint ;
        sh:qualifiedValueShape [
            sh:class brick:Supply_Air_Temperature_Sensor ;
            sh:qualifiedMinCount 1 ;
        ] ;
    ] ;
    # RVAV must have a Supply Air Temperature Setpoint
    sh:property [
        sh:path brick:hasPoint ;
        sh:qualifiedValueShape [
            sh:class brick:Supply_Air_Temperature_Setpoint ;
            sh:qualifiedMinCount 1 ;
        ] ;
    ] .
```


### Example: Custom Shape for a Heat Exchanger (with 223P)

In this example, we will define a custom SHACL shape for an energy recovery ventilation (ERV) heat exchanger.
This is an air-to-air heat exhanger with two inputs and two outputs.
We want to define a custom SHACL shape that checks that all instances of this new ERV type have exactly two air inlets and two air outlets.

Brick does not care about inlets and outlets, so extending Brick to support an ERV would only involve ensuring that the ERV has two `brick:feeds` and two `brick:isFedBy` relationships.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix : <urn:erv_extension/> .

:Energy_Recovery_Ventilation_Heat_Exchanger a owl:Class, sh:NodeShape ;
    rdfs:subClassOf brick:Heat_Exchanger ;
    rdfs:label "Energy Recovery Ventilation Heat Exchanger" ;
    sh:property [
        sh:path brick:isFedBy ;
        sh:message "ERV must have exactly two inputs" ;
        sh:minCount 2 ;
        sh:maxCount 2 ;
    ] ;
    sh:property [
        sh:path brick:feeds ;
        sh:message "ERV must have exactly two outputs" ;
        sh:minCount 2 ;
        sh:maxCount 2 ;
    ] .
```

Using [ASHRAE 223P](https://open223.info), we can add additional constraints on the Brick class which represent the actual connection points and get more specific as to what kind of fluid is being exchanged.

```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix s223: <http://data.ashrae.org/standard223#> .
@prefix : <urn:erv_extension/> .

:Energy_Recovery_Ventilation_Heat_Exchanger a owl:Class, sh:NodeShape ;
    rdfs:subClassOf brick:Heat_Exchanger ;
    rdfs:label "Energy Recovery Ventilation Heat Exchanger" ;
    sh:property [ rdfs:comment "An ERV has 2 air outlet connection points."^^xsd:string ;
            sh:minCount 2 ;
            sh:path s223:hasConnectionPoint ;
            sh:qualifiedMinCount 2 ;
            sh:qualifiedValueShape [ sh:class s223:OutletConnectionPoint ;
                    sh:node [ sh:property [ sh:class s223:Fluid-Air ;
                                    sh:path s223:hasMedium ] ] ] ],
        [ rdfs:comment "An ERV has 2 air inlet connection points"^^xsd:string ;
            sh:minCount 2 ;
            sh:path s223:hasConnectionPoint ;
            sh:qualifiedMinCount 2 ;
            sh:qualifiedValueShape [ sh:class s223:InletConnectionPoint ;
                    sh:node [ sh:property [ sh:class s223:Fluid-Air ;
                                    sh:path s223:hasMedium ] ] ] ] .
```






