import toml
from item import Item
from item import Umthes

config = toml.load('.streamlit/config.toml')
primary_color = config['theme']['primaryColor']
primary_button = config['theme']['primaryButton']


def flatten_item(item: Item) -> dict:
    item['description'] = item['description'] if item['description'] else ''
    return item


def prepare_tags(tags) -> str:
    tags_html = "<div>"
    if tags is not None:
        for tag_raw in tags:
            tag = tag_raw['label']
            tags_html += f'<span class="tag">{tag}</span>'
        tags_html += "</div>"
    return tags_html


def print_data(recommendation) -> str:
    html_data = (f'<div class="rec" id="scrollableContent">'
                 f'<p class="title">{recommendation["title"]}</p>'
                 f'<a href="{recommendation["source_url"]}">Link zur Quelle</a>'
                 f'<p>{recommendation["description"]}</p>'
                 f'{prepare_tags(recommendation["umthes"])}'
                 f'</div>')
    return html_data


def process_item(json_obj) -> Item:
    print(json_obj)
    item_data = {
        "id": json_obj['id'],
        "title": json_obj['title'],
    }

    if 'tags_json' in json_obj and json_obj['tags_json']:
        umthes_list = [Umthes(**tag['Umthes']) for tag in json_obj['tags_json']['json'] if 'Umthes' in tag]
        item_data['umthes'] = umthes_list

    if 'source_url' in json_obj:
        item_data['source_url'] = json_obj['source_url']

    return item_data





