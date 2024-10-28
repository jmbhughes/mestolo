# Mestolo

| Mestolo                   |   "Serving up data, one spoonful at a time."                                                                                                                                                                                                                                                                           |
|:--------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| ![mestolo logo](logo.png) | Mestolo means "ladle" in Italian. The `mestolo` package was designed to serve up data from the `punchbowl`, the PUNCH mission's calibration code. It has been designed in an agnostic way and can be applied to any pipeline with complex dependencies and scheduling needs. |

## Features

> [!WARNING]
> This code is being rapidly developed and likely has bugs. Use caution.

- [ ] checks for dependency cycles on start
- [x] handles input and output passing
- [ ] makes processes clean themselves up instead of periodically checking
- [x] make scheduling aware of dependencies
- [x] check if files are fully consumed and can be removed from the graph
- [ ] allow using old, consumed files to satisfy new products
- [x] handle instances and time constraints on ingredients
- [x] handle problem where graph could grow perpetually due to some silly configuration
- [x] properly close queue and processes on cooking end
- [ ] add steps to recipes and check if asked to shutdown between steps... also more logging
- [ ] add monitor for status and resource usage
- [ ] for recipes that are prefect flows, link to the prefect interface?
