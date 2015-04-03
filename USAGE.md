# Usage Guide

## Scripts

These descriptions are not the actions the script takes, but the actions
the scripts validate and prepare for you.  If the scripts exit code
is zero ([ $? -eq 0 ]) then stdout will have commands for you to execute.

The scripts job isn't to hide the commands from the user.  But to make
sure itis safe for you to run them.  The cli in the tools directory is
uses these script to create a more fluid ui.  You can see another way in
tests/lib.sh to automate the running of these scripts.

This current scripts are for linux only (but both btrfs and zfs).

### Core 

core-gen-arid.sh - determine the next label for archive filesystem
core-gen-key.sh - crypto key generation for luks

### Disk

disk-add-part.sh - add a gpt partition table, and a whole disk partition on it
disk-rem-part.sh - wipe partition table

### Partition

part-add-arfs.sh - create ext4 filesystem on the partition
part-add-luks.sh - create a luks block layer on the partition
part-add-ssfs.sh - will allow creation of btrfs or zfs pools

### System

sys-attach-arfs.sh - add fs to fstab and reload systemd so it can be automounted
sys-detach-arfs.sh - unmount fs and remove from fstab and reload system to clean up

### Snapshots

ssfs-delete-snap.sh - remove a snapshot
ssfs-list-snap.sh   - list all snapshots
ssfs-take-snap.sh   - create a snapshot

## Tools 

### snapmgr

#### help

```bash
# ./tools/snapmgr 
usage: ./tools/snapmgr

COMMANDS
 manage <path> [--policy=XXX] [--noprompt]
 delete <path> <label>
 create <path> [--label=XXX] [--noprompt]
   list <path>

OPTIONS
 policy = [0-9]*[hr,dy,wk,yr]
 label = use a manual id
 noprompt = will take action, no pause for confirmation
```

#### create

Creating snapshots are simple, and independent of the preservation
rules.  The naming convention defaulted is required if the manage
functionality is being used to delete older snapshots.

#### policy

Policy is a different way to prune/manage/remove/delete snapshots.  
A common patter is to have a set of dailys, a set of nightlys, and
a set of weeklys.  We treat snapshot management for what is is, which
is removing snapshots.  And we allow a simple description of the 
natural usage:

```
    policy = timerange ":" density
 timerange = time "-" time | time "+"
      time = digit timespec
  timespec = "mi" | "hr" | "dy" | "wk" | "yr"
   density = timespec | "all" | "none"
```

##### A simple example

If snapshots are create every 30 minutes, and we want to keep them all for 2 days:

     0-2dy: all

After that, we only want to keep one every four hours, for the rest of the week:
   
     2dy-1wk: 4hr

Then it's weekly till the end of the quarter:
 
    1wk-90dy: 1wk

Then lastly every month till the end of the year:

    90dy-1yr: 4wk

Join with "," to make the full policy:

      0 - 2dy : all, 2dy - 1wk : 4hr, 1wk - 90dy : 1wk, 90dy - 1y: 4wk, 1y+ : none

There is this infinite range.  Any time period that isn't captured will be kept, 
hence the "+" support to go back to the epoch :)

**Note** There is no "mo" for month.  Use wk for week or dy for day.

#### noprompt

This allows the python wrapper to take action that the script suggests.
This removes a key protection that input is always confirming action.

Creating a snapshot is a relatively safe operation.  Manage will remove
snapshots that too bundled for the policy.  This should not be done
without due consideration of what could go wrong.

## Example 

### Creating Snapshots

Here we see the tool way to create a snapshot, and below it the scripts that it's using.

The script has a specific date format to generate the default snapshot name, but both the
tool and the script allow the user to override it.

```bash
[root@static tests]# ../tools/snapmgr create /t2/home 

PLEASE CONFIRM THE FOLLOWING ACTION
---
btrfs subvolume snapshot -r /t2/home /t2/home/.snapshot/20150402_02:39:31_-0400
---
Do you wish to launch? y/n y
Success, got output
---
Create a readonly snapshot of '/t2/home' in '/t2/home/.snapshot/20150402_02:39:31_-0400'
---
[root@static tests]# ../scripts/ssfs-take-snap.sh 
usage: ../scripts/ssfs-take-snap.sh path [--label=XXX]
[root@static tests]# ../scripts/ssfs-take-snap.sh /t2/home
# 'snap':'20150402_02:39:51_-0400'
btrfs subvolume snapshot -r /t2/home /t2/home/.snapshot/20150402_02:39:51_-0400
[root@static tests]# echo $?
0
```
