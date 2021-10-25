import requests
from bs4 import BeautifulSoup
import string
import csv
#movie.csv

print("begin movies")
# response1 = requests.get('https://www.hindigeetmala.net/movie/')
suffixes = [c for c in string.ascii_lowercase]
suffixes.insert(0, "0-9")
# print(suffixes)

movies_header = ["Title", "Year", "Number of Songs", "Film Director", "Film Producer",
                 "Film Cast", "Lyricist", "Music Director", "Singer", "External Links",
                 "Watch Full Movie"]

songs_header = ["Artist", "Title", "Rating", "Number of Votes", "Movie Title"]

with open('movies.csv', 'w', newline='') as csvfile:
    moviewriter = csv.writer(csvfile, delimiter=';')
    moviewriter.writerow(movies_header)
    
with open('songs.csv', 'w', newline='') as csvfile:
    songwriter = csv.writer(csvfile, delimiter=';')
    songwriter.writerow(songs_header)

for suf in suffixes:
    url = 'https://www.hindigeetmala.net/movie/' + str(suf) + ".php"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    total_pages = soup.find_all("td", {"class": "alcen w720 bg7f"})
    
    total_pages = total_pages[0].getText()
    index = total_pages.find("Page") + 10
    if index == 9: #"Page" not found, only one page
        total_pages = 1
    else:
        total_pages = int(total_pages[index:])
    
#     if suf != "0-9": continue
    
    for i in range(1, total_pages + 1):
        time.sleep(1) #pause for 1 second for each page
        sub_url = url
        if i != 1:
            sub_url = url + "?page=" + str(i)
        response = requests.get(sub_url)
        page_soup = BeautifulSoup(response.content, 'html.parser')
        movie_table = page_soup.find_all("td", {"class": "w25p h150"})
    
        for movie in movie_table:
            #setup basic info
#             if movie != movie_table[0]: continue
            #get title and year
            #two links per movie, 2nd one contains
            #title and year released in the text
            title_and_year = movie.find_all("a")[1].getText() 
            
            temp = title_and_year.split("(")
            title = temp[0][:-1] #remove ending whitespace before "("
            
            if len(temp) == 1: 
                year = None
            else:
                year = temp[1][:-1]  #remove ending parens
                
#             print(title)
            
            #get movie url and soup
            movie_url = movie.find("a", {"class": "thumb"})['href']
            movie_url = "https://www.hindigeetmala.net" + str(movie_url)
            movie_response = requests.get(movie_url)
            movie_soup = BeautifulSoup(movie_response.content, 'html.parser') 
            
            ##scrape data for songs.csv of each movie
            num_songs = movie_soup.find("meta", itemprop="numTracks")
            if num_songs == None: #DMCA'd movie page, skip
                continue 
                
            songs = movie_soup.find("table", {"class": "w760", "itemtype": "http://schema.org/MusicAlbum"})
            songs = songs.find_all("tr", itemprop="track")
            
            for song in songs:
                song_title = song.find("span", itemprop="name").getText()
                song_title = song_title[1:-1] #remove whitespace
#                 print(song_title)
                
                artists_list = song.find_all("span", itemprop="byArtist")
                if len(artists_list) == 0: artists = "N/A"
                else: 
                    artists = ""
                    for artist in artists_list:
                        artists += artist.getText()
                        if artist != artists_list[-1]:
                            artists += ", "
                            
                rating = song.find("span", itemprop="ratingValue").getText()
                votes = song.find("span", itemprop="ratingCount").getText()
                
                song_info = [artists, song_title, rating, votes, title]
                
                with open('songs.csv', 'a', newline='') as csvfile:
                    songwriter = csv.writer(csvfile, delimiter=';')
                    songwriter.writerow(song_info)

            
            #songs done, scrape data for movies.csv
                
            num_songs = num_songs['content']
            movie_info = movie_soup.find("table", {"class": "b1 allef w100p"})
            
            entries = movie_info.find_all("td") #get all table entries
            #loop through all entries in table and check text
            
            info = {"Film Director": None, "Film Producer": None, "Film cast": None, 
                    "Lyricist": None, "Music Director": None, "Singer": None, 
                    "External Links": None, "Watch Full Movie": None}
            
            for i in range(len(entries) // 2): #evens are keys
                key = entries[i * 2].getText()[:-2] #remove :
                
                if key == "Film cast": #parse into a giant string
                    result = ""
                    cast = entries[i * 2 + 1].find_all("span", itemprop="name")
                    for person in cast:
                        result += person.getText()
                        if person != cast[-1]:
                            result += ", "
#                     info[key] = result
                elif key == "Watch Full Movie" or key == "External Links":
                    result = ""
                    links = entries[i * 2 + 1].find_all("a")
                    for link in links:
                        result += link['href']
                        if link != links[-1]:
                            result += ", "
                else:
                    result = entries[i * 2 + 1].getText()
#                     print(info[key])
                info[key] = result

            result_list = [title, year, num_songs]
            for key in info:
                if info[key] == None:
                    result_list.append("N/A")
                else:
                    result_list.append(info[key])
            
            #write to csv
            with open('movies.csv', 'a', newline='', encoding="utf-8") as csvfile: #create file if doesn't exist
                moviewriter = csv.writer(csvfile, delimiter=';')
                moviewriter.writerow(result_list)
        
print("movies done")