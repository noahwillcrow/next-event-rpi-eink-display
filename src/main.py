import os
import yaml
from artist import Artist
from data_fetcher import DataFetcher
from renderer import Renderer


def main():
    config = load_config_yaml('../config.yaml')

    # fetch the upcoming events
    data_fetcher = DataFetcher(config)
    next_event = data_fetcher.fetch_upcoming_events()

    # draw the image
    path_to_font = os.path.join(
        os.path.dirname(__file__), '..', config['image']['font']['path']
    )
    artist = Artist(
        height=int(config['image']['height']),
        width=int(config['image']['width']),
        padding=int(config['image']['padding']),
        path_to_font=path_to_font,
        big_text_size=int(config['image']['font']['big-text-size']),
        small_text_size=int(config['image']['font']['small-text-size']),
    )
    if next_event is None:
        image = artist.draw_nothing_coming_up()
    else:
        image = artist.draw_upcoming_event_notice(
            next_event.name, next_event.time_until_event
        )

    # render the image
    renderer = Renderer(config['renderer'])
    renderer.render(image)


def load_config_yaml(config_path) -> dict:
    """This function reads the config yaml file and returns the content as a dictionary."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


if __name__ == '__main__':
    main()
