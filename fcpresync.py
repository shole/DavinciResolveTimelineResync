import os
import csv
from smpte.SMPTE import SMPTE
# import xml.etree.ElementTree as ET
from lxml import etree as ET

s = SMPTE()
s.fps = 50
s.df = False

synced = "synced"
unsynced = "unsynced"


# if your file names change, change it here
def filerename(unsyncedfile):
	filename = unsyncedfile.replace('_aud.mp4', '.mov')
	if (filename == '0014.mov' or filename.endswith("/0014.mov")):
		filename = filename.replace("0014.mov", "11C-D1-0014.mov")
	return filename

# modify timeline name - resolve adds a postfix that i don't want
def timelinerename(name):
	return name.replace(" (Resolve)", "xx")

def conditionaliterable(o):
	return o if isinstance(o, list) else [o]

def fractionaltoseconds(f):
	left, right = f.replace('s', '').split('/')
	return float(left) / float(right), int(right)

def secondstofractional(s, fraction=50):
	return str(int(s * fraction)) + "/" + str(fraction)+"s"

def timetoframes(time):
	return time * 50

def framestotime(frames):
	return float(frames) / 50

syncedmeta = dict()
with open(synced + '/Metadata.csv', encoding='UTF-16', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row['File Name'].lower().endswith(".mov") or row['File Name'].lower().endswith(".mp4"):
			file = dict()
			file['file'] = filerename(row['File Name'])
			file['duration'] = row['Duration TC']
			file['start'] = row['Start TC']
			file['startTime'] = framestotime(s.getframes(row['Start TC']))
			file['end'] = row['End TC']
			file['endTime'] = framestotime(s.getframes(row['End TC']))
			syncedmeta[file['file']] = file

unsyncedmeta = dict()
with open(unsynced + '/Metadata.csv', encoding='UTF-16', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row['File Name'].lower().endswith(".mov") or row['File Name'].lower().endswith(".mp4"):
			file = dict()
			file['file'] = filerename(row['File Name'])
			file['duration'] = row['Duration TC']
			file['durationTime'] = framestotime(s.getframes(row['Duration TC']))
			file['start'] = row['Start TC']
			file['startTime'] = framestotime(s.getframes(row['Start TC']))
			file['end'] = row['End TC']
			file['endTime'] = framestotime(s.getframes(row['End TC']))
			unsyncedmeta[file['file']] = file


def retime(file, v):
	# synced = unsynced - unsyncedtimecode + syncedtimecode
	unsynced = unsyncedmeta[filerename(file)]['startTime']
	synced = syncedmeta[filerename(file)]['startTime']
	resynced = v - unsynced + synced
	print("   unsynced media " + s.gettc(timetoframes(unsynced)) + " <")
	print(" >  current value " + s.gettc(timetoframes(v)))
	print("     synced media " + s.gettc(timetoframes(synced)) + " <")
	print(" > resynced value " + s.gettc(timetoframes(resynced)))
	return resynced


def retimefractional(file, f):
	# return "XXXXX"
	value, fraction=fractionaltoseconds(f)
	return secondstofractional(retime(file, value), 50)


fcps = [f.name for f in os.scandir(unsynced) if f.is_dir() and f.name.endswith('.fcpxmld')]
for fcp in fcps:
	# if "scene10-250116B" not in fcp:  # only do testfile
	# 	continue
	print()
	print()
	print(fcp)
	fcpfile = None
	abortfile = False

	tree = ET.parse(unsynced + "/" + fcp + "/Info.fcpxml")
	root = tree.getroot()

	# timeline name
	for node in root.findall('.//event'):
		node.set('name', timelinerename(node.get('name')))
	for node in root.findall('.//project'):
		node.set('name', timelinerename(node.get('name')))

	print("asset")
	for node in root.findall('.//asset'):
		name = filerename(node.get('name'))
		node.set('name', name)
		print(name)

		starttime = node.get('start')
		node.set('start', retimefractional(name, starttime))

		# node.set('duration', secondstofractional(unsyncedmeta[filerename(name)]['durationTime']))

	print('media-rep')
	for node in root.findall('.//media-rep'):
		name = filerename(node.get('src'))
		node.set('src', name)
		print(name)

	print("clip")
	for node in root.findall('.//clip'):
		name = filerename(node.get('name'))
		node.set('name', name)
		print(name)

		starttime = node.get('start')
		node.set('start', retimefractional(name, starttime))

		starttime = node.get('offset')
		node.set('offset', retimefractional(name, starttime))

	print('asset-clip')
	for node in root.findall('.//asset-clip'):
		name = filerename(node.get('name'))
		node.set('name', name)
		print(name)

		starttime = node.get('start')
		node.set('start', retimefractional(name, starttime))

		# this is actual TIMELINE offset - don't change this!
		# starttime = node.get('offset')
		# if (starttime is not None):
		# 	print('offset')
		# 	node.set('offset', retimefractional(name, starttime))

		starttime = node.get('audioStart')
		if (starttime is not None):
			print('audioStart')
			node.set('audioStart', retimefractional(name, starttime))

	print("video")
	for node in root.findall('.//video'):
		name = filerename(node.find('..').get('name'))
		print(name)
		starttime = node.get('start')
		node.set('start', retimefractional(name, starttime))
		starttime = node.get('offset')
		node.set('offset', retimefractional(name, starttime))

	print("audio")
	for node in root.findall('.//audio'):
		name = filerename(node.find('..').get('name'))
		print(name)
		starttime = node.get('start')
		node.set('start', retimefractional(name, starttime))
		starttime = node.get('offset')
		node.set('offset', retimefractional(name, starttime))
		node.set('srcCh', "1")

	# print("spine")
	# for node in root.findall('.//spine'):
	# 	if node.find('..').get('name') is not None and node.get('offset') is not None:
	# 		name = filerename(node.find('..').get('name'))
	# 		print(name)
	# 		starttime = node.get('offset')
	# 		node.set('offset', retimefractional(name, starttime))

	if (not abortfile):
		if not os.path.exists("syncedtimelines"):
			os.mkdir("syncedtimelines")
		if not os.path.exists("syncedtimelines/" + fcp):
			os.mkdir("syncedtimelines/" + fcp)

	tree.write("syncedtimelines/" + fcp + "/Info.fcpxml", encoding='utf-8', xml_declaration=True)
