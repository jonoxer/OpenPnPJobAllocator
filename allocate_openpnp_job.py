#!/usr/bin/python3
#  To do:
#  * Accumulate a list of parts that were enabled but are no longer enabled
#    for any machine, and therefore may need hand placement.
#  * Better configuration for the machine configs. Currently hard-coded.
#  * Refactor code to allow an arbitrary number of machines to be targeted.
#  * Document setup process.
#
#  Process:
#  * Parse two OpenPnP machine config files
#  * Read a job file
#  * Find a panel file reference, if it exists
#  * If it does, read it to find a board file reference
#  * If it doesn't, find a board file reference directly
#  * Open the board file
#  * Create a set of job files for each target machine
#  * Update the job files to enable only the parts loaded on that machine
#
#  Bugs:
#  * Doesn't rewrite self-referenced filenames in updated filesets.

import os.path
import sys
from bs4 import BeautifulSoup
import copy

print('OpenPnP Job Allocator')
if len(sys.argv) == 1:
    print('Please provide the name of an OpenPnP job file.')
    quit()

job_file_name = sys.argv[1]

print('Processing OpenPnP job file "' + job_file_name + '"')

# Check if the job file exists
if(os.path.isfile(job_file_name)):
    print("Found job file")
else:
    print("The requested job file doesn't exist.")
    quit()


############# Find what parts are available on the target machines ##################
# Read feeder setup for machine 1
with open('machine-config-1.xml', 'r') as fp_config:
    machine_1 = fp_config.read()
fp_config.close()
feeder_data_1 = BeautifulSoup(machine_1, "xml")
machine1_parts = []
for feeder in feeder_data_1.find_all('feeder', attrs={'enabled':'true'}):
    machine1_parts.append(feeder['part-id'])


# Read feeder setup for machine 2
with open('machine-config-2.xml', 'r') as fp_config:
    machine_2 = fp_config.read()
fp_config.close()
feeder_data_2 = BeautifulSoup(machine_2, "xml")
machine2_parts = []
for feeder in feeder_data_2.find_all('feeder', attrs={'enabled':'true'}):
    machine2_parts.append(feeder['part-id'])


############## Open the requested job file ###################################
with open(job_file_name, 'r') as fp_jobfile:
    jobfile = fp_jobfile.read()
fp_jobfile.close()
job_data = BeautifulSoup(jobfile, "xml")

new_job_file_1_name = job_file_name[:-3] + 'machine1.xml'
new_job_file_2_name = job_file_name[:-3] + 'machine2.xml'

machine1_job = copy.deepcopy(job_data)
machine2_job = copy.deepcopy(job_data)


############## Find the panel file we need ###################################
panelised = False
panel_file_source = job_data.find('object', attrs={'class':'org.openpnp.model.PanelLocation'})

# If there is a panel file we take a detour to process it
if(panel_file_source != None):
    panelised = True
    print("panel: ")
    print(panel_file_source)
    panel_file_name = panel_file_source['file-name']

    # Check if the panel file exists
    if(os.path.isfile(panel_file_name)):
        print("Found panel file " + panel_file_name)
    else:
        print("The requested panel file doesn't exist.")
        quit()

    with open(panel_file_name, 'r') as fp_panelfile:
        panel_file_contents = fp_panelfile.read()
    fp_panelfile.close()
    panel_data = BeautifulSoup(panel_file_contents, "xml")
    #print(panel_data)

############ Prepare the new panel files
    new_panel_file_1_name = panel_file_name[:-3] + 'machine1.xml'
    new_panel_file_2_name = panel_file_name[:-3] + 'machine2.xml'

    machine1_panel = copy.deepcopy(panel_data)
    machine2_panel = copy.deepcopy(panel_data)

############# Replace the panel file references in the new job files #######################
    for panel in machine1_job.find_all('object', attrs={'class':'org.openpnp.model.PanelLocation'}):
        panel['file-name'] = new_panel_file_1_name

    for panel in machine2_job.find_all('object', attrs={'class':'org.openpnp.model.PanelLocation'}):
        panel['file-name'] = new_panel_file_2_name


############ Find the board file we need in the panel  #####################################
# Below only finds the first board listed in the panel. Each panel can have multiple
# boards, and they can even be different. We should find all boards listed and process
# each one separately.
    board_file_source = panel_data.find('object', attrs={'class':'org.openpnp.model.BoardLocation'})
    board_file_name = board_file_source['file-name']
    print("Got a board file from the panel: ")
    print(board_file_name)
    #print(board_file)

else:
############ Find the board file we need in the job  #####################################
    # Get the board name from the job file
    board_file_source = job_data.find('object', attrs={'class':'org.openpnp.model.BoardLocation'})
    board_file_name = board_file_source['file-name']
    print("Got a board file from the job: ")
    print(board_file_name)


############ Check if the board file exists ##############################################
if(os.path.isfile(board_file_name)):
    print("Found board file " + board_file_name)
else:
    print("The requested board file doesn't exist.")
    quit()

############ Prepare the new board files ####################################################
with open(board_file_name, 'r') as fp_boardfile:
    board = fp_boardfile.read()
fp_boardfile.close()
board_data = BeautifulSoup(board, "xml")

new_board_file_1_name = board_file_name[:-3] + 'machine1.xml'
new_board_file_2_name = board_file_name[:-3] + 'machine2.xml'

machine1_board = copy.deepcopy(board_data)
machine2_board = copy.deepcopy(board_data)

############ Update placements in the new board files #######################################
# Find all placements that are NOT fiducials, and are set to enabled
for placement in machine1_board.find_all('placement', attrs={'enabled':'true', 'type':'Placement'}):
    if(placement['part-id'] not in machine1_parts):
        placement['enabled'] = 'false'

for placement in machine2_board.find_all('placement', attrs={'enabled':'true', 'type':'Placement'}):
    if(placement['part-id'] not in machine2_parts):
        placement['enabled'] = 'false'

############# Write out the new board files #######################################
#print(board_data.prettify())
outfile = open(new_board_file_1_name, 'w')
outfile.write(machine1_board.prettify())
outfile.close()

outfile = open(new_board_file_2_name, 'w')
outfile.write(machine2_board.prettify())
outfile.close()


if(panelised):
############# Replace the board file references in the new panel files ##################
    for board in machine1_panel.find_all('object', attrs={'class':'org.openpnp.model.BoardLocation'}):
        board['file-name'] = new_board_file_1_name

    for board in machine2_panel.find_all('object', attrs={'class':'org.openpnp.model.BoardLocation'}):
        board['file-name'] = new_board_file_2_name

############# Write out the new panel files #########################
    outfile = open(new_panel_file_1_name, 'w')
    outfile.write(machine1_panel.prettify())
    outfile.close()

    outfile = open(new_panel_file_2_name, 'w')
    outfile.write(machine2_panel.prettify())
    outfile.close()

else:
############# Replace the board file references in the new job files #######################
    for board in machine1_job.find_all('object', attrs={'class':'org.openpnp.model.BoardLocation'}):
        board['file-name'] = new_board_file_1_name

    for board in machine2_job.find_all('object', attrs={'class':'org.openpnp.model.BoardLocation'}):
        board['file-name'] = new_board_file_2_name




############# Write out the new job files ##########################################
outfile = open(new_job_file_1_name, 'w')
outfile.write(machine1_job.prettify())
outfile.close()

outfile = open(new_job_file_2_name, 'w')
outfile.write(machine2_job.prettify())
outfile.close()
