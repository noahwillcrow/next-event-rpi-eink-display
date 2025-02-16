import os
import yaml
from artist import Artist
from data_fetcher import DataFetcher
from renderer import Renderer

last_update_file_path = './last_update_data.gitignored.txt'


def main():
    config = load_config_yaml('../config.yaml')

    # fetch the upcoming events
    data_fetcher = DataFetcher(config)
    next_event = data_fetcher.fetch_next_event()

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
        should_flip=config['image']['should-flip'],
    )
    image = None
    if next_event is None:
        if did_last_update_have_event():
            image = artist.draw_text(config['image']['no-events-message'])
    else:
        image = artist.draw_upcoming_event_notice(
            next_event.name, next_event.time_until_event
        )

    # render the image
    if image is not None:
        renderer = Renderer(config['renderer'])
        renderer.render(image)

    # save whether the last update had an event
    set_did_last_update_have_event(next_event is not None)


def did_last_update_have_event() -> bool:
    """This function reads from a local file to see if the last update had an event."""
    if not os.path.exists(last_update_file_path):
        return True  # if the file doesn't exist, we assume that the last update had an event

    with open(last_update_file_path, 'r') as file:
        return str.lower(file.read()) == 'true'


def load_config_yaml(config_path) -> dict:
    """This function reads the config yaml file and returns the content as a dictionary."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def set_did_last_update_have_event(value: bool):
    """This function writes whether the most recent update had an event to disk."""
    with open(last_update_file_path, 'w') as file:
        file.write(str(value))


if __name__ == '__main__':
    main()
