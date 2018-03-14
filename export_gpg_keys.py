#!/usr/bin/python
#title           :export_gpg_keys.py
#description     :export GPG keys for all repositories and store it in faked api 
#                 structure like satellite
#URL             :https://github.com/4nn0/sat6_scripts
#author          :Andreas Nowak <andreas-nowak@gmx.net>
#notes           :This script is NOT SUPPORTED by Red Hat Global Support Services.
#license         :GPLv3
#==============================================================================
"""
Export GPG Keys from satellite and store it to defined directory

"""
#pylint: disable-msg=R0912,R0913,R0914,R0915

import sys, argparse, os
import simplejson as json
import helpers

def get_gpg(org_id):
    """Get the GPG keys"""

    # Query API to get all GPG keys for organization
    gpg = helpers.get_json(
        helpers.KATELLO_API + "organizations/" + str(org_id) + "/gpg_keys/")

    return gpg['results']

def store_gpg(gpg_result,targetdir,plain):
    """
    Export GPG keys
    """
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    if not plain:
        if not os.path.exists(targetdir + "/katello"):
            os.makedirs(targetdir + "/katello")
        if not os.path.exists(targetdir + "/katello/api"):
            os.makedirs(targetdir + "/katello/api")
        if not os.path.exists(targetdir + "/katello/api/repositories"):
            os.makedirs(targetdir + "/katello/api/repositories")
        fakedir = targetdir + "/katello/api/repositories/"
    for gpg in gpg_result:
        for repo in gpg['repositories']:
            if plain:
                key_file = open(targetdir + "/" + str(repo['id']) + ".gpg", "w")
            else:
                if not os.path.exists(fakedir + str(repo['id'])):
                    os.makedirs(fakedir + str(repo['id']))
                key_file = open(fakedir + str(repo['id']) + "/gpg_key_content", "w")
            key_file.write(gpg['content'])
            key_file.close

def main(args):
    """
    Main routine
    """

    # Who is running this script?
    runuser = helpers.who_is_running()

    # Check for sane input
    parser = argparse.ArgumentParser(
        description='export GPG keys to defined directory')
    # pylint: disable=bad-continuation
    parser.add_argument('-o', '--org', help='Organization (Uses default if not specified)',
        required=False)
    parser.add_argument('-d', '--dryrun', help='Dry Run - Only show GPG keys',
        required=False, action="store_true")
    parser.add_argument('-t', '--target', help='Define target director for keys',
        required=False)
    parser.add_argument('-p', '--plain', help='No faked directory structure for satellite',
        required=False, action="store_true")

    args = parser.parse_args()

    # Set our script variables from the input args
    if args.org:
        org_name = args.org
    else:
        org_name = helpers.ORG_NAME
    if args.plain:
        plain = args.plain
    else:
        plain = False
    dry_run = args.dryrun

    # Get the org_id (Validates our connection to the API)
    org_id = helpers.get_org_id(org_name)

    # Get the list of Content Views along with the latest view version in each environment
    gpg_result = get_gpg(org_id)

    # store GPG keys to given export dir
    if not dry_run:
        if args.target:
            targetdir = args.target
            store_gpg(gpg_result,targetdir,plain)
        else:
            parser.print_help()
    else:
        print json.dumps(gpg_result, indent=4, sort_keys=False)

    # Exit cleanly
    sys.exit(0)

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt, e:
        print >> sys.stderr, ("\n\nExiting on user cancel.")
        sys.exit(1)

