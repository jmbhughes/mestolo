|        **Mestolo**        |                                                                                                    "Dishing up data, one spoonful at a time."                                                                                                    |
|:-------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| ![mestolo logo](logo.png) |  Mestolo means "ladle" in Italian. The `mestolo` package was designed to prepare data using `punchbowl`, the PUNCH mission's calibration code. It is mission agnostic and can run any pipeline with complex dependencies and scheduling needs.   |

## Features

> [!WARNING]
> This code is under rapid development and likely has bugs. Use caution.

- [x] add priorities and priority escalation
- [x] handles input and output passing
- [x] make scheduling aware of dependencies
- [x] check if files are fully consumed and can be removed from the graph
- [x] handle instances and time constraints on ingredients
- [x] handle problem where graph could grow perpetually due to some silly configuration
- [x] properly close queue and processes on cooking end
- [ ] add steps to recipes and check if asked to shutdown between steps... also more logging
- [ ] add monitor for status and resource usage
- [ ] for recipes that are prefect flows, link to the prefect interface?
- [ ] fully integrate database tracking
- [ ] add AI credit for logo
- [ ] create documentation
- [ ] make easier to define using decorators
- [ ] more completely test
- [ ] test with mocked database in specific scenarios
- [ ] allow optional or expiring dependencies
- [ ] add more realistic constraints for PUNCH where an input type is repeated at many times
- [ ] allow using old, consumed files to satisfy new products
- [ ] makes processes clean themselves up instead of periodically checking
- [ ] checks for dependency cycles on start
- [ ] add a sensor mode for triggering on new files (particularly for PUNCH raw --> level 0)
