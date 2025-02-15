from data_fetcher import DataFetcher


def main():
    data_fetcher = DataFetcher('../config.yaml')
    events = data_fetcher.fetch_upcoming_events()
    for event in events:
        print(event)


if __name__ == '__main__':
    main()
