import os
import csv
from smpte.SMPTE import SMPTE

s = SMPTE()
s.fps = 50
s.df = False

synced="synced"
unsynced="unsynced"

# if your file names change, change it here
def filerename(unsyncedfile):
	return unsyncedfile.replace('_aud.mp4','.mov')


syncedmeta=dict()
with open(synced+'/Metadata.csv', encoding='UTF-16', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row['File Name'].lower().endswith(".mov") or row['File Name'].lower().endswith(".mp4"):
			file=dict()
			file['file']=filerename(row['File Name'])
			file['duration']=row['Duration TC']
			file['start']=row['Start TC']
			file['end']=row['End TC']
			syncedmeta[file['file']]=file

unsyncedmeta=dict()
with open(unsynced+'/Metadata.csv', encoding='UTF-16', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		if row['File Name'].lower().endswith(".mov") or row['File Name'].lower().endswith(".mp4"):
			file=dict()
			file['file']=filerename(row['File Name'])
			file['duration']=row['Duration TC']
			file['start']=row['Start TC']
			file['end']=row['End TC']
			unsyncedmeta[file['file']]=file

print(unsyncedmeta)

edls = [f.name for f in os.scandir(unsynced) if f.is_file() and f.name.endswith('.edl')]
for edl in edls:
	print()
	print()
	print(edl)
	edlfile=None
	with open(unsynced+"/"+edl, "r") as handle:
		edlfile=handle.readlines()

	abortfile=False
	index=len(edlfile)-1
	while index>0:
		if (edlfile[index].startswith('* FROM CLIP')): # filename def
			print()

			if ("CLIP NAME: Transition" in edlfile[index]):
				print("!!!!! Transitions not supported !!!!!")
				abortfile=True
				break

			medianame=edlfile[index][len('* FROM CLIP NAME: '):].strip()
			print(medianame)
			edlfile[index]='* FROM CLIP NAME: '+filerename(medianame)
			index=index-1
			if (edlfile[index][len("003  AX       V     ")]=='D'):
				print("!!!!! crossfades not supported !!!!!")
				index = index - 1

			"001  AX       V     C        19:09:06:39 19:09:19:00 00:00:00:00 00:00:12:11  "
			# print(edlfile[index])
			metadata=edlfile[index][:len("001  AX       V     C        ")]
			# print(metadata)
			startTC=edlfile[index][len("001  AX       V     C        "):len("001  AX       V     C        00:00:00:00")]
			print("edit start " + startTC)
			endTC=edlfile[index][len("001  AX       V     C        00:00:00:00 "):len("001  AX       V     C        00:00:00:00 00:00:00:00")]
			print("edit end " + endTC)

			print( "unsynced media "+unsyncedmeta[filerename(medianame)]['start'] )
			print( "synced media "+ syncedmeta[filerename(medianame)]['start'] )

			# unsynced - edit + synced

			syncedframes=s.getframes( syncedmeta[filerename(medianame)]['start'] )
			unsyncedframes=s.getframes( unsyncedmeta[filerename(medianame)]['start'] )
			startframes=s.getframes( startTC )
			endframes=s.getframes( endTC )

			synced_startframes= startframes - unsyncedframes + syncedframes
			synced_endframes= endframes - unsyncedframes + syncedframes

			synced_startTC=s.gettc(synced_startframes)
			synced_endTC=s.gettc(synced_endframes)

			editdata=edlfile[index][len("001  AX       V     C        19:09:06:39 19:09:19:00"):]
			# print(editdata)

			newline=metadata + synced_startTC + " " + synced_endTC + editdata
			print(newline)
			edlfile[index]=newline
		index=index-1

	if (not abortfile):
		with open("syncedtimelines"+"/"+edl, "w") as handle:
			handle.writelines(edlfile)
			print("wrote "+"syncedtimelines"+"/"+edl)











