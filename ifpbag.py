import sys
import bagit

bag_dir = sys.argv[1]

bag = bagit.make_bag(bag_dir, {'Contact-Name': 'Dean Kavanagh','Source-Organization': 'Irish Film Institute','Contact-Email': 'dkavanagh@irishfilm.ie'})
print bag.entries
