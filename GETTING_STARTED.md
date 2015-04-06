
# Welcome

You will need python3 to run and git to retrieve this tool.  Please refer to
your operating systems documentation or https://git-scm.herokuapp.com/ and
https://www.python.org/ if you are missing them.

## Get the code

This walkthrough is in bash running on linux.

```bash
$ mkdir ~/workspace
$ cd ~/workspace
$ git clone https://github.com/toppk/saveme.git
```


## Tour of the tree

* tools/ - wrapper commands that present a more polished interface.
* scripts/ - all storage access (disk/partition/luks/btrfs/zfs) are
             done in these bash shell scripts
* lib/ - python code for the tools
* tests/ - python and shell test scripts for code under lib/ and scripts/
           These are meant to run in automated (no human confirmation) way.

The tools wrap the scripts, and the scripts do all the storage work.  The
scripts are perfectly usable directly, and there is presently more
functionality there then is wrapped by the tool.

## How to use

As this tool will potentially be running commands the can destroy data, preventing
that is a importent issue.  Please read through our design philosophy
below for more of that story.

This tool can be run anywhere, the scripts do not currently include anything, and
the python code will position itself as long as this structure (./{lib/,scripts/,tools/})
is maintained.  Any keys for crypto will be stored under /etc/saveme/.o

All execution has only been tested running as root.  Many actions would require
this access.

### Scripts

The scripts are named after the action they take.  For example, let's look
at "part-add-luks.sh".  As these scripts run disk and filesystem commands
that require root privledges.

*Note* One important issue is that the scripts currently have a lot of 
hardcoded assumptions about naming.  This will likely necessitate some
restructuring of the scripts as there is no source'ing of one script
to another.

Let's walk through creating a partition table.  We are using sdj 

------------------------------------

```bash
# lsblk  | egrep sdj\|sdm\|NAME
NAME         MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINT
sdj            8:144  0   477G  0 disk  
└─sdj1         8:145  0   477G  0 part  
sdm            8:192  0   1.8T  0 disk
#
```

So no partition table on sdm, but sdj has a partition table.

------------------------------------

```bash
# ./scripts/disk-add-part.sh 
usage: ./scripts/disk-add-part.sh disk
# echo $?
1
#
```

Here when running the script, since it is missing a required parameter
it will return a usage string and a non-zero exit code.  Some commands
do not require a parameter, and will run normally.

------------------------------------

```bash
# ./scripts/disk-add-part.sh /dev/sdm
/dev/sdm is not a block device
#
```

Here we see what we think will be a common error, but we've unified on
not specify the "/dev/" prefix to the partition names.  That is true
for all scripts that require a disk or partition path.

------------------------------------

```bash
# ./scripts/disk-add-part.sh sdm
parted /dev/sdm mktable gpt
parted -a optimal /dev/sdm mkpart primary 0% 100%
#
```

Now we see that running didn't actually execute any commands, it just
displays the commands on the terminal.  So the scripts basically tell
the operator what descructive commands to run, while the scripts is
just doing some extra checks to make sure it is as safe to run as can
be.

------------------------------------

```bash
# ./scripts/disk-add-part.sh sdj
sdj has partitions or is not a disk
# echo $?
2
# 
```

Here you can see that we get a different exit code, and we are not told the
commands that would attempt to recreate the partition table.

------------------------------------

```bash
# ./scripts/disk-add-part.sh sdm > /tmp/create-sdm-part-table.sh
# echo $?
0
#
```
So run the script on the new disk again, this time capturing the output in
a file to run.  Also confirm that the exit code is zero, meaning these commands
are meant for running (and not just an error message).

------------------------------------

```bash
# bash -x /tmp/create-sdm-part-table.sh 
+ parted /dev/sdm mktable gpt
Information: You may need to update /etc/fstab.

+ parted -a optimal /dev/sdm mkpart primary 0% 100%                       
Information: You may need to update /etc/fstab.

#
```

Now run the capture output (this could have been a cut-n-paste), but it is
less dangerous then pasting into root shells :).

------------------------------------

```bash
# lsblk  | egrep sdm\|NAME
NAME         MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINT
sdm            8:192  0   1.8T  0 disk  
└─sdm1         8:193  0   1.8T  0 part  
```

And we can run whatever tools we want to confirm that the partition table
was successfully created.

------------------------------------

### Tools



------------------------------------

