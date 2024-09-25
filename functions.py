import sys
sys.dont_write_bytecode = True

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from typing import List, Dict, Optional, Union
from dicttoxml import dicttoxml as convertToXML
import csv

class Video:
    def __init__(self, id: str) -> None:
        if len(id.strip()) != 11:
            raise ValueError("Video id must be 11 characters in length")
        self.id: str = id.strip()
        self.transcription: Optional[Union[Dict[str, str, str], str]]

    def transcribe(self, fileFormat: Optional[str] = "JSON", justText: Optional[bool] = False):
        if not self.id:
            print("Video id not provided, must be 11 characters in length")
            exit()
        
        if fileFormat not in ["CSV", "JSON", "TXT", "XML"]:
            print("Invalid fileFormat received.  Expected CSV, JSON, TXT, or XML")
            exit()
        
        if justText and fileFormat in ["CSV", "XML"]:
            justText = False

        elif not justText and fileFormat == "TXT":
            justText = True

        try:
            transcription: Dict[str, str, str] = YouTubeTranscriptApi.get_transcript(self.id)
            if justText:
                try:
                    text = ""
                    for item in transcription:
                        text += item["text"].replace("[\xa0__\xa0]", "EXPLETIVE").replace("[�__�]", "EXPLETIVE") + " "

                    self.transcription = text

                except:
                    print("There was an error while transcribing the text from the provided video ID, please check your connection and try again, if this issue persists please try a without justText!")
                    exit()

            else:
                self.transcription = transcription

        except:
            transcription = None
            print("There was an error while transcribing the provided video ID, please check your connection and try again, if this issue persists please try a different video!")
            exit()


        if self.transcription and fileFormat == "JSON":
            with open(f'{self.id}.json', 'w', encoding='utf-8') as json_file:
                if justText:
                    try:
                        json_file.write(str({"text": self.transcription}).replace("'text'", '"text"'))
                    except:
                        print("There was an error while transcribing the text from the provided video ID, please check your connection and try again, if this issue persists please try a without justText!")
                        exit()
                else:
                    try:
                        json_formatted = JSONFormatter().format_transcript(self.transcription, indent=2)
                        json_file.write(json_formatted)
                    except:
                        print("There was an error while transcribing the provided video ID, please check your connection and try again, if this issue persists please try a different video!")
                        exit()

        elif self.transcription and fileFormat == "XML":
            try:
                xml = convertToXML(self.transcription)
            except:
                xml = None
                
            if xml and isinstance(xml, bytes):
                with open(f'{self.id}.xml', 'wb') as xml_file:
                    try:
                        xml_file.write(xml)
                    except:
                        print("There was an error while writing the transcription for the provided video ID, please check your connection and try again, if this issue persists please try a different format!")
                        exit()

            elif xml and isinstance(xml, str):
                with open(f'{self.id}.xml', 'w', encoding='utf-8') as xml_file:
                    try:
                        xml_file.write(xml)
                    except:
                        print("There was an error while writing the transcription for the provided video ID, please check your connection and try again, if this issue persists please try a different format!")
                        exit()
            else:
                print("There was an error while transcribing the provided video ID, please check your connection and try again, if this issue persists please try a different video!")
                exit()
        
        elif self.transcription and fileFormat == "CSV":
            with open(f'{self.id}.csv', "w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, ["text", "start", "duration"])
                writer.writeheader()
                for row in self.transcription:
                    writer.writerow(row)

        elif self.transcription and fileFormat == "TXT":
            with open(f'{self.id}.txt', "w", newline="") as txt_file:
                txt_file.write(self.transcription)
        
        else:
            print("There was an error while transcribing the provided video ID, please check your connection and try again, if this issue persists please try a different video!")
            exit()
