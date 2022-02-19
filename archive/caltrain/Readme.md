A command line twitter client with more focus on caltrain.

Command line Arguments
- Twitter consumer key, secret and access token, access token secert should be passed as arguments to the python script.
- user account : defaults to [Caltrain](https://twitter.com/Caltrain)
- Caltrain only tweets filter : whether or not to show tweets not relavent about caltrain

I have the below bash function which calls python script
```bash
caltrain ()
{
    python3 /Users/stps/code/MiniProjects/caltrain/get_caltrain_tweets.py -ck consumer_key -cs consumer_secret -at access_token -ats access_token_secret "$@"
}
```
Example usage
- `caltrain` : show [Caltrain](https://twitter.com/Caltrain)'s tweets about caltrain 
- `caltrain -u yesteapea` : show [yesteapea](https://twitter.com/yesteapea)'s tweets about caltrain 
- `caltrain -u yesteapea -a` : show tweets by [yesteapea](https://twitter.com/yesteapea) 

For demo check this [asciinema](https://asciinema.org/a/0pofsz9luuep2edkqrobfasjr) 
