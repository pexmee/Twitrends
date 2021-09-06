# Twitrends (alpha)

Twitrends is a utility to be used by developers with access to the Twitter Developer Portal.

Twitrends is used for listening to new tweets containing a keyword and pattern. \
The utility will send all new tweets matching a keyword and pattern to an Elasticsearch instance,
and will keep all existing entries updated with the current count of retweets and likes. 

Twitrends does not store the actual tweet content, nor the name of the author or profile. 

## Development

Currently in development. Please refer to the issues to see a little bit about what is going to be added in the future. 

## Prerequisites

To use Twitrends, access to the [Twitter Developer Portal](https://developer.twitter.com/en/apply-for-access) with working credentials to the Twitter API is needed. \
Once access and credentials are obtained, the below packages need to be installed. 

Keep in mind, a configured [Elasticsearch](https://www.elastic.co/) instance with https, username and password is required.

[tweepy](https://www.tweepy.org/) - Twitter python library
```bash
pip install tweepy
```
[elasticsearch](https://pypi.org/project/elasticsearch/) - Elasticsearch python client
```bash
pip install elasticsearch
```
[urllib3](https://pypi.org/project/urllib3/) - HTTP library
```bash
pip install urllib3
```

<!-- ## Installation -->

## NOTE: <br>Right now the .deb and .rpm packages are outdated. <br> Please clone repo and set up manually - fix for this is coming soon  

<!-- .deb package installation:

```bash
sudo dpkg -i twitrends_1.0.0-2_all.deb
```
.rpm package installation:

```bash
sudo rpm -i twitrends_1.0.0-1_all.rpm
``` -->
<br>

## Usage
Open trends_settings.json
and add your configuration. Here's an example configuration:

```json
{
    "elastic": {
        "username": "example",
        "password": "example",
        "ip": "127.0.0.1",
        "port": "9200"
    },
    "auth_handle_creds": {
        "consumer_key": "aafdsfasdddafldsfdlsfdfd",
        "consumer_secret": "aafdsfasdddafldsfdlsfdfd"
    },
    "access_token": {
        "key": "aafdsfasdddafldsfdlsfdfd",
        "secret": "aafdsfasdddafldsfdlsfdfd"
    },
    "search_rules": {
       "example1" : {
          "search_keyword" : "example1",
	      "search_pattern" : "\\s+example1\\s+",
	      "make_link" : true	  
       },
       "example2" : {
	      "search_keyword" : "example2",
	      "search_pattern" : "\\s+example2\\s+",
	      "make_link" : false
       }
    }
}
```
Note: The credentials are for example use and will not work. 
Only official credentials from the Twitter Developer Portal will be accepted.

Once the configuration is done, [manually add the service](https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6), enable and start the service: <br> Note: this will be fixed once .rpm & .deb packages are updated.
```bash
sudo systemctl enable twitrends.service
sudo systemctl start twitrends.service
```
Done!

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
