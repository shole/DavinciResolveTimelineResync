# DavinciResolveTimelineResync
Scripts for applying timestamp synced footage to existing timelines with unsynced footage

There is a really annoying deficiency with Davinci Resolve where changing existing timeline footage timestamps is impossible.
I had a project pretty deep into editing and had to solve it somehow so here's a few scripts.

**All of this was made for me and my professipersonal use and need. You are welcome to it. I will not support any of this in any way.**   
This is incredibly hacky and will likely break your project, so think of it as last resort.
I hope you feel this repository like a warm blanket left by the last editor who froze in this hell - less useful but more comforting that you're not alone.
Feel free to fix my mistakes.

- python 3.?
- pip install lxml
- uses the smpte module (included as git submodule)

1. Create a copy of your entire project and call it 'unsynced'. Do all the changes to it you want it to have.
2. Export Mediapool Metadata.csv to the 'unsynced' folder (call it "Metadata.csv")
3. Export all timelines (EDL or FCPXML 1.11) you want retimed to the 'unsynced' folder
4. Create a copy of the 'unsynced' project and call it 'synced'.
5. Retime or replace your footage.
6. Export Mediapool Metadata.csv to 'synced' folder (call it "Metadata.csv")
7. edit edlresync.py / fcpresync.py for your usecase, such as framerate, file renames, special rules for mismatching filenames, etc etc
8. run edlresync.py / fcpresync.py 
9. Check for errors.. this is hacky code so explosions are likely
10. Import from the 'syncedtimelines' folder
11. **Doublecheck all your compositions and footage that they are in their place!** Do not delete your unsynced project until you're sure!

- EDL is much more simple so more likely not to explode - but only supports the most basic edits - no audio tracks detached from video etc - does NOT support any fades/crossfades eventhough they're EDL features and i've commented it out
- FCPXML 1.11 supports much more editing features like independent audio tracks etc, but is also much more complex and WILL explode on complex compositions.. I noticed it exploding with videos on two tracks, which is pretty bad but I only had it in one scene and did not have time to debug as the solution was non-obvious.
