import tkinter
import customtkinter
from tkinter import *
from tkinter.ttk import *
from pytube import YouTube
from PIL import Image, ImageTk
import CTkMessagebox
from CTkMessagebox import CTkMessagebox
from sclib import SoundcloudAPI, Track, Playlist

import os
import re
import shutil
import time
import urllib.request

import requests
import spotipy
from moviepy.editor import *
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from pytube import YouTube
from rich.console import Console
from spotipy.oauth2 import SpotifyClientCredentials
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# System Settings:

SPOTIPY_CLIENT_ID = '724c55a50b0c4a458a795a2b8f641a34'
SPOTIPY_CLIENT_SECRET = '62d522ffb74d42f0963c25c0f84a1bd1'


client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


customtkinter.set_appearance_mode("dark")
#customtkinter.set_default_color_theme("dark")
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# App Frame:

app = customtkinter.CTk()
app.geometry("1080x720")
app.title("desire")
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UI Elements:

takeoverbig = customtkinter.CTkFont(family="Takeover", size=60)
takeoversmall = customtkinter.CTkFont(family="Ubuntu-Title", size=20)
creditfont = customtkinter.CTkFont(family="Takeover", size=12)
ubuntusmall = customtkinter.CTkFont(family="Ubuntu-Title", size=12)
title = customtkinter.CTkLabel(app, text="desire tool", font=takeoverbig)
title.pack(padx=10, pady=0)
divider = customtkinter.CTkLabel(app, text='___________________________________________________________________')
divider.pack()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Spotify Download Functions:
def showYouTubeSuccessMessage():
    successmsg = CTkMessagebox(title='SUCESS', message="SUCCESSFULLY DOWNLOADED FILE", icon="check", option_1="Ok")

def showYouTubeErrorMessage():
    errormsg = CTkMessagebox(title='ERROR', message="LINK IS INVALID OR IS NOT ALLOWED FOR DOWNLOAD", icon="cancel", option_1="Cancel")
def main():
    url = validate_url(spotifylink.get().strip())
    if "track" in url:
        songs = [get_track_info(url)]
    elif "playlist" in url:
        songs = get_playlist_info(url)

    start = time.time()
    downloaded = 0
    for i, track_info in enumerate(songs, start=1):
        search_term = f"{track_info['artist_name']} {track_info['track_title']} audio"
        video_link = find_youtube(search_term)

        downloadingpreview = customtkinter.CTkLabel(
            app, text=f"[magenta]({i}/{len(songs)})[/magenta] DOWNLOADING '[cyan]{track_info['artist_name']} - {track_info['track_title']}[/cyan]'...", font=takeoversmall
        )
        audio = download_yt(video_link)
        if audio:
            set_metadata(track_info, audio)
            os.replace(audio, f"../music/{os.path.basename(audio)}")
            downloaded += 1
        else:
            downloadingpreviewalreadyexists = customtkinter.CTkLabel(app, text="FILE ALREADY EXISTS. SKIPPING...", font=takeoversmall)
    shutil.rmtree("../music/tmp")
    os.chdir("../music")
    downloadlocationpreview = customtkinter.CTkLabel(app, text=f"Successfully Downloaded {audio.title}\nFile Location: {os.getcwd()}", font=takeoversmall)
    downloadlocationpreview.pack()
    showYouTubeSuccessMessage()
    
def validate_url(sp_url):
    if re.search(r"^(https?://)?open\.spotify\.com/(playlist|track)/.+$", sp_url):
        return sp_url

    raise ValueError("INVALID SPOTIFY URL.")
    showYouTubeErrorMessage()

def get_track_info(track_url):
    res = requests.get(track_url)
    if res.status_code != 200:
        raise ValueError("INVALID SPOTIFY TRACK URL.")
        showYouTubeErrorMessage()

    track = sp.track(track_url)

    track_metadata = {
        "artist_name": track["artists"][0]["name"],
        "track_title": track["name"],
        "track_number": track["track_number"],
        "isrc": track["external_ids"]["isrc"],
        "album_art": track["album"]["images"][1]["url"],
        "album_name": track["album"]["name"],
        "release_date": track["album"]["release_date"],
        "artists": [artist["name"] for artist in track["artists"]],
    }

    return track_metadata

def get_playlist_info(sp_playlist):
    res = requests.get(sp_playlist)
    if res.status_code != 200:
        raise ValueError("INVALID SPOTIFY PLAYLIST URL.")
        showYouTubeErrorMessage()
    pl = sp.playlist(sp_playlist)
    if not pl["public"]:
        raise ValueError(
            "CAN'T DOWNLOAD PRIVATE PLAYLISTS. CHANGE YOUR PLAYLIST'S STATE TO PUBLIC."
        )
        showYouTubeErrorMessage()
    playlist = sp.playlist_tracks(sp_playlist)

    tracks = [item["track"] for item in playlist["items"]]
    tracks_info = []
    for track in tracks:
        track_url = f"https://open.spotify.com/track/{track['id']}"
        track_info = get_track_info(track_url)
        tracks_info.append(track_info)

    return tracks_info

