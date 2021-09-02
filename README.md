# Twitrends (alpha)

Twitrends is a utility to be used by developers with access to the Twitter Developer Portal.

Twitrends is used for listening to new tweets containing a keyword and pattern. \
The utility will send all new tweets matching the keyword and pattern to an Elasticsearch instance,
and will keep all existing entries updated with the current count of retweets and likes. 

Twitrends does not store the actual tweet content, nor the name of the author or profile. 

## Prerequisites

To use Twitrends, access to the [Twitter Developer Portal](https://developer.twitter.com/en/apply-for-access) with working credentials to the Twitter API is needed. \
Once access and credentials are obtained, the below packages need to be installed. 

Keep in mind, a configured [Elasticsearch](https://www.elastic.co/) instance with https, username and password is required.

[tweepy - twitter python library](https://www.tweepy.org/)
```bash
pip install tweepy
```
[elasticsearch python client](https://pypi.org/project/elasticsearch/)
```bash
pip install elasticsearch
```

## Installation

.deb package installation:

```bash
sudo dpkg -i twitrends_1.0.0-2_all.deb
```
.rpm package installation:

```bash
sudo rpm -i twitrends_1.0.0-2_all.deb
```

## Usage
Open /usr/local/bin/Twitrends/twitrends/trends_settings.json
and add your configuration. Here's an example configuration:

```json
{
   "elastic":{
      "username":"asdf",
      "password":"fdsa",
      "ip":"127.0.0.1",
      "port":"9200"
   },
   "auth_handle_creds":{
      "consumer_key":"asdf1234569ads9as99ds9dds99ad",
      "consumer_secret":"asdf1234569ads9as99ds9dds99ad"
   },
   "access_token":{
      "key":"asdf1234569ads9as99ds9dds99ad",
      "secret":"asdf1234569ads9as99ds9dds99ad"
   },
   "search_keyword":"icecream",
   "search_pattern":"icecream"
}
```
Note: The credentials are for example use and will not work. 
Only official credentials from the Twitter Developer Portal will be accepted.

Once the configuration is done, enable and start the service:
```bash
sudo systemctl enable twitrends.service
sudo systemctl start twitrends.service
```
Done!

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
