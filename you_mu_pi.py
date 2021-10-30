import sys, os, re, subprocess
from ytmusicapi import YTMusic


def print_genres(d):
	print()
	print("GENRE CODES")
	for k in genre_codes:
		print(k, "\t\t", genre_codes[k])
	print("If your genre is not listed, just provide your genre as it is. If you don't provide any genre, you will be prompted to, when an album download is complete. So provide NONE as genre code in the query, for uninterrupted downloads")
	print()

"""
	Depends on:
		ytmusicapi
		yt-dlp
		kid3-cli
"""
def setup_dependencies_linux():

	print("Installing ytmusicapi, yt-dlp, kid3-cli")

	os.system("pip3 install ytmusicapi")

	if hasattr(sys, 'getwindowsversion'):
		print("Looks like you're a Windows user. You will need to manually install the following dependencies for now")
		print("  yt-dlp\thttps://github.com/yt-dlp/yt-dlp#release-files")
		print("  kid3-cli\thttps://kid3.kde.org/#download")
		return

	os.system("sudo wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp")
	os.system("sudo chmod a+rx /usr/local/bin/yt-dlp")

	os.system("sudo add-apt-repository ppa:ufleisch/kid3")
	os.system("sudo apt-get update")
	os.system("sudo apt-get install kid3-cli")

ytmusic = YTMusic()

genre_codes = {
	"NONE": "Unknown",
	"PDM": "Progressive Death Metal",
	"BM": "Black Metal",
	"TDM": "Technical Death Metal",
	"PM": "Progressive Metal",
	"SW": "Synthwave",
	"R": "Rock",
	"HR": "Hard Rock",
	"EM": "Extreme Metal",
	"MDM": "Melodic Death Metal",
	"HM": "Heavy Metal",
	"PR": "Progressive Rock",
	"MC": "Mathcore",
	"IM": "Industrial Metal",
	"I": "Industrial"
}

print("Welcome to YoutubeSurf! This is a work in progress and so far allows downloading albums by a simple query and tags the downloaded mp3 files automatically with:")
print(" - Title")
print(" - Track number")
print(" - Artist")
print(" - Album")
print(" - Year")
print(" - Genre")
print("\nOn the TODO list is support for browsing songs on the command line, selecting specific songs to download, downloading entire artist discogs, downloading album art and maybe cleaning up existing untagged music files")
print("Piracy is illegal. Use this script at your own risk. I do not condone piracy in any way whatsoever.")
print()

music_dir = input("Enter your full music directory\n>>> ")
print()

print("Enter your download queries one by one in the form 'Album Name_Artist Name_Genre Code (or) Genre' (Genre field is optional)'\n Enter i to setup dependencies\n Enter d when done\n Enter h to show available genre codes\n Enter q to quit")
queries = []
while True:
	i = input(">>> ")
	if i == "i":
		setup_dependencies_linux()
	elif i == "d": 
		break
	elif i == "q":
		quit()
	elif i == "h":
		print_genres(genre_codes)
	else:
		queries.append(i)

print()
print("Queued " + str(len(queries)) + " albums to be downloaded. Proceed? (y for yes, any key for no)")
confirm = input(">>> ")

if not confirm.lower() == 'y':
	print("User interrupt. Exiting...")
	quit()

print()

for query in queries:
	try:
		album, artist, genre = query.split("_")
	except:
		try:
			album, artist = query.split("_")
			genre = ""
		except:
			print("Bad input query: " + query + "\nSkipping...\n")
			continue

	results = ytmusic.search(query = album + " " + artist, filter = "albums")
	album_matches = [x for x in results if x['category'].lower() == 'albums' or x['category'].lower() == 'top results']

	if(len(album_matches) == 0):
		print("OOPS! Could not find " + album + " by " + artist + ". Ensure spelling is correct. Continuing...")
		print()
		continue

	album_data = album_matches[0]
	album_data = ytmusic.get_album(album_data['browseId'])
	album_playlist_id = album_data['audioPlaylistId']

	# In case user was wrong
	album = album_data['title']
	year = album_data['year']

	os.chdir(music_dir)
	path = os.path.join(artist, album.replace("/", "_"))
	os.makedirs(path, exist_ok=True)
	os.chdir(path)

	print("Downloading...")
	os.system("yt-dlp -x --audio-format mp3 https://music.youtube.com/playlist?list=" + album_playlist_id)
	print("Download complete!")

	print("Cleaning filenames and setting track tags...")
	audio_files = [file for file in os.listdir() if file.endswith(".mp3")]
	audio_files.sort(key = os.path.getctime)

	i = 1
	for file in audio_files:
		new_file = re.sub(" \\[[A-Za-z0-9_-]*\\]\\.mp3", ".mp3", file)
		os.rename(file, new_file)
		subprocess.call(['kid3-cli', '-c', r'select "'+new_file+r'"', '-c', r'set title "'+new_file.rstrip(".mp3").replace("_", "/")+r'"', '-c', r'set "track number" '+str(i), '-c', 'save', '-c', 'select none'])
		i = i+1

	print("Setting common album tags...")
	if genre == "": 
		print("Enter the genre or genre code\n Enter h to view available genre codes")
		while True:
			genre = input(">>> ")
			if genre == "h":
				print()
				print("GENRE CODES")
				for k in genre_codes:
					print(k, "\t\t", genre_codes[k])
				print("If your genre is not listed, just provide your genre as it is. If you don't provide any genre, you will be prompted to, when an album download is complete. So provide NONE as genre code in the query, for uninterrupted downloads")
				print()
			else: 
				break

	genre = genre if genre not in genre_codes else genre_codes[genre]
	subprocess.call(['kid3-cli', '-c', 'select *.mp3', '-c', r'set artist "'+artist+r'"', '-c', r'set album "'+album+r'"', '-c', r'set genre "'+genre+r'"', '-c', 'set date '+year, '-c', 'save', '-c', 'select none'])

	print("File setup done for " + album + " by " + artist)
	print()

print("All albums downloaded! Enjoy")