def find_youtube(query):
    phrase = query.replace(" ", "+")
    search_link = "https://www.youtube.com/results?search_query=" + phrase
    count = 0
    while count < 3:
        try:
            response = urllib.request.urlopen(search_link)
            break
        except:
            count += 1
    else:
        raise ValueError("PLEASE CHECK YOUR INTERNET CONNECTION AND TRY AGAIN LATER.")

    search_results = re.findall(r"watch\?v=(\S{11})", response.read().decode())
    first_vid = "https://www.youtube.com/watch?v=" + search_results[0]

    return first_vid

def prompt_exists_action():
    global file_exists_action
    if file_exists_action == "SA":  # SA == 'Skip All'
        return False
    elif file_exists_action == "RA":  # RA == 'Replace All'
        return True

    filealreadyexists = customtkinter.CTkLabel(app,text="THIS FILE ALREADY EXISTS.", font=takeoversmall)
    filealreadyexists.pack()
    while True:
        resp = (
            input("replace[R] | replace all[RA] | skip[S] | skip all[SA]: ")
            .upper()
            .strip()
        )
        if resp in ("RA", "SA"):
            file_exists_action = resp
        if resp in ("R", "RA"):
            return True
        elif resp in ("S", "SA"):
            return False
        invalidresponse = customtkinter.CTkLabel(app, font=takeoversmall, text="---INVALID RESPONSE---")

def download_yt(yt_link):
    ytdownload = YouTube(yt_link)
    # remove chars that can't be in a windows file name
    ytdownload.title = "".join([c for c in ytdownload.title if c not in ['/', '\\', '|', '?', '*', ':', '>', '<', '"']])
    # don't download existing files if the user wants to skip them
    exists = os.path.exists(f"../music/{ytdownload.title}.mp3")
    #if exists and not prompt_exists_action():
        #return False

    # download the music
    VIDEO = ytdownload.streams.filter(only_audio=True).first()
    vid_file = VIDEO.download(output_path="../music/tmp")
    # convert the downloaded video to mp3
    base = os.path.splitext(vid_file)[0]
    audio_file = base + ".mp3"
    mp4_no_frame = AudioFileClip(vid_file)
    mp4_no_frame.write_audiofile(audio_file, logger=None)
    mp4_no_frame.close()
    os.remove(vid_file)
    os.replace(audio_file, f"../music/tmp/{ytdownload.title}.mp3")
    audio_file = f"../music/tmp/{ytdownload.title}.mp3"
    return audio_file

def set_metadata(metadata, file_path):

    mp3file = EasyID3(file_path)

    # add metadata
    mp3file["albumartist"] = metadata["artist_name"]
    mp3file["artist"] = metadata["artists"]
    mp3file["album"] = metadata["album_name"]
    mp3file["title"] = metadata["track_title"]
    mp3file["date"] = metadata["release_date"]
    mp3file["tracknumber"] = str(metadata["track_number"])
    mp3file["isrc"] = metadata["isrc"]
    mp3file.save()

    # add album cover
    audio = ID3(file_path)
    with urllib.request.urlopen(metadata["album_art"]) as albumart:
        audio["APIC"] = APIC(
            encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read()
        )
    audio.save(v2_version=3)


if __name__ == "__main__":
    file_exists_action = ""
    console = Console()
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# YouTube Download Functions:


def startYTAudioDownload():
    try:
   # os.chdir("../music")
     ytAudioLink = youtubelink.get()
     YOUTUBEAUDIOOBJECT = YouTube(ytAudioLink)
     audio = YOUTUBEAUDIOOBJECT.streams.get_audio_only()
     audio.download(output_path="../music")
     os.chdir("../music")
     #shutil.rmtree("../music/audio")
    except:
        showYouTubeErrorMessage()
    downloadytaudiolocationpreview = customtkinter.CTkLabel(app, text=f"Successfully Downloaded {YOUTUBEAUDIOOBJECT.title}\nFile Location: {os.getcwd()}", font=takeoversmall)
    downloadytaudiolocationpreview.pack()
    showYouTubeSuccessMessage()

