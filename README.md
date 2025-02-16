OpenPnP Job Allocator
=====================

Copyright 2025 SuperHouse Automation Pty Ltd  www.superhouse.tv

Processes OpenPnP job files to split them across multiple machine
configurations. This can be used when a board has some parts
loaded on one machine, and then is moved to a second machine for
additional parts.

The overall job including all placements is defined first, resulting
in several XML files:

 1. One "job" file.
 2. One or more "board" files.
 3. Optionally one "panel" file.

If the project has not been panelised, the job file will directly
reference one or more board files.

If the project has been panelised, the job file will reference a
panel file which in turn will reference the board files.

Once the overall job has been defined with all placements set, the
allocator script is then run with the name of the job file as the
first argument. The script will:

 1. Parse the config files for each PnP machine to find what parts
    they have loaded.
 2. Open the job file, and work down the tree to find all associated
    board and panel files.
 3. Create duplicate sets of files for each PnP machine, including
    job, board, and panel files.
 4. Modify the file sets for each machine to suit the parts they have
    loaded.

You can then open the resulting jobs on the target machines, and run
them independently.

INSTALLATION
------------
To come.


CREDITS
-------
Designed by Jonathan Oxer jon@oxer.com.au


DISTRIBUTION
------------
The specific terms of distribution of this project are governed by the
license referenced below.


LICENSE
-------
Licensed under the GPL v3.0.
