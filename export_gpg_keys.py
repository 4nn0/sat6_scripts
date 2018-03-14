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

def store_gpg(gpg_result,targetdir):
    """
    Export GPG keys in faked satellite structure
    """
    GPGDIR = targetdir
    if not os.path.exists(GPGDIR):
        os.makedirs(GPGDIR)
    if not os.path.exists(GPGDIR + "/katello"):
        os.makedirs(GPGDIR + "/katello")
    if not os.path.exists(GPGDIR + "/katello/api"):
        os.makedirs(GPGDIR + "/katello/api")
    if not os.path.exists(GPGDIR + "/katello/api/repositories"):
        os.makedirs(GPGDIR + "/katello/api/repositories")
    for gpg in gpg_result:
        for repo in gpg['repositories']:
            if not os.path.exists(GPGDIR + "/katello/api/repositories/" + str(repo['id'])):
                os.makedirs(GPGDIR + "/katello/api/repositories/" + str(repo['id']))
            key_file = open(GPGDIR + "/katello/api/repositories/" + str(repo['id']) + "/gpg_key_content", "w")
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
    parser.add_argument('-d', '--dryrun', help='Dry Run - Only show what will be cleaned',
        required=False, action="store_true")
    parser.add_argument('-t', '--target', help='Define target director for keys',
        required=True)

    args = parser.parse_args()

    # Set our script variables from the input args
    if args.org:
        org_name = args.org
    else:
        org_name = helpers.ORG_NAME
    dry_run = args.dryrun

    # Get the org_id (Validates our connection to the API)
    org_id = helpers.get_org_id(org_name)

    # Get the list of Content Views along with the latest view version in each environment
    gpg_result = get_gpg(org_id)

    # store GPG keys to given export dir
    if not dry_run:
        targetdir = args.target
        store_gpg(gpg_result,targetdir)

    # Exit cleanly
    sys.exit(0)

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt, e:
        print >> sys.stderr, ("\n\nExiting on user cancel.")
        sys.exit(1)