```bash
# ./tools/snapmgr 
usage: ./tools/snapmgr

COMMANDS
 manage <path> [--policy=XXX]
   snap <path>
 delete <path> <label>
 create <path> [--label=XXX]
   list <path>

OPTIONS
 policy = [0-9]*[hr,dy,wk,yr]
 label = use a manual id
#
```

Passing no arguments where some are required will display help.

------------------------------------

```bash
# ./tools/snapmgr list /t2/home
20150329_21:56:37_-0400
20150402_02:21:14_-0400
20150402_02:39:31_-0400
#
```

Here we are listing the snapshots.

------------------------------------

```bash
# ./tools/snapmgr create /t2/home

PLEASE CONFIRM THE FOLLOWING ACTION
---
btrfs subvolume snapshot -r /t2/home /t2/home/.snapshot/20150402_20:39:11_-0400
---
Do you wish to launch? y/n y
Success, got output
---
Create a readonly snapshot of '/t2/home' in '/t2/home/.snapshot/20150402_20:39:11_-0400'
---
#
```

Here there is a command being executed.  The tool calls to the script, and is allowing
us to confirm before executing the suggested commands.  There is a prompt waiting for
input where it says "Do you wish to launch? y/n".

------------------------------------

```bash
# ./tools/snapmgr list /t2/home
20150329_21:56:37_-0400
20150402_02:21:14_-0400
20150402_02:39:31_-0400
20150402_20:39:11_-0400
#
```

Here the created snapshot appears.

------------------------------------

```bash
# ./tools/snapmgr delete /t2/home 20150402_02:39:31_-0400

PLEASE CONFIRM THE FOLLOWING ACTION
---
btrfs subvolume delete /t2/home/.snapshot/20150402_02:39:31_-0400
---
Do you wish to launch? y/n y
Success, got output
---
Delete subvolume (no-commit): '/t2/home/.snapshot/20150402_02:39:31_-0400'
---
#
```

Removing a snapshot will prompt again before executing the commands.

------------------------------------

```bash
# ./tools/snapmgr manage /t2/home --policy="0-1yr: 2dy"
Managing snapshots for path="/t2/home" with policy="0-1yr: 2dy" 

PLEASE CONFIRM THE FOLLOWING ACTION
---
btrfs subvolume delete /t2/home/.snapshot/20150402_20:39:11_-0400
---
Do you wish to launch? y/n y
Success, got output
---
Delete subvolume (no-commit): '/t2/home/.snapshot/20150402_20:39:11_-0400'
---
# 
```

Here manage is evaluating all snapshots according to the policy, and since it says you need
two days between snapshots for all snapshots from now to a year old, there is one snapshot
to be removed

------------------------------------

```bash
# ./tools/snapmgr list /t2/home
20150329_21:56:37_-0400
20150402_02:21:14_-0400
#
```
And now there are two snapshots

------------------------------------

## Testing

under tests/ here are the contents:

* highlevel.sh - will be zfs and btrfs tests
* lib.sh - routines for the test suite
* lowlevel.sh - disk -> partition -> luks -> ext4
* lowlevel-teardown.sh -  ext4 -> luks -> partition -> disk
* fullrun.sh - will run through lowlevel -> lowlevel-teardown.  can be used in a for loop!
* output - a directory that is automatically created by the shell tests.  this is to ensure 
           we always capture diagnostics and a listing of all commands we run
* python.py - test the python code, this can run as non-root
* snapshots.sh - will be used to test snapshots
* system.sh - is used to verify the operating system has all the required tools.
              this is recommended to run for compatability

## Design philosophy

* scriptable vs libraries - Since all storage commands are wrapped inside of a shell
script layer.  Users can see and verify the actions, as well as learn the commands
they will need to use one day.  Everything that the tool can do a human can do
manually.

* readable code - scripts are top down linear (no functions, no includes) so that
they can easily be reviewed and therefore trusted.  Keep indirection to a appropiate
minimum, as well as baroque coding styles.

* testing - for both shell and python code.  even at the small size, without automatable
tests, quality would suffer.  make sure that all codepaths have a reproducable entrypoint
to verify code is not stale (which would be misleading)

* defensive - there are no user errors, just bad software causing users to make mistakes
check whatever is common

* convention over configuration - provide rational defaults and require as little as possible.

* users control - users should be able to control the things they should need to, in the simplest
way.  The user should be able to take their ideas and easily translate that to configuration.

## Current standards and conventions

* time specification - all time is internally represented in integer epoch microseconds

* checksums - sha512+size
