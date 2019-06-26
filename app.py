# /* Copyright (C) Phattharachon Thongrit - All Rights Reserved
#  * Unauthorized copying of this file, via any medium is strictly prohibited
#  * Proprietary and confidential
#  * Written by Phattharachon Thongrit <phattharachon.t@gmail.com>, June 2019
# */

from flask import Flask,request
import config,json,isodate,iso8601,csv,re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

app = Flask(__name__)

def get_authenticated_service():
    youtube = build(config.api_servicename, config.api_version,
                    developerKey=config.developer_key)
    return youtube



def regEX(title):
  regexIgnore = re.compile(pattern=keyword)
  videoTitle = regexIgnore.findall(title)
  return videoTitle

def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    removeTag = TAG_RE.sub('', text)
    pattern = re.compile(r'\s+\t+\n+')
    removeTag = re.sub(pattern, ' ', removeTag)
    return removeTag.rstrip().strip().lstrip()

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def comment_threads_list_by_video_id(client, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.commentThreads().list(
        **kwargs
    ).execute()

    return response

def preview_list(type,key):

    lstVideo = []
    nextPageToken = ''
    number = 0;
    client = get_authenticated_service()

    while nextPageToken is not None:

        if type == "channel_id":
            channel_response = client.search().list(
                channelId=key,
                part='id,snippet',
                order='viewCount',
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        elif type == "channel_name":
            channel_response = client.channels().list(
                forUsername=key,
                part='id,snippet',
                order='viewCount',
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        elif type == "keyword":
            channel_response = client.search().list(
                q=key,
                part='id,snippet',
                order='viewCount',
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        else:
            print("ERROR -- Please Enter argument Channel ID or Search Keyword")

        # print(channel_response)
        if (channel_response['items']):

            if 'nextPageToken' not in channel_response:
                nextPageToken = None
            else:
                nextPageToken = channel_response['nextPageToken']

            for channel_result in channel_response.get('items', []):
            #
                # print(channel_result)
                if (channel_result['id']['kind'] == 'youtube#video'):
                    number += 1
                    # print(number, channel_result['id']['kind'])
                    videoTitle = channel_result['snippet']['title']
                    videoTitle = videoTitle.replace("&quot;", "")
                    videoId = channel_result['id']['videoId']
                    # print(videoTitle)
                    # print(videoId)
                    results_videoList = {
                        'ID': videoId,
                        'message': videoTitle,
                    }
                    lstVideo.append(results_videoList)

    return lstVideo

def youtube_list(type,key,filter,keyword):

    client = get_authenticated_service()
    lstVideo = []
    lstComment = []
    nextPageToken = ''
    number = 0;

    while nextPageToken is not None:
        if type == "channel_id":
            channel_response = client.search().list(
                channelId=key,
                part='id,snippet',
                order='viewCount',
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        elif type == "channel_name":
            channel_response = client.channels().list(
                forUsername=key,
                part='id,snippet',
                order='viewCount',
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        elif type == "keyword":
            channel_response = client.search().list(
                q=key,
                part='id,snippet',
                order='viewCount',
                maxResults=50,
                pageToken=nextPageToken,
            ).execute()
        else:
            print("ERROR -- Please Enter argument Channel ID or Search Keyword")


        # print(json.dumps(channel_response,indent=2))

        if(channel_response['items']):

            if 'nextPageToken' not in channel_response:
                nextPageToken = None
            else:
                nextPageToken = channel_response['nextPageToken']


            for channel_result in channel_response.get('items', []):

                # print(channel_result)
                if(channel_result['id']['kind'] == 'youtube#video'):
                    number += 1
                    videoTitle = channel_result['snippet']['title']
                    videoTitle = videoTitle.replace("&quot;","")
                    regexIgnore = re.compile(pattern=r'(?:'+keyword+')')
                    videoTitle_keyword = regexIgnore.findall(videoTitle)

                    if (filter == "include" and videoTitle_keyword) or (filter == "exclude" and not videoTitle_keyword) :
                        # if 'ทาโร' in videoTitle:
                        videoId = channel_result['id']['videoId']
                        print(videoTitle)
                        # print(videoId)
                        videoList = videos_list_by_id(client,
                                        part='snippet,contentDetails,statistics',
                                        id=videoId,maxResults=50)
                        publishedTime = iso8601.parse_date(channel_result['snippet']['publishedAt'])
                        publishedTime = str(publishedTime)
                        publishedTime = str(datetime.strptime(publishedTime, "%Y-%m-%d %H:%M:%S+00:00"))
                        channelTitle = videoList['items'][0]['snippet']['channelTitle']
                        duration = isodate.parse_duration(videoList['items'][0]['contentDetails']['duration'])

                        snippet = videoList['items'][0]['snippet']
                        if 'tags' in snippet:
                            tags = snippet['tags']
                            tags = '|'.join(tags)
                        else:
                            tags = 'NONE'

                        if 'dislikeCount' in videoList['items'][0]['statistics']:
                            dislikeCount = videoList['items'][0]['statistics']['dislikeCount']
                        else:
                            dislikeCount = 0

                        if 'likeCount' in videoList['items'][0]['statistics']:
                            likeCount = videoList['items'][0]['statistics']['likeCount']
                        else:
                            likeCount = 0

                        if 'commentCount' in videoList['items'][0]['statistics']:
                            commentCount = videoList['items'][0]['statistics']['commentCount']
                        else:
                            commentCount = 0

                        if 'favoriteCount' in videoList['items'][0]['statistics']:
                            favoriteCount = videoList['items'][0]['statistics']['favoriteCount']
                        else:
                            favoriteCount = 0

                        results_json_video = {
                            'ID': videoId,
                            'URL' : 'https://www.youtube.com/watch?v='+videoId,
                            'message': videoTitle,
                            'post_time' : publishedTime,
                            'definition': videoList['items'][0]['contentDetails']['definition'],
                            'duration': duration,
                            'liveBroadcastContent': videoList['items'][0]['snippet']['liveBroadcastContent'],
                            'channel_name': channelTitle,
                            'categoryId': videoList['items'][0]['snippet']['categoryId'],
                            'viewCount': videoList['items'][0]['statistics']['viewCount'],
                            'commentCount': commentCount,
                            'dislikeCount': dislikeCount,
                            'favoriteCount': favoriteCount,
                            'likeCount': likeCount,
                            'tags': tags,
                            'data_from' : 'Youtube',
                            'get_by' : 'Channel'
                        }
                        lstVideo.append(results_json_video)
                        print(commentCount)
                        # if commentCount == '0':
                        #     print("IF")
                        if commentCount != '0':
                            # print("ELSE")
                            commentNextPageToken = ''
                            numberComment = 0
                            while commentNextPageToken is not None:
                                comment = comment_threads_list_by_video_id(client,part='snippet,replies',
                                                                                   videoId=videoId,pageToken=commentNextPageToken)
                                if(comment['items']):

                                    if 'nextPageToken' not in comment:
                                        commentNextPageToken = None
                                    else:
                                        commentNextPageToken = comment['nextPageToken']

                                    for comment_result in comment.get('items',[]):
                                        # print(json.dumps(comment_result,indent=2))
                                        commentText = comment_result['snippet']['topLevelComment']['snippet']['textDisplay']
                                        # commentText_with_KW = regEXComment(commentText)
                                        # if commentText_with_KW:
                                        commentId = comment_result['snippet']['topLevelComment']['id']
                                        numberComment += 1
                                        commentText = remove_tags(str(commentText))
                                        updatedAt = iso8601.parse_date(comment_result['snippet']['topLevelComment']['snippet']['updatedAt'])
                                        updatedAt = str(updatedAt)
                                        updatedAt = str(datetime.strptime(updatedAt, "%Y-%m-%d %H:%M:%S+00:00"))
                                        if(commentText):
                                            results_json = {
                                                'ID': videoId,
                                                'URL': 'https://www.youtube.com/watch?v=' + videoId,
                                                'message':commentText,
                                                'message_id':commentId,
                                                'authorDisplayName': comment_result['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                                'authorChannelUrl': comment_result['snippet']['topLevelComment']['snippet']['authorChannelUrl'],
                                                'likeCount': comment_result['snippet']['topLevelComment']['snippet']['likeCount'],
                                                'comment_time': updatedAt,
                                                'data_from': 'Youtube',
                                                'get_by': 'Channel'
                                            }
                                            lstComment.append(results_json)

                                        else:
                                            break

                                else:
                                    break

        else:
            break
    # print(json.dumps(lstVideo,indent=2))
    # return [channelTitle,lstVideo,typeOption]
    return [channelTitle,lstVideo,lstComment]

def videos_list_by_id(client, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.videos().list(
        **kwargs
    ).execute()

    return response

@app.route('/preview',methods=['POST'])
def preview():
    req_data = request.get_json()
    list = preview_list(req_data['type'],req_data['key'])
    list_json = json.dumps(list)
    return list_json

@app.route('/filter',methods=['POST'])
def filter():
    req_data = request.get_json()
    list = youtube_list(req_data['type'],req_data['key'],req_data['filter'],req_data['keyword'])
    list_json = json.dumps(list)
    return list_json

if __name__ == '__main__':
    app.run(debug=True,port=5000)