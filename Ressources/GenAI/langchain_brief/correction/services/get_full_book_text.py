import requests
import re


async def get_text_by_id(book_id):


    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"

    try:
        response = requests.get(url, timeout=10)

        response.raise_for_status()

        text = response.text


        pattern = r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*\s+"

        # Use re.split() to split the text and only keep the part after the marker
        split_text = re.split(pattern, text, maxsplit=1)

        if len(split_text) > 1:
            main_content = split_text[1]
            return main_content
        else:
            print("Regex marker not found, sending whole text")
            return text



    except Exception as e:
        print(e)
        return None