def startYTVideoDownload():
    try:
        ytVideoLink = youtubelink.get()
        ytVideoObject = YouTube(ytVideoLink)
        video = ytVideoObject.streams.get_highest_resolution()
        #os.chdir("../music/video")
        video.download(output_path="../music")
        os.chdir("../music")
        
    except:
        showYouTubeErrorMessage()
    downloadytvideolocationpreview = customtkinter.CTkLabel(app, text=f"Successfully Downloaded {ytVideoObject.title}\nFile Location: {os.getcwd()}", font=takeoversmall)
    downloadytvideolocationpreview.pack()
    showYouTubeSuccessMessage()
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 # YouTube Tool:

youtubelabel = customtkinter.CTkLabel(app, text="YOUTUBE!", font=takeoversmall, text_color='#DD6763')
youtubelabel.pack(padx=10, pady=10)



youtube_url = tkinter.StringVar()

youtubelink = customtkinter.CTkEntry(app, width=350, height=40, textvariable=youtube_url, placeholder_text="Paste Youtube Link Here", font=takeoversmall, placeholder_text_color='white' )
youtubelink.pack(padx=5, pady=2.5)

youtubeAudioDownload = customtkinter.CTkButton(app, width=350, height=40, fg_color="gray", hover_color="#347ECB", border_color='#2659D9', text="🎵 Audio Download", font=takeoversmall,  command=startYTAudioDownload)
youtubeAudioDownload.pack(padx=5 ,pady=2.5)

youtubeVideoDownload = customtkinter.CTkButton(app, width=350, height=40, fg_color="gray", hover_color="#347ECB", border_color='#2659D9', text="📺 Video Download", font=takeoversmall, command=startYTVideoDownload)
youtubeVideoDownload.pack(padx=5,pady=2.5)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Spotify Tool:

spotifylabel = customtkinter.CTkLabel(app, text='SPOTIFY!', font=takeoversmall, text_color='#77EAA0')
spotifylabel.pack(padx=10, pady=2.5)

spotify_url = tkinter.StringVar()
spotifylink = customtkinter.CTkEntry(app, height=40, width=350, textvariable=spotify_url, placeholder_text="PASTE SPOTIFY LINK HERE", font=takeoversmall, placeholder_text_color='white')
spotifylink.pack(padx=5, pady=2.5)
spotifyDownload = customtkinter.CTkButton(app, width=350, height=40, fg_color='gray', hover_color='#347ECB', border_color='#2659D9', text='🎵 AUDIO DOWNLOAD', font=takeoversmall, command=main)
spotifyDownload.pack(padx=5, pady=2.5)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SoundCloud Tool:

soundcloudlabel = customtkinter.CTkLabel(app, text='SOUNDCLOUD!', font=takeoversmall, text_color='#FFB45D')
soundcloudlabel.pack(padx=10, pady=2.5)

soundcloud_url = tkinter.StringVar()
soundcloudlink = customtkinter.CTkEntry(app, height=40, width=350, textvariable=soundcloud_url, placeholder_text="PASTE SOUNDCLOUD LINK HERE", font=takeoversmall)
soundcloudlink.pack(padx=5, pady=2.5)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 # SoundCloud Functions :


# Singular Track Download Function
def trackdownload():
    api = SoundcloudAPI()  
    tracksingle = api.resolve(soundcloudlink.get())
    try:
        assert type(tracksingle) is Track

        filename = f'./{tracksingle.artist} - {tracksingle.title}.mp3'

        with open(filename, 'wb+') as file:
            tracksingle.write_mp3_to(file)
        showYouTubeSuccessMessage()
    except:
        showYouTubeErrorMessage
# Playlist Download Function
def playlistdownload():
    api = SoundcloudAPI()  
    trackplaylist = api.resolve(soundcloudlink.get())
    try:
        assert type(trackplaylist) is Track

        filename = f'./{trackplaylist.artist} - {trackplaylist.title}.mp3'

        with open(filename, 'wb+') as file:
            trackplaylist.write_mp3_to(file)
    except:
        showYouTubeErrorMessage()
    downloadsclocationpreview = customtkinter.CTkLabel(app, text=f"Successfully Downloaded {trackplaylist.title}\nFile Location: {os.getcwd()}", font=takeoversmall)
    downloadsclocationpreview.pack()
    showYouTubeSuccessMessage()

soundclouddownload = customtkinter.CTkButton(app, width=350, height=40, fg_color='grey', hover_color='#347ECB', border_color='#2659D9', text='🎵 AUDIO DOWNLOAD', font=takeoversmall, command=playlistdownload)
soundclouddownload.pack(padx=5, pady=2.5)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Credits

credits = customtkinter.CTkLabel(app, text='made by: \n danesh', font=creditfont)
credits.pack(side=BOTTOM, pady=16)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Run App:

app.mainloop()
